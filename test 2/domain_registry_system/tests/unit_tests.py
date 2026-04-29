"""
Тесты для проверки корректности работы системы.
Этап 4: Unit-тесты для каждого компонента.
"""

import sys
import os
import unittest
from datetime import datetime

# Добавляем родительскую директорию в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Domain, DomainRegistry, DomainEvent, EventType, FilteredDomainObserver
from observers import WhoisService, BillingService, SecurityAudit, BackorderService


class TestDomain(unittest.TestCase):
    """Тесты для класса Domain."""
    
    def test_domain_creation(self):
        """Тест создания доменов."""
        domain = Domain("example.kz", "owner@example.kz", ["ns1.example.com"])
        self.assertEqual(domain.name, "example.kz")
        self.assertEqual(domain.owner_email, "owner@example.kz")
        self.assertEqual(len(domain.dns_servers), 1)
    
    def test_domain_equality(self):
        """Тест сравнения доменов."""
        domain1 = Domain("test.kz", "user1@test.kz")
        domain2 = Domain("test.kz", "user2@test.kz")
        self.assertEqual(domain1, domain2)
    
    def test_domain_string_representation(self):
        """Тест представления домена в виде строки."""
        domain = Domain("example.kz", "owner@example.kz", ["ns1.com", "ns2.com"])
        str_repr = str(domain)
        self.assertIn("example.kz", str_repr)
        self.assertIn("owner@example.kz", str_repr)


class TestDomainRegistry(unittest.TestCase):
    """Тесты для класса DomainRegistry."""
    
    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.registry = DomainRegistry()
        self.domain = Domain("test.kz", "owner@test.kz")
    
    def test_register_domain(self):
        """Тест регистрации домена."""
        self.registry.register(self.domain)
        retrieved = self.registry.get_domain("test.kz")
        self.assertEqual(retrieved.name, "test.kz")
    
    def test_duplicate_registration_raises_error(self):
        """Тест ошибки при дублировании регистрации."""
        self.registry.register(self.domain)
        with self.assertRaises(ValueError):
            self.registry.register(self.domain)
    
    def test_update_dns(self):
        """Тест обновления DNS-серверов."""
        self.registry.register(self.domain)
        new_dns = ["ns1.new.com", "ns2.new.com"]
        self.registry.update_dns("test.kz", new_dns)
        retrieved = self.registry.get_domain("test.kz")
        self.assertEqual(retrieved.dns_servers, new_dns)
    
    def test_update_nonexistent_domain_raises_error(self):
        """Тест ошибки при обновлении несуществующего домена."""
        with self.assertRaises(ValueError):
            self.registry.update_dns("nonexistent.kz", [])
    
    def test_delete_domain(self):
        """Тест удаления домена."""
        self.registry.register(self.domain)
        self.registry.delete("test.kz")
        retrieved = self.registry.get_domain("test.kz")
        self.assertIsNone(retrieved)
    
    def test_delete_nonexistent_domain_raises_error(self):
        """Тест ошибки при удалении несуществующего домена."""
        with self.assertRaises(ValueError):
            self.registry.delete("nonexistent.kz")
    
    def test_list_domains(self):
        """Тест получения списка доменов."""
        domain1 = Domain("test1.kz", "owner1@test.kz")
        domain2 = Domain("test2.kz", "owner2@test.kz")
        self.registry.register(domain1)
        self.registry.register(domain2)
        domains = self.registry.list_domains()
        self.assertEqual(len(domains), 2)


class MockObserver(FilteredDomainObserver):
    """Моковый наблюдатель для тестирования."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
    
    def handle_event(self, event: DomainEvent) -> None:
        self.events.append(event)


class TestObserverPattern(unittest.TestCase):
    """Тесты для паттерна Observer."""
    
    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.registry = DomainRegistry()
        self.observer = MockObserver()
        self.registry.subscribe(self.observer)
    
    def test_observer_receives_registration_event(self):
        """Тест получения события регистрации."""
        domain = Domain("test.kz", "owner@test.kz")
        self.registry.register(domain)
        self.assertEqual(len(self.observer.events), 1)
        self.assertEqual(self.observer.events[0].event_type, EventType.DOMAIN_REGISTERED)
    
    def test_observer_receives_update_event(self):
        """Тест получения события обновления."""
        domain = Domain("test.kz", "owner@test.kz")
        self.registry.register(domain)
        self.observer.events.clear()
        
        self.registry.update_dns("test.kz", ["ns1.new.com"])
        self.assertEqual(len(self.observer.events), 1)
        self.assertEqual(self.observer.events[0].event_type, EventType.DOMAIN_DNS_UPDATED)
    
    def test_observer_receives_deletion_event(self):
        """Тест получения события удаления."""
        domain = Domain("test.kz", "owner@test.kz")
        self.registry.register(domain)
        self.observer.events.clear()
        
        self.registry.delete("test.kz")
        self.assertEqual(len(self.observer.events), 1)
        self.assertEqual(self.observer.events[0].event_type, EventType.DOMAIN_DELETED)
    
    def test_filtered_observer_ignores_unsubscribed_events(self):
        """Тест фильтрации событий."""
        # Создаем наблюдателя, интересуемого только регистрацией
        filtered_observer = MockObserver(subscribed_events=[EventType.DOMAIN_REGISTERED])
        self.registry.subscribe(filtered_observer)
        
        domain = Domain("test.kz", "owner@test.kz")
        self.registry.register(domain)
        self.assertEqual(len(filtered_observer.events), 1)
        
        # Обновляем DNS
        self.registry.update_dns("test.kz", ["ns1.new.com"])
        # Должно остаться 1 событие (регистрация), обновление не должно быть добавлено
        self.assertEqual(len(filtered_observer.events), 1)
    
    def test_unsubscribe_observer(self):
        """Тест отписки наблюдателя."""
        domain = Domain("test.kz", "owner@test.kz")
        self.registry.register(domain)
        self.assertEqual(len(self.observer.events), 1)
        
        self.registry.unsubscribe(self.observer)
        self.observer.events.clear()
        
        # Удаляем домен
        self.registry.delete("test.kz")
        # Наблюдатель отписан, поэтому не получит событие
        self.assertEqual(len(self.observer.events), 0)


class TestBillingService(unittest.TestCase):
    """Тесты для сервиса выставления счетов."""
    
    def test_billing_only_reacts_to_registration(self):
        """Тест что биллинг реагирует только на регистрацию."""
        registry = DomainRegistry()
        billing = BillingService()
        registry.subscribe(billing)
        
        domain = Domain("test.kz", "owner@test.kz")
        # При регистрации биллинг должен реагировать
        registry.register(domain)
        
        # При обновлении DNS биллинг не должен реагировать
        registry.update_dns("test.kz", ["ns1.new.com"])
        
        # При удалении биллинг не должен реагировать
        registry.delete("test.kz")


class TestSecurityAudit(unittest.TestCase):
    """Тесты для сервиса аудита."""
    
    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.audit = SecurityAudit("test_audit.log")
        # Очищаем файл перед тестом
        with open("test_audit.log", 'w') as f:
            f.write("")
    
    def tearDown(self):
        """Очистка после тестов."""
        if os.path.exists("test_audit.log"):
            os.remove("test_audit.log")
    
    def test_audit_logs_events(self):
        """Тест логирования событий."""
        event = DomainEvent(
            event_type=EventType.DOMAIN_REGISTERED,
            domain_name="test.kz",
            owner_email="owner@test.kz",
            timestamp=datetime.now()
        )
        self.audit.update(event)
        
        log_content = self.audit.get_log_content()
        self.assertIn("test.kz", log_content)
        self.assertIn("DOMAIN_REGISTERED", log_content)


if __name__ == "__main__":
    unittest.main()
