"""
Сервис безопасности — ведет аудит всех действий с доменами.
Реагирует на все события и записывает их в лог файл.
"""

import os
from datetime import datetime
from core.observer import DomainObserver
from core.events import DomainEvent, EventType


class SecurityAudit(DomainObserver):
    """
    Сервис аудита безопасности записывает все действия с доменами в файл.
    Реагирует на ВСЕ события.
    """
    
    LOG_FILE = "audit.log"
    
    def __init__(self, log_file: str = None):
        """
        Инициализирует сервис аудита.
        
        Args:
            log_file: Путь к файлу логов (если None, используется audit.log)
        """
        self.log_file = log_file or self.LOG_FILE
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self) -> None:
        """Создает файл логов, если его еще нет."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("DOMAIN REGISTRY AUDIT LOG\n")
                f.write(f"Log started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
    
    def update(self, event: DomainEvent) -> None:
        """
        Записывает событие в лог файл.
        
        Args:
            event: Событие для логирования
        """
        log_entry = self._format_log_entry(event)
        self._write_to_log(log_entry)
        print(f"📋 [SECURITY AUDIT] Event logged: {event.event_type.value}")
    
    def _format_log_entry(self, event: DomainEvent) -> str:
        """
        Форматирует запись события для логирования.
        
        Args:
            event: Событие для форматирования
            
        Returns:
            Отформатированная строка лога
        """
        timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        event_type = event.event_type.value.upper()
        dns_info = ", ".join(event.dns_servers) if event.dns_servers else "N/A"
        
        return (
            f"[{timestamp}] ACTION: {event_type}\n"
            f"  Domain: {event.domain_name}\n"
            f"  Owner: {event.owner_email}\n"
            f"  DNS Servers: {dns_info}\n"
            f"{'-' * 80}\n"
        )
    
    def _write_to_log(self, entry: str) -> None:
        """
        Записывает запись в файл логов.
        
        Args:
            entry: Строка для записи
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        except IOError as e:
            print(f"❌ Error writing to audit log: {e}")
    
    def get_log_content(self) -> str:
        """
        Возвращает содержимое лог файла.
        
        Returns:
            Содержимое файла логов
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            return f"Error reading log file: {e}"
