# Система управления доменными именами | Domain Registry System

## 📋 Описание проекта

Это **готовый boilerplate** для лабораторной работы по проектированию системы управления доменными именами на основе паттерна **Observer** (Наблюдатель).

### Основная идея
Регистратура доменов — это «источник истины», но о её действиях должны мгновенно узнавать другие независимые подсистемы (сервисы). Это достигается через применение паттерна Observer.

---

## 🏗️ Структура проекта

```
domain_registry_system/
├── core/                      # Основные классы и интерфейсы
│   ├── __init__.py
│   ├── domain.py              # Класс Domain (хранит данные о домене)
│   ├── events.py              # Типы событий (DomainEvent, EventType)
│   ├── observer.py            # Абстрактные интерфейсы наблюдателей
│   └── registry.py            # Класс DomainRegistry (Subject)
│
├── observers/                 # Реализации наблюдателей (Observers)
│   ├── __init__.py
│   ├── whois_service.py       # Публикует изменения доменов
│   ├── billing_service.py     # Выставляет счета (только при регистрации)
│   ├── security_audit.py      # Записывает логи в файл
│   └── backorder_service.py   # Проверяет заявки на удаляемые домены
│
├── tests/                     # Тесты и демонстрация
│   ├── __init__.py
│   ├── test_domain_registry.py  # Основной тестовый сценарий (Этап 3)
│   └── unit_tests.py            # Unit-тесты для всех компонентов
│
├── README.md                  # Этот файл
└── audit.log                  # Файл с логом событий (создается при запуске)
```

---

## 🎯 Компоненты системы

### 1. **Core модули**

#### `domain.py` - Класс Domain
```python
@dataclass
class Domain:
    name: str              # Имя домена (напр., mysite.kz)
    owner_email: str       # Email владельца
    dns_servers: List[str] # Список DNS-серверов
```

#### `events.py` - События
```python
class EventType(Enum):
    DOMAIN_REGISTERED = "domain_registered"    # Домен зарегистрирован
    DOMAIN_DNS_UPDATED = "domain_dns_updated"  # Обновлены DNS
    DOMAIN_DELETED = "domain_deleted"          # Домен удален

@dataclass
class DomainEvent:
    event_type: EventType
    domain_name: str
    owner_email: str
    timestamp: datetime
    dns_servers: Optional[List[str]]
```

#### `observer.py` - Интерфейсы наблюдателей
```python
class DomainObserver(ABC):
    @abstractmethod
    def update(self, event: DomainEvent) -> None:
        pass

class FilteredDomainObserver(DomainObserver):
    """Поддерживает фильтрацию событий (доп. задание)"""
    def __init__(self, subscribed_events: Optional[List[EventType]] = None):
        self.subscribed_events = subscribed_events
```

#### `registry.py` - Класс DomainRegistry (Subject)
```python
class DomainRegistry:
    def subscribe(self, observer: DomainObserver) -> None
    def unsubscribe(self, observer: DomainObserver) -> None
    def register(self, domain: Domain) -> None          # → уведомление
    def update_dns(self, name: str, new_dns) -> None    # → уведомление
    def delete(self, name: str) -> None                 # → уведомление
    def _notify_observers(self, event: DomainEvent)     # Разослает событие
```

### 2. **Наблюдатели (Observers)**

#### `whois_service.py` - WhoisService ✅
- Реагирует на **ВСЕ** события
- Публикует информацию о домене (имитация Whois сервиса)
- Покажет: регистрацию, обновление DNS, удаление

#### `billing_service.py` - BillingService 💰
- Реагирует **ТОЛЬКО** на `DOMAIN_REGISTERED`
- Выставляет счета владельцам
- Использует фильтрацию `FilteredDomainObserver`

#### `security_audit.py` - SecurityAudit 📋
- Реагирует на **ВСЕ** события
- Записывает в файл `audit.log` историю всех действий
- Формат: `[ВРЕМЯ] ACTION | Domain | Owner | DNS`

#### `backorder_service.py` - BackorderService 🎯
- Реагирует **ТОЛЬКО** на `DOMAIN_DELETED`
- Проверяет, есть ли заявки на удаляемый домен
- Использует фильтрацию `FilteredDomainObserver`

---

## 🚀 Быстрый старт

### 1. Запуск основной демонстрации

```bash
cd domain_registry_system
python tests/test_domain_registry.py
```

**Ожидаемый вывод:**
1. Регистрация `google.kz` → реагируют Billing, Whois, Audit
2. Обновление DNS → Billing игнорирует, остальные сработают
3. Удаление `google.kz` → BackorderService найдет заявки и запустит аукцион

### 2. Запуск Unit-тестов

```bash
cd domain_registry_system
python -m pytest tests/unit_tests.py -v
```

или

```bash
python -m unittest tests.unit_tests -v
```

### 3. Просмотр аудит-лога

```bash
cat audit.log
```

---

## 📝 Основной сценарий (Этап 3)

Файл: `tests/test_domain_registry.py`

```python
# Инициализация
registry = DomainRegistry()
whois = WhoisService()
billing = BillingService()
audit = SecurityAudit()
backorder = BackorderService()

# Подписка
registry.subscribe(whois)
registry.subscribe(billing)
registry.subscribe(audit)
registry.subscribe(backorder)

# Сценарий 1: Регистрация
google = Domain("google.kz", "admin@google.kz", ["ns1.google.com"])
registry.register(google)
# ✅ Billing: выставит счет
# ✅ Whois: опубликует
# ✅ Audit: запишет в лог
# ✅ Backorder: проверит заявки

# Сценарий 2: Обновление DNS
registry.update_dns("google.kz", ["ns1.example.com", "ns2.example.com"])
# ❌ Billing: НЕ реагирует (фильтр работает)
# ✅ Whois: обновит информацию
# ✅ Audit: запишет в лог

# Сценарий 3: Удаление
registry.delete("google.kz")
# ❌ Billing: НЕ реагирует
# ✅ Whois: обновит статус
# ✅ Audit: запишет в лог
# ✅ Backorder: запустит аукцион (есть заявки!)
```

---

## ✅ Критерии оценки

### ✔️ Отсутствие жестких связей
```python
# ❌ НЕПРАВИЛЬНО:
class DomainRegistry:
    def register(self, domain):
        billing = BillingService()      # Жесткая связь!
        billing.process()

# ✅ ПРАВИЛЬНО:
class DomainRegistry:
    def _notify_observers(self, event):
        for observer in self._observers:  # Только список!
            observer.update(event)
```

### ✔️ Типизация (Type Hinting)
```python
def register(self, domain: Domain) -> None: ...
def subscribe(self, observer: DomainObserver) -> None: ...
def _notify_observers(self, event: DomainEvent) -> None: ...
```

### ✔️ Обработка исключений
```python
def _notify_observers(self, event: DomainEvent) -> None:
    for observer in self._observers:
        try:
            observer.update(event)
        except Exception as e:
            logger.error(f"Error notifying {observer}: {e}")
            # Остальные получат уведомление!
```

---

## 🌟 Дополнительное задание (на "отлично")

### Фильтрация событий на стороне наблюдателя

Уже реализовано в `core/observer.py` через класс `FilteredDomainObserver`:

```python
# BillingService реагирует ТОЛЬКО на регистрацию
class BillingService(FilteredDomainObserver):
    def __init__(self):
        super().__init__(subscribed_events=[EventType.DOMAIN_REGISTERED])
    
    def handle_event(self, event: DomainEvent) -> None:
        # Этот метод вызовется только для DOMAIN_REGISTERED
        self._issue_invoice(event)

# BackorderService реагирует ТОЛЬКО на удаление
class BackorderService(FilteredDomainObserver):
    def __init__(self):
        super().__init__(subscribed_events=[EventType.DOMAIN_DELETED])
```

### Альтернативный синтаксис (возможное расширение):
```python
# Вариант подписки на конкретные события:
registry.subscribe(billing, events=[EventType.DOMAIN_REGISTERED])
```

---

## 🧪 Примеры тестов

Файл: `tests/unit_tests.py`

```python
# Тест регистрации
def test_register_domain(self):
    registry.register(domain)
    retrieved = registry.get_domain("test.kz")
    assert retrieved.name == "test.kz"

# Тест фильтрации
def test_filtered_observer_ignores_unsubscribed_events(self):
    billing = BillingService()
    registry.subscribe(billing)
    
    registry.register(domain)      # Billing получит событие
    registry.update_dns(...)       # Billing НЕ получит событие
    
    assert len(billing.events) == 1

# Тест отписки
def test_unsubscribe_observer(self):
    registry.unsubscribe(observer)
    registry.delete("test.kz")
    assert len(observer.events) == 0
```

---

## 📚 Принципы проектирования

### 1. **Observer Pattern (Паттерн Наблюдатель)**
- Subject (`DomainRegistry`) уведомляет Observers об изменениях
- Слабая связанность между компонентами

### 2. **Dependency Inversion Principle**
- `DomainRegistry` зависит от `DomainObserver` (абстракция), а не от конкретных сервисов
- Новые сервисы можно добавлять, не изменяя `DomainRegistry`

### 3. **Single Responsibility Principle**
- `WhoisService` — только публикация
- `BillingService` — только выставление счетов
- `SecurityAudit` — только логирование
- `BackorderService` — только управление заявками

### 4. **Open/Closed Principle**
- Система открыта для расширения (добавления новых Observer'ов)
- Закрыта для модификации (`DomainRegistry` не меняется)

---

## 🔍 Обработка ошибок

### Гарантии надежности:
```python
def _notify_observers(self, event: DomainEvent) -> None:
    """
    Если один наблюдатель выбросит исключение,
    остальные всё равно получат уведомление
    """
    for observer in self._observers:
        try:
            observer.update(event)
        except Exception as e:
            logger.error(f"Error: {e}")
            # Продолжаем цикл!
```

---

## 📖 Что дальше?

### Возможные расширения:
1. **Асинхронные операции** - Сделать `update()` асинхронным
2. **Приоритеты** - Обработать наблюдателей в определенном порядке
3. **Отписка по условию** - Автоматическая отписка при определенных событиях
4. **Событие-ответ** - Наблюдатель может вернуть результат
5. **История событий** - Сохранение всех событий для воспроизведения
6. **Webhook'и** - Отправка событий во внешние системы

---

## 🎓 Для преподавателя

Этот boilerplate содержит:
- ✅ Все необходимые классы и интерфейсы
- ✅ Полную реализацию всех наблюдателей
- ✅ Обработку исключений
- ✅ Type Hinting
- ✅ Фильтрацию событий (доп. задание)
- ✅ Unit-тесты
- ✅ Документацию и примеры

Студентам достаточно:
1. Разобраться с архитектурой
2. Запустить демонстрацию
3. Пройти unit-тесты
4. (Опционально) Добавить свой наблюдатель

---

## 📞 Вопросы и поддержка

При возникновении вопросов обратитесь к преподавателю или создайте issue.

**Удачи в обучении! 🚀**

