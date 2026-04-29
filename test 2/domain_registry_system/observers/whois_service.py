"""
Сервис Whois — публикует изменения в статусе доменов.
Реагирует на ВСЕ события и обновляет публичную запись.
"""

from core.observer import DomainObserver
from core.events import DomainEvent, EventType


class WhoisService(DomainObserver):
    """
    Сервис Whois обновляет публичную информацию о домене при каждом изменении.
    Реагирует на все типы событий.
    """
    
    def update(self, event: DomainEvent) -> None:
        """
        Обновляет записи Whois для домена.
        
        Args:
            event: Событие об изменении домена
        """
        if event.event_type == EventType.DOMAIN_REGISTERED:
            self._publish_registration(event)
        elif event.event_type == EventType.DOMAIN_DNS_UPDATED:
            self._publish_dns_update(event)
        elif event.event_type == EventType.DOMAIN_DELETED:
            self._publish_deletion(event)
    
    def _publish_registration(self, event: DomainEvent) -> None:
        """Публикует информацию о регистрации домена."""
        dns_list = ", ".join(event.dns_servers) if event.dns_servers else "Not configured"
        print(
            f"🌐 [WHOIS SERVICE] Domain registered:\n"
            f"   Name: {event.domain_name}\n"
            f"   Owner: {event.owner_email}\n"
            f"   DNS Servers: {dns_list}\n"
            f"   Status: ACTIVE"
        )
    
    def _publish_dns_update(self, event: DomainEvent) -> None:
        """Публикует обновление DNS-серверов."""
        dns_list = ", ".join(event.dns_servers) if event.dns_servers else "Not configured"
        print(
            f"🌐 [WHOIS SERVICE] DNS servers updated:\n"
            f"   Domain: {event.domain_name}\n"
            f"   New DNS: {dns_list}"
        )
    
    def _publish_deletion(self, event: DomainEvent) -> None:
        """Публикует информацию об удалении домена."""
        print(
            f"🌐 [WHOIS SERVICE] Domain deleted:\n"
            f"   Name: {event.domain_name}\n"
            f"   Status: INACTIVE"
        )
