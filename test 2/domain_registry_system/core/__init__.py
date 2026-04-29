"""
Модуль core содержит основные классы системы управления доменами.
"""

from .domain import Domain
from .events import DomainEvent, EventType
from .observer import DomainObserver, FilteredDomainObserver
from .registry import DomainRegistry

__all__ = [
    'Domain',
    'DomainEvent',
    'EventType',
    'DomainObserver',
    'FilteredDomainObserver',
    'DomainRegistry',
]
