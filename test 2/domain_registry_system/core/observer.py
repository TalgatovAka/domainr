"""
Модуль с определением абстрактного интерфейса наблюдателя.
Соответствует паттерну Observer и принципу Dependency Inversion.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .events import DomainEvent, EventType


class DomainObserver(ABC):
    """
    Абстрактный базовый класс для всех наблюдателей за событиями в реестре доменов.
    
    Любой класс, желающий получать уведомления о событиях в DomainRegistry,
    должен наследоваться от этого класса и реализовать метод update().
    """
    
    @abstractmethod
    def update(self, event: DomainEvent) -> None:
        """
        Вызывается реестром при возникновении события.
        
        Args:
            event: Объект события, содержащий информацию о произошедшем действии
        """
        pass


class FilteredDomainObserver(DomainObserver):
    """
    Расширенная версия наблюдателя с поддержкой фильтрации событий.
    Позволяет наблюдателю подписаться только на интересующие события.
    
    Это реализация дополнительного задания на "отлично".
    """
    
    def __init__(self, subscribed_events: Optional[List[EventType]] = None):
        """
        Инициализация фильтрованного наблюдателя.
        
        Args:
            subscribed_events: Список типов событий, на которые подписан наблюдатель.
                             Если None, наблюдатель получит все события.
        """
        self.subscribed_events = subscribed_events
    
    def is_interested(self, event: DomainEvent) -> bool:
        """
        Проверяет, интересует ли этого наблюдателя данное событие.
        
        Args:
            event: Событие для проверки
            
        Returns:
            True, если наблюдатель должен получить это событие
        """
        if self.subscribed_events is None:
            return True
        return event.event_type in self.subscribed_events
    
    def update(self, event: DomainEvent) -> None:
        """
        Обновляет наблюдателя только если событие в списке интересующих.
        Подклассы должны переопределить метод handle_event().
        
        Args:
            event: Объект события
        """
        if self.is_interested(event):
            self.handle_event(event)
    
    @abstractmethod
    def handle_event(self, event: DomainEvent) -> None:
        """
        Обработчик события. Должен быть реализован подклассами.
        
        Args:
            event: Событие для обработки
        """
        pass
