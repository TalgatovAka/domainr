"""
Модуль с определением класса DomainRegistry (Subject).
Реализует логику управления доменами и систему подписки наблюдателей.
"""

from typing import List, Dict
from datetime import datetime
import logging

from .domain import Domain
from .observer import DomainObserver
from .events import DomainEvent, EventType


# Настройка логирования для отладки
logger = logging.getLogger(__name__)


class DomainRegistry:
    """
    Реестр доменов (Subject в паттерне Observer).
    
    Это главный класс системы, который:
    - Управляет жизненным циклом доменов (регистрация, обновление, удаление)
    - Уведомляет подписчиков (наблюдателей) о каждом действии
    - Не знает о деталях работы других сервисов (Dependency Inversion)
    
    Attributes:
        _domains: Словарь, хранящий зарегистрированные домены
        _observers: Список подписчиков на события
    """
    
    def __init__(self):
        """Инициализирует пустой реестр доменов и список наблюдателей."""
        self._domains: Dict[str, Domain] = {}
        self._observers: List[DomainObserver] = []
    
    def subscribe(self, observer: DomainObserver) -> None:
        """
        Добавляет наблюдателя в список подписчиков.
        
        Args:
            observer: Объект, реализующий интерфейс DomainObserver
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observer {observer.__class__.__name__} subscribed")
    
    def unsubscribe(self, observer: DomainObserver) -> None:
        """
        Удаляет наблюдателя из списка подписчиков.
        
        Args:
            observer: Объект для удаления
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observer {observer.__class__.__name__} unsubscribed")
    
    def _notify_observers(self, event: DomainEvent) -> None:
        """
        Уведомляет всех подписчиков о событии.
        
        Важная особенность: Если один из наблюдателей выбросит исключение,
        остальные всё равно получат уведомление (принцип надежности).
        
        Args:
            event: Событие для уведомления
        """
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                logger.error(
                    f"Error notifying {observer.__class__.__name__}: {e}",
                    exc_info=True
                )
    
    def register(self, domain: Domain) -> None:
        """
        Регистрирует новый домен в реестре.
        
        Args:
            domain: Объект домена для регистрации
            
        Raises:
            ValueError: Если домен с таким именем уже зарегистрирован
        """
        if domain.name in self._domains:
            raise ValueError(f"Domain {domain.name} already registered")
        
        self._domains[domain.name] = domain
        logger.info(f"Domain {domain.name} registered for {domain.owner_email}")
        
        # Уведомляем всех наблюдателей о регистрации
        event = DomainEvent(
            event_type=EventType.DOMAIN_REGISTERED,
            domain_name=domain.name,
            owner_email=domain.owner_email,
            dns_servers=domain.dns_servers.copy(),
            timestamp=datetime.now()
        )
        self._notify_observers(event)
    
    def update_dns(self, domain_name: str, new_dns_servers: List[str]) -> None:
        """
        Обновляет список DNS-серверов для домена.
        
        Args:
            domain_name: Имя домена для обновления
            new_dns_servers: Новый список DNS-серверов
            
        Raises:
            ValueError: Если домен не найден в реестре
        """
        if domain_name not in self._domains:
            raise ValueError(f"Domain {domain_name} not found")
        
        domain = self._domains[domain_name]
        domain.dns_servers = new_dns_servers.copy()
        logger.info(f"DNS updated for {domain_name}: {new_dns_servers}")
        
        # Уведомляем всех наблюдателей об обновлении DNS
        event = DomainEvent(
            event_type=EventType.DOMAIN_DNS_UPDATED,
            domain_name=domain.name,
            owner_email=domain.owner_email,
            dns_servers=domain.dns_servers.copy(),
            timestamp=datetime.now()
        )
        self._notify_observers(event)
    
    def delete(self, domain_name: str) -> None:
        """
        Удаляет домен из реестра.
        
        Args:
            domain_name: Имя домена для удаления
            
        Raises:
            ValueError: Если домен не найден в реестре
        """
        if domain_name not in self._domains:
            raise ValueError(f"Domain {domain_name} not found")
        
        domain = self._domains.pop(domain_name)
        logger.info(f"Domain {domain_name} deleted")
        
        # Уведомляем всех наблюдателей об удалении
        event = DomainEvent(
            event_type=EventType.DOMAIN_DELETED,
            domain_name=domain.name,
            owner_email=domain.owner_email,
            dns_servers=domain.dns_servers.copy(),
            timestamp=datetime.now()
        )
        self._notify_observers(event)
    
    def get_domain(self, domain_name: str) -> Domain:
        """
        Получает информацию о домене.
        
        Args:
            domain_name: Имя домена
            
        Returns:
            Объект Domain или None, если домен не найден
        """
        return self._domains.get(domain_name)
    
    def list_domains(self) -> List[Domain]:
        """
        Возвращает список всех зарегистрированных доменов.
        
        Returns:
            Список объектов Domain
        """
        return list(self._domains.values())
