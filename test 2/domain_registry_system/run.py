"""
Файл для запуска демонстрации и тестов системы.
Содержит удобный интерфейс выбора действий.
"""

import sys
import os
import subprocess

# Добавляем текущую директорию в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_menu():
    """Выводит главное меню."""
    print("\n" + "=" * 80)
    print("  СИСТЕМА УПРАВЛЕНИЯ ДОМЕННЫМИ ИМЕНАМИ")
    print("=" * 80)
    print("\n1. 🚀 Запустить демонстрацию (основной тестовый сценарий)")
    print("2. 🧪 Запустить unit-тесты")
    print("3. 📋 Просмотреть аудит-лог")
    print("4. 🧹 Очистить аудит-лог")
    print("5. 📚 Показать справку по структуре проекта")
    print("6. ❌ Выход")
    print("\n" + "-" * 80)
    return input("Выберите действие (1-6): ").strip()


def run_demo():
    """Запускает основную демонстрацию."""
    print("\n" + "=" * 80)
    print("  Запуск демонстрации...")
    print("=" * 80 + "\n")
    
    try:
        from tests.test_domain_registry import main
        main()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что вы находитесь в директории domain_registry_system")


def run_tests():
    """Запускает unit-тесты."""
    print("\n" + "=" * 80)
    print("  Запуск unit-тестов...")
    print("=" * 80 + "\n")
    
    try:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='unit_tests.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("\n✅ Все тесты прошли успешно!")
        else:
            print(f"\n❌ Некоторые тесты не прошли:")
            print(f"   Failures: {len(result.failures)}")
            print(f"   Errors: {len(result.errors)}")
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")


def view_audit_log():
    """Просматривает содержимое аудит-лога."""
    audit_file = "audit.log"
    
    if not os.path.exists(audit_file):
        print("\n⚠️  Файл audit.log не найден.")
        print("Сначала запустите демонстрацию, чтобы создать лог.")
        return
    
    print("\n" + "=" * 80)
    print("  СОДЕРЖИМОЕ АУДИТ-ЛОГА (audit.log)")
    print("=" * 80 + "\n")
    
    try:
        with open(audit_file, 'r', encoding='utf-8') as f:
            print(f.read())
    except IOError as e:
        print(f"❌ Ошибка при чтении файла: {e}")


def clear_audit_log():
    """Очищает аудит-лог."""
    audit_file = "audit.log"
    
    if not os.path.exists(audit_file):
        print("\n✅ Файл audit.log уже удален.")
        return
    
    confirm = input("\n⚠️  Вы уверены? Это действие нельзя отменить (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            os.remove(audit_file)
            print("✅ Аудит-лог успешно очищен.")
        except Exception as e:
            print(f"❌ Ошибка при удалении файла: {e}")
    else:
        print("❌ Действие отменено.")


def show_help():
    """Показывает справку по структуре проекта."""
    help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║           СТРУКТУРА ПРОЕКТА — СИСТЕМА УПРАВЛЕНИЯ ДОМЕНАМИ                ║
╚════════════════════════════════════════════════════════════════════════════╝

📁 ОСНОВНЫЕ МОДУЛИ
────────────────────────────────────────────────────────────────────────────

core/
  ├─ domain.py           📦 Класс Domain
  │  └─ Хранит имя, email владельца и DNS-серверы
  │
  ├─ events.py           📢 События системы
  │  └─ EventType (REGISTERED, DNS_UPDATED, DELETED)
  │  └─ DomainEvent (объект события с деталями)
  │
  ├─ observer.py         👁️  Интерфейсы наблюдателей
  │  ├─ DomainObserver (абстрактный класс)
  │  └─ FilteredDomainObserver (с поддержкой фильтрации)
  │
  └─ registry.py         📋 DomainRegistry (Subject)
     ├─ subscribe(observer)
     ├─ register(domain) → уведомление
     ├─ update_dns(name, dns) → уведомление
     └─ delete(name) → уведомление

observers/
  ├─ whois_service.py       🌐 WhoisService (реагирует на ВСЕ)
  │  └─ Публикует информацию о доменах
  │
  ├─ billing_service.py     💰 BillingService (только REGISTERED)
  │  └─ Выставляет счета владельцам
  │  └─ Использует FilteredDomainObserver
  │
  ├─ security_audit.py      📋 SecurityAudit (реагирует на ВСЕ)
  │  └─ Записывает логи в audit.log
  │
  └─ backorder_service.py   🎯 BackorderService (только DELETED)
     └─ Проверяет заявки на удаляемые домены
     └─ Использует FilteredDomainObserver

tests/
  ├─ test_domain_registry.py  🚀 Основная демонстрация (Этап 3)
  │  └─ Все тестовые сценарии
  │
  └─ unit_tests.py            🧪 Unit-тесты
     └─ Тесты для каждого компонента


╔════════════════════════════════════════════════════════════════════════════╗
║                       ОСНОВНЫЕ КОНЦЕПЦИИ                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

🎯 ПАТТЕРН OBSERVER (Наблюдатель)
   ├─ Subject: DomainRegistry
   ├─ Observer: DomainObserver (абстрактный интерфейс)
   └─ Конкретные наблюдатели: Whois, Billing, Audit, Backorder

🔧 ПРИНЦИП ИНВЕРСИИ ЗАВИСИМОСТЕЙ
   ├─ DomainRegistry зависит от DomainObserver (абстракция)
   ├─ НЕ зависит от конкретных сервисов
   └─ Новые сервисы добавляются без изменения реестра

🛡️ ОБРАБОТКА ОШИБОК
   ├─ Если один наблюдатель выбросит исключение
   ├─ Остальные всё равно получат уведомление
   └─ Используется try-except в _notify_observers()

🎚️ ФИЛЬТРАЦИЯ СОБЫТИЙ
   ├─ FilteredDomainObserver поддерживает фильтрацию
   ├─ BillingService только на REGISTERED
   └─ BackorderService только на DELETED


╔════════════════════════════════════════════════════════════════════════════╗
║                       ТЕСТОВЫЕ СЦЕНАРИИ                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Сценарий 1️⃣  РЕГИСТРАЦИЯ домена google.kz
  → Billing выставляет счет ✅
  → Whois публикует информацию ✅
  → Audit записывает в лог ✅
  → Backorder проверяет заявки ✅

Сценарий 2️⃣  ОБНОВЛЕНИЕ DNS для google.kz
  → Billing НЕ реагирует (фильтр) ❌
  → Whois обновляет информацию ✅
  → Audit записывает в лог ✅
  → Backorder НЕ реагирует ❌

Сценарий 3️⃣  УДАЛЕНИЕ домена google.kz
  → Billing НЕ реагирует ❌
  → Whois обновляет статус на INACTIVE ✅
  → Audit записывает в лог ✅
  → Backorder запускает аукцион (есть заявки!) ✅


╔════════════════════════════════════════════════════════════════════════════╗
║                       ФАЙЛЫ СОЗДАВАЕМЫЕ ПРИ ЗАПУСКЕ                       ║
╚════════════════════════════════════════════════════════════════════════════╝

audit.log  📋 Файл с историей всех действий (создается при запуске)
  └─ Содержит запись каждого события с временем и деталями


Для получения подробной информации смотрите README.md
    """
    print(help_text)


def main():
    """Главная функция программы."""
    while True:
        choice = print_menu()
        
        if choice == '1':
            run_demo()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            view_audit_log()
        elif choice == '4':
            clear_audit_log()
        elif choice == '5':
            show_help()
        elif choice == '6':
            print("\n👋 До свидания!")
            sys.exit(0)
        else:
            print("\n❌ Некорректный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
