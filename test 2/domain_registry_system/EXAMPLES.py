"""
ПРИМЕРЫ: Как написать собственного Observer'а?

Этот файл содержит примеры для студентов, которые хотят написать
свой наблюдатель для системы управления доменами.
"""

from core import DomainObserver, FilteredDomainObserver, DomainEvent, EventType, DomainRegistry, Domain


# ============================================================================
# ПРИМЕР 1: Простой Observer (реагирует на все события)
# ============================================================================

class EmailNotificationService(DomainObserver):
    """
    Пример: Сервис отправки email уведомлений.
    Реагирует на ВСЕ события.
    """
    
    def update(self, event: DomainEvent) -> None:
        """
        Отправляет email уведомление владельцу домена.
        
        Args:
            event: Событие об изменении домена
        """
        if event.event_type == EventType.DOMAIN_REGISTERED:
            self._send_registration_email(event)
        elif event.event_type == EventType.DOMAIN_DNS_UPDATED:
            self._send_dns_update_email(event)
        elif event.event_type == EventType.DOMAIN_DELETED:
            self._send_deletion_email(event)
    
    def _send_registration_email(self, event: DomainEvent) -> None:
        """Отправляет email о регистрации."""
        print(
            f"📧 [EMAIL SERVICE] Отправляю email владельцу {event.owner_email}\n"
            f"   Тема: Domain Registration Confirmation\n"
            f"   Домен {event.domain_name} успешно зарегистрирован!"
        )
    
    def _send_dns_update_email(self, event: DomainEvent) -> None:
        """Отправляет email об изменении DNS."""
        dns_list = ", ".join(event.dns_servers) if event.dns_servers else "N/A"
        print(
            f"📧 [EMAIL SERVICE] Отправляю email владельцу {event.owner_email}\n"
            f"   Тема: DNS Settings Updated\n"
            f"   DNS серверы изменены на: {dns_list}"
        )
    
    def _send_deletion_email(self, event: DomainEvent) -> None:
        """Отправляет email об удалении."""
        print(
            f"📧 [EMAIL SERVICE] Отправляю email владельцу {event.owner_email}\n"
            f"   Тема: Domain Deletion Notification\n"
            f"   Домен {event.domain_name} был удален из реестра"
        )


# ============================================================================
# ПРИМЕР 2: Observer с фильтрацией (реагирует только на определенные события)
# ============================================================================

class AnalyticsService(FilteredDomainObserver):
    """
    Пример: Сервис аналитики.
    Реагирует только на события регистрации для подсчета статистики.
    """
    
    def __init__(self):
        """Инициализирует сервис с фильтром на события регистрации."""
        super().__init__(subscribed_events=[EventType.DOMAIN_REGISTERED])
        self.registration_count = 0
        self.total_revenue = 0.0
    
    def handle_event(self, event: DomainEvent) -> None:
        """
        Обрабатывает события регистрации и собирает статистику.
        
        Args:
            event: Событие регистрации (благодаря фильтру, это ВСЕГДА регистрация)
        """
        self.registration_count += 1
        price = self._calculate_price(event.domain_name)
        self.total_revenue += price
        
        self._log_statistics(event)
    
    def _calculate_price(self, domain_name: str) -> float:
        """Рассчитывает стоимость домена."""
        base_price = 100.0
        return base_price + len(domain_name) * 10
    
    def _log_statistics(self, event: DomainEvent) -> None:
        """Логирует текущую статистику."""
        print(
            f"📊 [ANALYTICS SERVICE] Статистика обновлена:\n"
            f"   Всего регистраций: {self.registration_count}\n"
            f"   Общий доход: ${self.total_revenue:.2f}\n"
            f"   Последний домен: {event.domain_name}"
        )


# ============================================================================
# ПРИМЕР 3: Observer с собственной логикой хранения
# ============================================================================

class DomainCacheService(DomainObserver):
    """
    Пример: Сервис кэширования информации о доменах.
    Реагирует на все события и обновляет кэш.
    """
    
    def __init__(self):
        """Инициализирует сервис с пустым кэшем."""
        self._cache = {}  # Кэш доменов
    
    def update(self, event: DomainEvent) -> None:
        """
        Обновляет кэш при изменении домена.
        
        Args:
            event: Событие об изменении
        """
        if event.event_type == EventType.DOMAIN_REGISTERED:
            self._add_to_cache(event)
        elif event.event_type == EventType.DOMAIN_DNS_UPDATED:
            self._update_cache(event)
        elif event.event_type == EventType.DOMAIN_DELETED:
            self._remove_from_cache(event)
    
    def _add_to_cache(self, event: DomainEvent) -> None:
        """Добавляет домен в кэш."""
        self._cache[event.domain_name] = {
            'owner': event.owner_email,
            'dns': event.dns_servers.copy() if event.dns_servers else [],
            'status': 'active'
        }
        print(
            f"💾 [CACHE SERVICE] Домен добавлен в кэш: {event.domain_name}\n"
            f"   Размер кэша: {len(self._cache)} доменов"
        )
    
    def _update_cache(self, event: DomainEvent) -> None:
        """Обновляет информацию в кэше."""
        if event.domain_name in self._cache:
            self._cache[event.domain_name]['dns'] = event.dns_servers.copy() if event.dns_servers else []
            print(
                f"💾 [CACHE SERVICE] Кэш обновлен: {event.domain_name}\n"
                f"   Новые DNS: {', '.join(event.dns_servers) if event.dns_servers else 'N/A'}"
            )
    
    def _remove_from_cache(self, event: DomainEvent) -> None:
        """Удаляет домен из кэша."""
        if event.domain_name in self._cache:
            del self._cache[event.domain_name]
            print(
                f"💾 [CACHE SERVICE] Домен удален из кэша: {event.domain_name}\n"
                f"   Размер кэша: {len(self._cache)} доменов"
            )
    
    def get_cached_domain(self, domain_name: str):
        """Возвращает информацию о домене из кэша."""
        return self._cache.get(domain_name)


# ============================================================================
# ПРИМЕР 4: Observer с обработкой ошибок
# ============================================================================

class SlowDatabaseService(DomainObserver):
    """
    Пример: Сервис, который может выбросить исключение
    (например, при недоступности базы данных).
    
    Демонстрирует, как работает обработка ошибок.
    """
    
    def __init__(self, simulate_error: bool = False):
        """
        Инициализирует сервис.
        
        Args:
            simulate_error: Если True, сервис выбросит исключение
        """
        self.simulate_error = simulate_error
    
    def update(self, event: DomainEvent) -> None:
        """
        Сохраняет событие в базу данных.
        Может выбросить исключение, если БД недоступна.
        
        Args:
            event: Событие для сохранения
        """
        if self.simulate_error:
            raise ConnectionError("❌ Database connection failed!")
        
        print(
            f"🗄️  [DATABASE SERVICE] Событие сохранено в БД:\n"
            f"   ID: {event.domain_name}-{event.timestamp.timestamp()}\n"
            f"   Тип: {event.event_type.value}"
        )


# ============================================================================
# ПРИМЕР 5: Advanced — Observer с фильтрацией по другим параметрам
# ============================================================================

class AdvancedFilteredObserver(FilteredDomainObserver):
    """
    Пример: Observer с дополнительными критериями фильтрации.
    Реагирует только на события определенного домена.
    
    Это расширение базового функционала фильтрации.
    """
    
    def __init__(self, subscribed_events=None, domain_filter: str = None):
        """
        Инициализирует observer с фильтрацией.
        
        Args:
            subscribed_events: Список типов событий для фильтрации
            domain_filter: Конкретный домен для отслеживания (или None для всех)
        """
        super().__init__(subscribed_events=subscribed_events)
        self.domain_filter = domain_filter
    
    def is_interested(self, event: DomainEvent) -> bool:
        """
        Проверяет, интересует ли этого наблюдателя данное событие.
        Учитывает и тип события, и имя домена.
        
        Args:
            event: Событие для проверки
            
        Returns:
            True, если наблюдатель должен обработать это событие
        """
        # Сначала проверяем фильтр по типу события
        if not super().is_interested(event):
            return False
        
        # Потом проверяем фильтр по имени домена
        if self.domain_filter is not None:
            return event.domain_name == self.domain_filter
        
        return True
    
    def handle_event(self, event: DomainEvent) -> None:
        """Обрабатывает событие для интересующего домена."""
        print(
            f"🎯 [ADVANCED OBSERVER] Событие для отслеживаемого домена:\n"
            f"   Домен: {event.domain_name}\n"
            f"   Тип: {event.event_type.value}"
        )


# ============================================================================
# ДЕМОНСТРАЦИЯ: Использование собственных Observer'ов
# ============================================================================

def example_usage():
    """Демонстрирует использование пользовательских Observer'ов."""
    
    print("\n" + "=" * 80)
    print("  ПРИМЕРЫ: Собственные Observer'ы")
    print("=" * 80 + "\n")
    
    # Создаем реестр
    registry = DomainRegistry()
    
    # Добавляем собственные наблюдатели
    email = EmailNotificationService()
    analytics = AnalyticsService()
    cache = DomainCacheService()
    advanced = AdvancedFilteredObserver(domain_filter="important.kz")
    
    # Подписываем их
    registry.subscribe(email)
    registry.subscribe(analytics)
    registry.subscribe(cache)
    registry.subscribe(advanced)
    
    # Регистрируем обычный домен
    print("\n--- Регистрируем обычный домен ---\n")
    domain1 = Domain("example.kz", "user@example.kz", ["ns1.example.com"])
    registry.register(domain1)
    
    # Регистрируем домен, на который подписан AdvancedFilteredObserver
    print("\n--- Регистрируем отслеживаемый домен ---\n")
    domain2 = Domain("important.kz", "vip@important.kz", ["ns1.important.com"])
    registry.register(domain2)
    
    # Обновляем DNS
    print("\n--- Обновляем DNS (Analytics не реагирует) ---\n")
    registry.update_dns("example.kz", ["ns2.new.com"])
    
    # Демонстрация обработки ошибок
    print("\n--- Демонстрация обработки ошибок ---\n")
    slow_db = SlowDatabaseService(simulate_error=True)
    registry.subscribe(slow_db)
    
    domain3 = Domain("test.kz", "test@test.kz")
    print("Даже если SlowDatabaseService выбросит ошибку, остальные получат событие:\n")
    registry.register(domain3)


if __name__ == "__main__":
    example_usage()
