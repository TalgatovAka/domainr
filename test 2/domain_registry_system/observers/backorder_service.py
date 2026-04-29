"""
Сервис перехвата удаленных доменов (Backorder Service).
Реагирует только на событие удаления доменов и проверяет, есть ли заявки на них.
"""

from core.observer import FilteredDomainObserver
from core.events import DomainEvent, EventType


class BackorderService(FilteredDomainObserver):
    """
    Сервис перехвата доменов проверяет наличие заявок на удаляемые домены.
    Используется для перепродажи «горячих» доменов.
    Реагирует только на событие DOMAIN_DELETED.
    """
    
    def __init__(self):
        """Инициализирует сервис с фильтром на событие удаления."""
        # Подписываемся только на события удаления доменов
        super().__init__(subscribed_events=[EventType.DOMAIN_DELETED])
        # Имитируем базу данных заявок на домены
        self._backorder_requests = {
            "google.kz": ["user1@example.com", "user2@example.com"],
            "popular.kz": ["enthusiast@example.com"],
            "famous.kz": []
        }
    
    def handle_event(self, event: DomainEvent) -> None:
        """
        Проверяет наличие заявок на удаляемый домен.
        
        Args:
            event: Событие удаления домена
        """
        backorders = self._check_backorders(event.domain_name)
        self._process_backorders(event, backorders)
    
    def _check_backorders(self, domain_name: str) -> list:
        """
        Проверяет, есть ли заявки на данный домен.
        
        Args:
            domain_name: Имя домена
            
        Returns:
            Список email адресов пользователей, заинтересованных в домене
        """
        return self._backorder_requests.get(domain_name, [])
    
    def _process_backorders(self, event: DomainEvent, backorders: list) -> None:
        """
        Обрабатывает заявки на удаленный домен.
        
        Args:
            event: Событие удаления
            backorders: Список заявок
        """
        if not backorders:
            print(
                f"🔓 [BACKORDER SERVICE] Domain released:\n"
                f"   Name: {event.domain_name}\n"
                f"   Status: No backorder requests found\n"
                f"   Action: Available for public registration"
            )
        else:
            print(
                f"🎯 [BACKORDER SERVICE] Domain auction started:\n"
                f"   Name: {event.domain_name}\n"
                f"   Interested users: {len(backorders)}\n"
                f"   Auction participants:"
            )
            for i, email in enumerate(backorders, 1):
                print(f"      {i}. {email}")
            print(f"   Action: Sending notification to interested parties...")
