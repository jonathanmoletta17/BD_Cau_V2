"""
GLPI Data Service V3 - DTIC Tickets Module
"""
from .models import Ticket, TicketUser, TicketGroup, TicketChange

__all__ = ["Ticket", "TicketUser", "TicketGroup", "TicketChange"]
