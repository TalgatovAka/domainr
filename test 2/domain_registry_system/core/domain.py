"""
Модуль для определения класса Domain.
Содержит основную структуру данных для хранения информации о домене.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Domain:
    """
    Представляет доменное имя с его метаданными.
    
    Attributes:
        name: Имя домена (например, mysite.kz)
        owner_email: Email владельца домена
        dns_servers: Список DNS-серверов для этого домена
    """
    name: str
    owner_email: str
    dns_servers: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        dns_info = ", ".join(self.dns_servers) if self.dns_servers else "No DNS configured"
        return f"Domain({self.name}) | Owner: {self.owner_email} | DNS: {dns_info}"
    
    def __eq__(self, other) -> bool:
        """Два домена считаются равными, если совпадают их имена."""
        if not isinstance(other, Domain):
            return False
        return self.name == other.name
