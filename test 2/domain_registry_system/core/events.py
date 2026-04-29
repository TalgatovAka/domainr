"""
Модуль для определения типов доменных событий (Domain Events).
Содержит классы, представляющие различные события в системе управления доменами.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


class EventType(Enum):
    """Типы событий, которые могут происходить в реестре доменов."""
    DOMAIN_REGISTERED = "domain_registered"
    DOMAIN_DNS_UPDATED = "domain_dns_updated"
    DOMAIN_DELETED = "domain_deleted"


@dataclass
class DomainEvent:
    """
    Базовый класс для события о домене.
    Содержит общую информацию о произошедшем событии.
    """
    event_type: EventType
    domain_name: str
    owner_email: str
    timestamp: datetime
    dns_servers: Optional[List[str]] = None
    
    def __str__(self) -> str:
        return (
            f"Event: {self.event_type.value} | "
            f"Domain: {self.domain_name} | "
            f"Owner: {self.owner_email} | "
            f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
