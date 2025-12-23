from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional

from src.services.ollama_service import ollama_service
from .models import KnowledgeEntry
from src.modules.dtic.tickets.models import Ticket

class KnowledgeService:
    
    async def learn_ticket(self, db: Session, ticket_id: int) -> KnowledgeEntry:
        """
        Learns from a ticket by creating an embedding of its content.
        """
        # 1. Fetch ticket (By GLPI ID, not internal ID)
        ticket = db.query(Ticket).filter(Ticket.glpi_id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # 2. Prepare content string
        # Combine title, description and solution (if we had a solution field, assuming description for now)
        ticket_text = f"Título: {ticket.titulo}\nDescrição: {ticket.descricao}"
        
        # 3. Generate embedding
        embedding = await ollama_service.get_embedding(ticket_text)
        
        # 4. Save or Update Entry
        # Fix: Use ticket.id (internal ID) not ticket_id (GLPI ID) for the FK check
        entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.ticket_id == ticket.id).first()
        
        if not entry:
            entry = KnowledgeEntry(
                ticket_id=ticket.id,
                content=ticket_text,
                embedding=embedding,
                metadata_json={
                    "glpi_id": ticket.glpi_id,
                    "status_id": ticket.status_id,
                    "title": ticket.titulo
                }
            )
            db.add(entry)
        else:
            entry.content = ticket_text
            entry.embedding = embedding
            entry.metadata_json = {
                "glpi_id": ticket.glpi_id,
                "status_id": ticket.status_id,
                "title": ticket.titulo
            }
        
        db.commit()
        db.refresh(entry)
        return entry

    def learn_ticket_sync(self, db: Session, ticket_id: int, commit: bool = True) -> Optional[KnowledgeEntry]:
        """
        Learns from a ticket (Synchronous).
        Safe for use inside SyncService loop.
        """
        try:
            # 1. Fetch ticket (By GLPI ID)
            ticket = db.query(Ticket).filter(Ticket.glpi_id == ticket_id).first()
            if not ticket:
                # If called inside sync loop before commit, it might be in session.new but not queryable if not flushed?
                # But SyncService usually flushes or query finds it in identity map.
                return None

            # 2. Text
            ticket_text = f"Título: {ticket.titulo}\nDescrição: {ticket.descricao}"
            
            # Check if entry exists and content is identical
            entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.ticket_id == ticket.id).first()
            if entry and entry.content == ticket_text:
                # Optimized: Content hasn't changed, skip embedding generation
                return entry

            # 3. Embedding (Sync)
            embedding = ollama_service.get_embedding_sync(ticket_text)
            
            # 4. Save/Update
            if not entry:
                entry = KnowledgeEntry(
                    ticket_id=ticket.id,
                    content=ticket_text,
                    embedding=embedding,
                    metadata_json={
                        "glpi_id": ticket.glpi_id,
                        "status_id": ticket.status_id,
                        "title": ticket.titulo
                    }
                )
                db.add(entry)
            else:
                entry.content = ticket_text
                entry.embedding = embedding
                entry.metadata_json = {
                    "glpi_id": ticket.glpi_id,
                    "status_id": ticket.status_id,
                    "title": ticket.titulo
                }
            
            if commit:
                db.commit()
                db.refresh(entry)
            else:
                db.flush() # Ensure ID is generated/linked but don't commit transaction
                
            return entry
        except Exception as e:
            # Log but don't crash the sync process
            print(f"   ⚠️ RAG Learn Error (Ticket {ticket_id}): {e}")
            return None

    async def search(self, db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for similar tickets.
        """
        # 1. Embed query
        query_embedding = await ollama_service.get_embedding(query)
        
        # 2. Search using pgvector L2 distance operator (<->)
        # Note: We use raw SQL for the vector operator usually, or specific SQLAlchemy syntax if type is bound correctly.
        # Here we will use text() for simplicity and robustness with the custom type.
        
        # Format vector as string for the query
        vec_str = str(query_embedding)
        
        sql = text("""
            SELECT id, ticket_id, content, metadata_json, 
                   embedding <-> :query_vec as distance
            FROM dtic.knowledge_entries
            ORDER BY distance ASC
            LIMIT :limit
        """)
        
        results = db.execute(sql, {"query_vec": vec_str, "limit": limit}).fetchall()
        
        return [
            {
                "ticket_id": r.ticket_id,
                "content": r.content,
                "metadata": r.metadata_json,
                "distance": float(r.distance)
            }
            for r in results
        ]

service = KnowledgeService()
