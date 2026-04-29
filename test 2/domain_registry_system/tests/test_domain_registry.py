"""
Основной тестовый сценарий, демонстрирующий работу системы управления доменами.

Этап 3: Тестовый сценарий

Демонстрирует:
1. Регистрацию домена -> Billing, Whois, Audit активны
2. Обновление DNS -> Billing должен игнорировать, остальные сработают
3. Удаление домена -> BackorderService активен
"""

import sys
import os

# Добавляем родительскую директорию в path для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Domain, DomainRegistry
from observers import WhoisService, BillingService, SecurityAudit, BackorderService


def print_section(title: str) -> None:
    """Печатает заголовок секции."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Основная функция для запуска демонстрации."""
    
    print_section("СИСТЕМА УПРАВЛЕНИЯ ДОМЕНАМИ — ДЕМОНСТРАЦИЯ")
    
    # ============================================================================
    # ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ
    # ============================================================================
    print("📦 Инициализация системы...\n")
    
    # Создаем реестр доменов (Subject)
    registry = DomainRegistry()
    
    # Создаем наблюдателей (Observers)
    whois = WhoisService()
    billing = BillingService()
    audit = SecurityAudit()
    backorder = BackorderService()
    
    # Подписываем наблюдателей на события
    registry.subscribe(whois)
    registry.subscribe(billing)
    registry.subscribe(audit)
    registry.subscribe(backorder)
    
    print("✅ Все сервисы инициализированы и подписаны на события\n")
    
    # ============================================================================
    # ТЕСТОВЫЙ СЦЕНАРИЙ 1: РЕГИСТРАЦИЯ ДОМЕНА
    # ============================================================================
    print_section("СЦЕНАРИЙ 1: РЕГИСТРАЦИЯ ДОМЕНА google.kz")
    print("Ожидаемое поведение:")
    print("  ✓ BillingService выставит счет (реагирует на REGISTER)")
    print("  ✓ WhoisService опубликует информацию")
    print("  ✓ SecurityAudit запишет в лог")
    print("  ✓ BackorderService проверит заявки\n")
    
    try:
        google_domain = Domain(
            name="google.kz",
            owner_email="admin@google.kz",
            dns_servers=["ns1.google.com", "ns2.google.com"]
        )
        registry.register(google_domain)
    except Exception as e:
        print(f"❌ Ошибка при регистрации: {e}\n")
    
    # ============================================================================
    # ТЕСТОВЫЙ СЦЕНАРИЙ 2: ОБНОВЛЕНИЕ DNS
    # ============================================================================
    print_section("СЦЕНАРИЙ 2: ОБНОВЛЕНИЕ DNS-СЕРВЕРОВ для google.kz")
    print("Ожидаемое поведение:")
    print("  ✓ BillingService НЕ реагирует (ждет только REGISTER)")
    print("  ✓ WhoisService обновит информацию")
    print("  ✓ SecurityAudit запишет в лог")
    print("  ✓ BackorderService не реагирует\n")
    
    try:
        new_dns_servers = [
            "ns1.example.com",
            "ns2.example.com",
            "ns3.example.com"
        ]
        registry.update_dns("google.kz", new_dns_servers)
    except Exception as e:
        print(f"❌ Ошибка при обновлении DNS: {e}\n")
    
    # ============================================================================
    # ТЕСТОВЫЙ СЦЕНАРИЙ 3: РЕГИСТРАЦИЯ ДРУГОГО ДОМЕНА
    # ============================================================================
    print_section("СЦЕНАРИЙ 3: РЕГИСТРАЦИЯ ДОМЕНА popular.kz")
    print("Ожидаемое поведение: Все сервисы реагируют\n")
    
    try:
        popular_domain = Domain(
            name="popular.kz",
            owner_email="owner@popular.kz",
            dns_servers=["ns1.popular.kz"]
        )
        registry.register(popular_domain)
    except Exception as e:
        print(f"❌ Ошибка при регистрации: {e}\n")
    
    # ============================================================================
    # ТЕСТОВЫЙ СЦЕНАРИЙ 4: УДАЛЕНИЕ ДОМЕНА
    # ============================================================================
    print_section("СЦЕНАРИЙ 4: УДАЛЕНИЕ ДОМЕНА google.kz")
    print("Ожидаемое поведение:")
    print("  ✓ BillingService НЕ реагирует")
    print("  ✓ WhoisService обновит статус на INACTIVE")
    print("  ✓ SecurityAudit запишет в лог")
    print("  ✓ BackorderService запустит аукцион (есть заявки!)\n")
    
    try:
        registry.delete("google.kz")
    except Exception as e:
        print(f"❌ Ошибка при удалении: {e}\n")
    
    # ============================================================================
    # ТЕСТОВЫЙ СЦЕНАРИЙ 5: ОБРАБОТКА ОШИБОК
    # ============================================================================
    print_section("СЦЕНАРИЙ 5: ПРОВЕРКА ОБРАБОТКИ ОШИБОК")
    print("Попытка удалить несуществующий домен...\n")
    
    try:
        registry.delete("nonexistent.kz")
    except ValueError as e:
        print(f"✅ Ошибка корректно обработана: {e}\n")
    
    # ============================================================================
    # ПРОСМОТР АУДИТ-ЛОГА
    # ============================================================================
    print_section("СОДЕРЖИМОЕ АУДИТ-ЛОГА")
    print(audit.get_log_content())
    
    # ============================================================================
    # ИТОГОВАЯ ИНФОРМАЦИЯ
    # ============================================================================
    print_section("ИТОГОВАЯ ИНФОРМАЦИЯ")
    
    remaining_domains = registry.list_domains()
    print(f"✅ Доменов в реестре: {len(remaining_domains)}")
    for domain in remaining_domains:
        print(f"   • {domain}")
    
    print("\n📝 Файл аудита сохранен в: audit.log")
    print("\n" + "=" * 80)
    print("  ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
