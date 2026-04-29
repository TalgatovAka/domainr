"""
Главный файл инициализации пакета domain_registry_system.
"""

from core import (
    Domain,
    DomainRegistry,
    DomainEvent,
    EventType,
    DomainObserver,
    FilteredDomainObserver,
)

from observers import (
    WhoisService,
    BillingService,
    SecurityAudit,
    BackorderService,
)

__version__ = "1.0.0"
__author__ = "Student Name"
__description__ = "Domain Registry System - Observer Pattern Implementation"

__all__ = [
    # Core
    'Domain',
    'DomainRegistry',
    'DomainEvent',
    'EventType',
    'DomainObserver',
    'FilteredDomainObserver',
    # Observers
    'WhoisService',
    'BillingService',
    'SecurityAudit',
    'BackorderService',
]
