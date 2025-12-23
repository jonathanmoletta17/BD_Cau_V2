def get_ticket_history(
    db: Session,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
) -> List[dict]:
    """
    Get daily ticket history (created and resolved) for the date range.
    Returns list of {date: 'DD/MM', created: int, resolved: int}
    """
    inicio_dt = _parse_date(inicio)
    fim_dt = _parse_date(fim)
    
    # Query for tickets created per day
    created_query = db.query(
        func.date(Ticket.criado_em).label('dia'),
        func.count(Ticket.id).label('criados')
    ).filter(Ticket.is_deleted == False)
    
    if inicio_dt:
        created_query = created_query.filter(Ticket.criado_em >= inicio_dt)
    if fim_dt:
        created_query = created_query.filter(Ticket.criado_em <= fim_dt)
    
    created_results = created_query.group_by(func.date(Ticket.criado_em)).all()
    
    # Query for tickets resolved per day (status 5=Resolvido or 6=Fechado)
    resolved_query = db.query(
        func.date(Ticket.data_resolucao).label('dia'),
        func.count(Ticket.id).label('resolvidos')
    ).filter(
        Ticket.is_deleted == False,
        Ticket.data_resolucao.isnot(None),
        Ticket.status_id.in_([5, 6])  # Resolvido ou Fechado
    )
    
    if inicio_dt:
        resolved_query = resolved_query.filter(Ticket.data_resolucao >= inicio_dt)
    if fim_dt:
        resolved_query = resolved_query.filter(Ticket.data_resolucao <= fim_dt)
    
    resolved_results = resolved_query.group_by(func.date(Ticket.data_resolucao)).all()
    
    # Combine results into a dict by date
    daily_stats = {}
    
    for row in created_results:
        date_str = row.dia.strftime('%d/%m') if row.dia else 'N/A'
        daily_stats[date_str] = {'date': date_str, 'created': row.criados, 'resolved': 0}
    
    for row in resolved_results:
        date_str = row.dia.strftime('%d/%m') if row.dia else 'N/A'
        if date_str in daily_stats:
            daily_stats[date_str]['resolved'] = row.resolvidos
        else:
            daily_stats[date_str] = {'date': date_str, 'created': 0, 'resolved': row.resolvidos}
    
    # Sort by date and return as list
    sorted_results = sorted(daily_stats.values(), key=lambda x: x['date'])
    
    return sorted_results
