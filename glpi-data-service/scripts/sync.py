"""
Unified Sync CLI Script
Orchestrates synchronization for specified contexts.

Usage:
  python scripts/sync.py [--context <dtic|sis|all>] [--type <metadata|tickets|all>]
"""
import sys
import argparse
import logging
import concurrent.futures
import uuid
import json
import contextvars
from pathlib import Path
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Config, Database
from src.core.glpi_client import GLPIClient
from src.core.models import SyncState, OrphanChange  # ✅ Import SyncState & OrphanChange
from src.services.sync import SyncService
from src.services.sync.changes import reprocess_orphan_changes

# Import Models dynamically
import src.modules.dtic.metadata as dtic_meta
import src.modules.dtic.tickets as dtic_tickets
import src.modules.sis.metadata as sis_meta
import src.modules.sis.tickets as sis_tickets
import src.modules.sis.carregadores.models as sis_carregadores

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SYNC - %(levelname)s - %(correlation_id)s - %(message)s'
)
correlation_id_ctx = contextvars.ContextVar('correlation_id', default='-')


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get()
        return True


_root_logger = logging.getLogger()
for _handler in _root_logger.handlers:
    _handler.addFilter(CorrelationIdFilter())
logger = logging.getLogger(__name__)


def get_models(context):
    """Return model classes for a context."""
    if context == 'dtic':
        return {
            'User': dtic_meta.User,
            'Group': dtic_meta.Group,
            'Entity': dtic_meta.Entity,
            'Location': dtic_meta.Location,
            'Category': dtic_meta.ITILCategory,
            'Profile': dtic_meta.Profile,
            'GroupUser': dtic_meta.GroupUser,
            'ProfileUser': dtic_meta.ProfileUser,
            'OrphanChange': OrphanChange,
            'Ticket': dtic_tickets.Ticket,
            'TicketUser': dtic_tickets.TicketUser,
            'TicketGroup': dtic_tickets.TicketGroup,
            'TicketChange': dtic_tickets.TicketChange
            # DTIC doesn't have TicketItem usage yet
        }
    elif context == 'sis':
        return {
            'User': sis_meta.User,
            'Group': sis_meta.Group,
            'Entity': sis_meta.Entity,
            'Location': sis_meta.Location,
            'Category': sis_meta.ITILCategory,
            'Profile': sis_meta.Profile,
            'GroupUser': sis_meta.GroupUser,
            'ProfileUser': sis_meta.ProfileUser,
            'Ticket': sis_tickets.Ticket,
            'TicketUser': sis_tickets.TicketUser,
            'TicketGroup': sis_tickets.TicketGroup,
            'TicketChange': sis_tickets.TicketChange,
            'TicketItem': sis_tickets.TicketItem,
            'Carregador': sis_carregadores.Carregador
        }
    return None

def _state_key(entity_type: str, phase: str = None):
    if phase:
        return f"{entity_type}:{phase}"
    return entity_type


def _get_sync_state(session, context: str, entity_type: str, phase: str = None):
    key = _state_key(entity_type, phase)
    state = session.query(SyncState).filter_by(context=context, entity_type=key).first()
    if state or not phase:
        return state
    return session.query(SyncState).filter_by(context=context, entity_type=entity_type).first()

def _get_since_date(state):
    if state and state.last_sync:
        return state.last_sync - timedelta(hours=1)
    return None

def _update_sync_state(session, context: str, entity_type: str, new_time, phase: str = None):
    if not new_time:
        return
    
    # Ensure new_time is aware (UTC) if it's naive, to match DB
    if new_time.tzinfo is None:
        from datetime import timezone
        new_time = new_time.replace(tzinfo=timezone.utc)

    key = _state_key(entity_type, phase)
    state = session.query(SyncState).filter_by(context=context, entity_type=key).first()
    if not state:
        state = SyncState(context=context, entity_type=key)
        session.add(state)
    
    # Ensure state.last_sync is compared correctly
    current_sync = state.last_sync
    if current_sync and current_sync.tzinfo is None:
         from datetime import timezone
         current_sync = current_sync.replace(tzinfo=timezone.utc)

    if not current_sync or new_time > current_sync:
        state.last_sync = new_time
    
    if phase:
        legacy = session.query(SyncState).filter_by(context=context, entity_type=entity_type).first()
        if legacy:
            leg_sync = legacy.last_sync
            if leg_sync and leg_sync.tzinfo is None:
                from datetime import timezone
                leg_sync = leg_sync.replace(tzinfo=timezone.utc)
            
            if not leg_sync or new_time > leg_sync:
                legacy.last_sync = new_time
    session.commit()


def _log_event(level, event, **fields):
    payload = {"event": event}
    payload.update(fields)
    logger.log(level, json.dumps(payload, ensure_ascii=False))


def _log_sync_error(error_type: str, context: str, phase: str, error: Exception):
    _log_event(
        logging.ERROR,
        "sync_error",
        error_type=error_type,
        context=context,
        phase=phase,
        message=str(error)
    )


def run_sync(context, sync_type, limit=None, incremental=False):
    """
    Executa o ciclo de sync com checkpoint por fase e cursor por date_mod.
    Atualiza checkpoints apenas após sucesso de cada fase.
    """
    correlation_id = uuid.uuid4().hex
    token = correlation_id_ctx.set(correlation_id)
    start_time = datetime.utcnow()
    _log_event(
        logging.INFO,
        "sync_start",
        correlation_id=correlation_id,
        context=context,
        sync_type=sync_type,
        incremental=incremental,
        limit=limit
    )
    print("\n" + "=" * 60)
    print(f"[START] SYNC: Context={context.upper()}, Type={sync_type.upper()}{f', Limit={limit}' if limit else ''}{', INCREMENTAL' if incremental else ''}")
    print("=" * 60)

    models = get_models(context)
    if not models:
        logger.error(f"Unknown context: {context}")
        correlation_id_ctx.reset(token)
        return

    url = Config.get_glpi_url(context)
    app_token = Config.get_glpi_app_token(context)
    user_token = Config.get_glpi_user_token(context)

    if not url:
        logger.error(f"Configuration missing for {context} (URL not set)")
        correlation_id_ctx.reset(token)
        return

    session = None
    try:
        session = Database.get_session(context=context)
        with GLPIClient(url, app_token, user_token) as client:
            if sync_type in ['all', 'metadata']:
                try:
                    st_entity = _get_sync_state(session, context, 'Entity', phase='metadata') if incremental else None
                    st_location = _get_sync_state(session, context, 'Location', phase='metadata') if incremental else None
                    st_group = _get_sync_state(session, context, 'Group', phase='metadata') if incremental else None
                    st_user = _get_sync_state(session, context, 'User', phase='metadata') if incremental else None
                    st_category = _get_sync_state(session, context, 'Category', phase='metadata') if incremental else None
                    st_profile = _get_sync_state(session, context, 'Profile', phase='metadata') if incremental else None
                    st_group_user = _get_sync_state(session, context, 'GroupUser', phase='metadata') if incremental else None
                    st_profile_user = _get_sync_state(session, context, 'ProfileUser', phase='metadata') if incremental else None

                    max_entity_date = SyncService.sync_entities(client, session, models['Entity'], since_date=_get_since_date(st_entity))
                    max_location_date = SyncService.sync_locations(client, session, models['Location'], since_date=_get_since_date(st_location))
                    max_group_date = SyncService.sync_groups(client, session, models['Group'], since_date=_get_since_date(st_group))
                    max_user_date = SyncService.sync_users(client, session, models['User'], since_date=_get_since_date(st_user))
                    max_category_date = SyncService.sync_categories(client, session, models['Category'], since_date=_get_since_date(st_category))
                    max_profile_date = SyncService.sync_profiles(client, session, models['Profile'], since_date=_get_since_date(st_profile))

                    if context == 'sis' and 'Carregador' in models:
                        SyncService.sync_carregadores(client, session, models['Carregador'])

                    logger.info("   [LOAD] Loading IDs for FK validation...")
                    valid_ids = {
                        'users': set(r.id for r in session.query(models['User'].id).all()),
                        'groups': set(r.id for r in session.query(models['Group'].id).all()),
                        'profiles': set(r.id for r in session.query(models['Profile'].id).all()),
                        'entities': set(r.id for r in session.query(models['Entity'].id).all())
                    }

                    max_group_user_date = SyncService.sync_groups_users(client, session, models['GroupUser'], valid_ids, since_date=_get_since_date(st_group_user))
                    max_profile_user_date = SyncService.sync_profiles_users(client, session, models['ProfileUser'], valid_ids, since_date=_get_since_date(st_profile_user))

                    if incremental and not limit:
                        _update_sync_state(session, context, 'Entity', max_entity_date, phase='metadata')
                        _update_sync_state(session, context, 'Location', max_location_date, phase='metadata')
                        _update_sync_state(session, context, 'Group', max_group_date, phase='metadata')
                        _update_sync_state(session, context, 'User', max_user_date, phase='metadata')
                        _update_sync_state(session, context, 'Category', max_category_date, phase='metadata')
                        _update_sync_state(session, context, 'Profile', max_profile_date, phase='metadata')
                        _update_sync_state(session, context, 'GroupUser', max_group_user_date, phase='metadata')
                        _update_sync_state(session, context, 'ProfileUser', max_profile_user_date, phase='metadata')
                except RequestException as e:
                    session.rollback()
                    _log_sync_error("glpi", context, "metadata", e)
                    raise
                except SQLAlchemyError as e:
                    session.rollback()
                    _log_sync_error("db", context, "metadata", e)
                    raise
                except (ValueError, KeyError) as e:
                    session.rollback()
                    _log_sync_error("validation", context, "metadata", e)
                    raise

            if sync_type in ['all', 'tickets']:
                valid_ids = {
                    'users': set(r.id for r in session.query(models['User'].id).all()),
                    'groups': set(r.id for r in session.query(models['Group'].id).all()),
                    'entities': set(r.id for r in session.query(models['Entity'].id).all()),
                    'locations': set(r.id for r in session.query(models['Location'].id).all()),
                    'categories': set(r.id for r in session.query(models['Category'].id).all()),
                }

                since_ticket = None
                since_changes = None

                if incremental:
                    st_ticket = _get_sync_state(session, context, 'Ticket', phase='tickets')
                    st_changes = _get_sync_state(session, context, 'TicketChange', phase='changes')

                    if st_ticket and st_ticket.last_sync:
                        since_ticket = _get_since_date(st_ticket)
                        logger.info(f"   Incremental Ticket: Since {st_ticket.last_sync} (Lookback: {since_ticket})")
                    if st_changes and st_changes.last_sync:
                        since_changes = _get_since_date(st_changes)
                        logger.info(f"   Incremental Changes: Since {st_changes.last_sync} (Lookback: {since_changes})")

                try:
                    max_ticket_date = SyncService.sync_tickets(client, session, models, valid_ids, context, limit, since_date=since_ticket)
                    if incremental and not limit and max_ticket_date:
                        _update_sync_state(session, context, 'Ticket', max_ticket_date, phase='tickets')
                    elif incremental and limit:
                        logger.warning("   Incremental Sync with LIMIT: State NOT updated.")
                except RequestException as e:
                    session.rollback()
                    _log_sync_error("glpi", context, "tickets", e)
                    raise
                except SQLAlchemyError as e:
                    session.rollback()
                    _log_sync_error("db", context, "tickets", e)
                    raise
                except (ValueError, KeyError) as e:
                    session.rollback()
                    _log_sync_error("validation", context, "tickets", e)
                    raise

                # === PHASE 1 FIX (ADR-001) ===
                # Trade-off: Sacrifice performance for immediate consistency
                # Always sync actors to fix NULL requester/technician/group
                import time
                actor_sync_start = time.time()
                
                SyncService.sync_ticket_actors(client, session, models, valid_ids, limit)
                
                actor_sync_duration = time.time() - actor_sync_start
                logger.info(f"   ✅ Actor Sync completed in {actor_sync_duration:.2f}s")


                try:
                    logger.info("   [DEMO] Skipping Ticket Changes to unblock Real-Time Ticket Sync")
                    # max_changes_date = SyncService.sync_ticket_changes(client, session, models, valid_ids, limit, since_date=since_changes)
                    # if incremental and not limit and max_changes_date:
                    #     _update_sync_state(session, context, 'TicketChange', max_changes_date, phase='changes')
                    # elif incremental and limit:
                    #     logger.warning("   Incremental Sync with LIMIT: State NOT updated.")
                except RequestException as e:
                    session.rollback()
                    _log_sync_error("glpi", context, "changes", e)
                    raise
                except SQLAlchemyError as e:
                    session.rollback()
                    _log_sync_error("db", context, "changes", e)
                    raise
                except (ValueError, KeyError) as e:
                    session.rollback()
                    _log_sync_error("validation", context, "changes", e)
                    raise

                if 'TicketItem' in models:
                    SyncService.sync_ticket_items(client, session, models, valid_ids, limit)

                orphan_metrics = reprocess_orphan_changes(session, models, context, limit=500, base_backoff_minutes=5)
                _log_event(
                    logging.INFO,
                    "orphan_metrics",
                    context=context,
                    processed=orphan_metrics.get("processed"),
                    skipped=orphan_metrics.get("skipped"),
                    remaining=orphan_metrics.get("remaining")
                )
    except RequestException as e:
        _log_sync_error("glpi", context, "global", e)
    except SQLAlchemyError as e:
        _log_sync_error("db", context, "global", e)
    except (ValueError, KeyError) as e:
        _log_sync_error("validation", context, "global", e)
    except Exception as e:
        _log_sync_error("unknown", context, "global", e)
    finally:
        if session:
            # === PHASE 1 METRICS (ADR-001) ===
            # Calculate consistency metrics for observability
            try:
                TicketModel = models.get('Ticket')
                TicketUser = models.get('TicketUser')
                
                if TicketModel and TicketUser:
                    total_tickets = session.query(TicketModel).filter_by(is_deleted=False).count()
                    tickets_with_requester = session.query(TicketModel.id).join(
                        TicketUser, TicketUser.ticket_id == TicketModel.id
                    ).filter(
                        TicketModel.is_deleted == False,
                        TicketUser.type == 1  # Requester
                    ).distinct().count()
                    
                    if total_tickets > 0:
                        consistency_pct = (tickets_with_requester / total_tickets) * 100
                        tickets_without_requester = total_tickets - tickets_with_requester
                        
                        logger.info(f"   📊 Consistency Metrics:")
                        logger.info(f"      Total Tickets: {total_tickets}")
                        logger.info(f"      With Requester: {tickets_with_requester} ({consistency_pct:.2f}%)")
                        logger.info(f"      Without Requester: {tickets_without_requester} ({100-consistency_pct:.2f}%)")
                        
                        _log_event(
                            logging.INFO,
                            "consistency_metrics",
                            context=context,
                            total_tickets=total_tickets,
                            tickets_with_requester=tickets_with_requester,
                            consistency_pct=round(consistency_pct, 2)
                        )
            except Exception as metric_error:
                logger.warning(f"   ⚠️ Failed to calculate metrics: {metric_error}")
            
            session.close()
        duration = (datetime.utcnow() - start_time).total_seconds()
        _log_event(
            logging.INFO,
            "sync_end",
            correlation_id=correlation_id,
            context=context,
            duration_s=round(duration, 2)
        )
        correlation_id_ctx.reset(token)

    print(f"\n[OK] SYNC COMPLETE for {context.upper()}")


def main():
    parser = argparse.ArgumentParser(description='GLPI Sync Tool')
    parser.add_argument('--context', choices=['dtic', 'sis', 'all'], default='all')
    parser.add_argument('--type', choices=['metadata', 'tickets', 'all'], default='all')
    parser.add_argument('--limit', type=int, help='Limit number of tickets/changes for testing', default=None)
    parser.add_argument('--incremental', action='store_true', help='Perform incremental sync based on last run')
    
    args = parser.parse_args()
    
    contexts = ['dtic', 'sis'] if args.context == 'all' else [args.context]
    
    start_time = datetime.now()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(contexts)) as executor:
        future_to_ctx = {
            executor.submit(run_sync, ctx, args.type, args.limit, args.incremental): ctx 
            for ctx in contexts
        }
        
        for future in concurrent.futures.as_completed(future_to_ctx):
            ctx = future_to_ctx[future]
            try:
                future.result()
            except Exception as exc:
                logger.error(f"❌ Context {ctx.upper()} generated an exception: {exc}")

        
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"[DONE] ALL TASKS COMPLETED (Parallel) in {duration:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
