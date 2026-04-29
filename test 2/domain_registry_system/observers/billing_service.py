"""
Сервис выставления счетов — выставляет счета только при регистрации доменов.
Реагирует только на событие DOMAIN_REGISTERED.
"""

from core.observer import FilteredDomainObserver
from core.events import DomainEvent, EventType


class BillingService(FilteredDomainObserver):
    """
    Сервис биллинга выставляет счета владельцам при регистрации доменов.
    Использует фильтрацию событий — реагирует только на DOMAIN_REGISTERED.
    """
    
    def __init__(self):
        """Инициализирует сервис с фильтром на событие регистрации."""
        # Подписываемся только на события регистрации
        super().__init__(subscribed_events=[EventType.DOMAIN_REGISTERED])
    
    def handle_event(self, event: DomainEvent) -> None:
        """
        Выставляет счет при регистрации домена.
        
        Args:
            event: Событие регистрации домена
        """
        amount = self._calculate_price(event.domain_name)
        self._issue_invoice(event, amount)
    
    def _calculate_price(self, domain_name: str) -> float:
        """
        Рассчитывает стоимость регистрации домена.
        
        Args:
            domain_name: Имя домена
            
        Returns:
            Стоимость в условных единицах
        """
        # Примитивный расчет: за каждый символ 10 условных единиц
        base_price = 100.0
        return base_price + len(domain_name) * 10
    
    def _issue_invoice(self, event: DomainEvent, amount: float) -> None:
        """Выставляет счет владельцу домена."""
        print(
            f"💰 [BILLING SERVICE] Invoice issued:\n"
            f"   Domain: {event.domain_name}\n"
            f"   Owner: {event.owner_email}\n"
            f"   Amount: ${amount:.2f}\n"
            f"   Description: Annual domain registration fee"
        )
