# СТРУКТУРА И КРАТКОЕ ОПИСАНИЕ

## Архитектура системы (паттерн Observer)

```
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN REGISTRY (Subject)                  │
│  • Управляет жизненным циклом доменов                          │
│  • Уведомляет наблюдателей об изменениях                       │
│  • Не знает о деталях работы наблюдателей                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓ notify()
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
    ┌─────────┐        ┌─────────┐        ┌──────────┐
    │ WHOIS   │        │ BILLING │        │ AUDIT    │
    │ SERVICE │        │ SERVICE │        │ SERVICE  │
    └─────────┘        └─────────┘        └──────────┘
    Реагирует          Реагирует только   Реагирует
    на ВСЕ             на REGISTERED      на ВСЕ
                       (с фильтром)       
         ↓
    ┌──────────────┐
    │ BACKORDER    │
    │ SERVICE      │
    └──────────────┘
    Реагирует только
    на DELETED
    (с фильтром)
```

---

## Быстрый старт для новичков

### 1. Главный класс: DomainRegistry

```python
from core import DomainRegistry, Domain

# Создаем реестр
registry = DomainRegistry()

# Регистрируем домен → рассылаются события
domain = Domain("example.kz", "owner@example.kz", ["ns1.com"])
registry.register(domain)

# Обновляем DNS → рассылаются события
registry.update_dns("example.kz", ["ns1.new.com"])

# Удаляем домен → рассылаются события
registry.delete("example.kz")
```

### 2. Наблюдатели подписываются на события

```python
from observers import WhoisService, BillingService

whois = WhoisService()
billing = BillingService()

registry.subscribe(whois)      # Получит ВСЕ события
registry.subscribe(billing)    # Получит только REGISTERED
```

### 3. События автоматически доставляются

```
registry.register(domain)
    ↓
_notify_observers(DomainEvent(...))
    ↓
whois.update(event)    ✅ реагирует
billing.update(event)  ✅ реагирует (это регистрация)
audit.update(event)    ✅ реагирует
backorder.update(event) ❌ не реагирует (интересует только удаление)
```

---

## Ответы на частые вопросы

### Q: Зачем нужны наблюдатели?
**A:** Когда случается событие (регистрация домена), автоматически выполняются зависимые действия (выставление счета, запись в лог, проверка заявок), БЕЗ жесткой связи.

### Q: Почему это лучше, чем прямые вызовы?
**A:**
```python
# ❌ ПЛОХО: Жесткая связь
class DomainRegistry:
    def register(self, domain):
        billing = BillingService()
        audit = SecurityAudit()
        billing.issue_invoice()
        audit.log_event()
        # Если добавить нового сервиса, нужно менять этот класс!

# ✅ ХОРОШО: Observer Pattern
class DomainRegistry:
    def register(self, domain):
        self._notify_observers(event)
        # Добавляются новые сервисы БЕЗ изменения этого класса!
```

### Q: Что такое фильтрация?
**A:** BillingService реагирует только на регистрацию, а BackorderService только на удаление.
```python
class BillingService(FilteredDomainObserver):
    def __init__(self):
        super().__init__(subscribed_events=[EventType.DOMAIN_REGISTERED])
```

### Q: Что если наблюдатель выбросит исключение?
**A:** Остальные всё равно получат событие (обработка в try-except)
```python
def _notify_observers(self, event):
    for observer in self._observers:
        try:
            observer.update(event)  # Если ошибка здесь...
        except Exception as e:
            logger.error(f"Error: {e}")
            # ...остальные всё равно получат событие
```

---

## Краткий словарь терминов

| Термин | Значение |
|--------|----------|
| **Subject** | Объект, за которым следят (DomainRegistry) |
| **Observer** | Объект, который следит за изменениями (BillingService, etc) |
| **Event** | Информация об изменении (DomainEvent) |
| **Notify** | Разослать уведомления (broadcast) |
| **Subscribe** | Подписаться на уведомления (добавить в список) |
| **Unsubscribe** | Отписаться от уведомлений (удалить из списка) |
| **Coupling** | Связь между классами (нужно минимизировать) |
| **Inversion of Dependencies** | Высокоуровневые модули не зависят от низкоуровневых |

---

## Пример: как работает фильтрация?

```
registry.register(domain) 
    ↓
DomainEvent(type=REGISTERED, ...)
    ↓
_notify_observers(event)
    ↓
    ├─ whois.update(event)
    │    └─ is_interested() → True → handle_event() → выполнить
    │
    ├─ billing.update(event)
    │    └─ is_interested() → True (интересует REGISTERED) → handle_event() → выполнить
    │
    ├─ audit.update(event)
    │    └─ is_interested() → True → handle_event() → выполнить
    │
    └─ backorder.update(event)
         └─ is_interested() → False (интересует только DELETED) → пропустить
```

---

## Тестирование системы

### Основной тестовый сценарий
```bash
python tests/test_domain_registry.py
```

Проверяет:
1. ✅ Регистрация домена
2. ✅ Обновление DNS
3. ✅ Удаление домена  
4. ✅ Обработка ошибок
5. ✅ Содержимое audit.log

### Unit-тесты
```bash
python -m unittest tests.unit_tests -v
```

Проверяет:
- Создание доменов ✅
- Операции реестра ✅
- Уведомление наблюдателей ✅
- Фильтрацию событий ✅
- Отписку ✅
- Логирование ✅

---

## Файлы, которые нужно изучить (по порядку)

1. **README.md** — Полная документация проекта
2. **core/domain.py** — Структура данных Domain
3. **core/events.py** — Типы событий
4. **core/observer.py** — Интерфейсы наблюдателей
5. **core/registry.py** — Главный класс системы (САМЫЙ ВАЖНЫЙ)
6. **observers/whois_service.py** — Простой наблюдатель
7. **observers/billing_service.py** — Наблюдатель с фильтрацией
8. **observers/security_audit.py** — Логирование в файл
9. **observers/backorder_service.py** — Сложная бизнес-логика
10. **tests/test_domain_registry.py** — Демонстрация всего вместе
11. **tests/unit_tests.py** — Все тесты

---

## Проверочный список перед сдачей

- [ ] Я понимаю, что такое паттерн Observer
- [ ] Я понимаю, почему нужна инверсия зависимостей
- [ ] Я запустил основной тестовый сценарий
- [ ] Я запустил unit-тесты и они все прошли
- [ ] Я читал audit.log и понял, как туда пишутся события
- [ ] Я вижу, что BillingService реагирует только на регистрацию
- [ ] Я вижу, что BackorderService реагирует только на удаление
- [ ] Я понимаю, как добавить нового Observer'а
- [ ] Я знаю, что делать, если Observer выбросит исключение
- [ ] Я можу объяснить весь код словами

---

## Если что-то не понятно

1. **Запустите демонстрацию** — увидите реальный вывод
2. **Посмотрите на выводы функций** — добавьте print()
3. **Отредактируйте код** — экспериментируйте
4. **Прочитайте комментарии** — они объясняют логику
5. **Спросите у преподавателя** — это нормально

