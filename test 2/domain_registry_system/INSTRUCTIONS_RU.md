# ИНСТРУКЦИЯ ДЛЯ СТУДЕНТОВ

## Как начать работу с проектом?

### Шаг 1: Ознакомление с проектом
1. Прочитайте файл `README.md` — там описана вся архитектура
2. Посмотрите на структуру папок в `domain_registry_system/`
3. Поймите, для чего нужен каждый файл

### Шаг 2: Запуск демонстрации

#### Вариант А: Через интерактивное меню
```bash
cd domain_registry_system
python run.py
```
Выберите пункт 1 "Запустить демонстрацию"

#### Вариант Б: Напрямую запустить сценарий
```bash
cd domain_registry_system
python tests/test_domain_registry.py
```

**Что вы увидите:**
- 📦 Инициализация системы
- 🎯 Регистрация домена → реагируют все сервисы
- 🔄 Обновление DNS → Billing игнорирует, остальные реагируют
- 🎯 Удаление домена → BackorderService запускает аукцион
- 📋 Содержимое audit.log

### Шаг 3: Запуск тестов

```bash
cd domain_registry_system
python tests/unit_tests.py
```

или с pytest:
```bash
pytest tests/unit_tests.py -v
```

**Должно выполниться ~20+ тестов и все должны быть ✅**

### Шаг 4: Просмотр аудит-лога

```bash
# Через меню
python run.py  # Выберите пункт 3

# Или напрямую
type audit.log  # Windows
cat audit.log   # Linux/Mac
```

---

## Как понять код?

### 1️⃣ Начните с `core/registry.py`
Это сердце системы. Обратите внимание на:
- Метод `subscribe()` — добавление наблюдателя
- Метод `_notify_observers()` — разсылка событий
- Обработка исключений (try-except)

### 2️⃣ Посмотрите на `core/observer.py`
Здесь определены два интерфейса:
- `DomainObserver` — базовый интерфейс
- `FilteredDomainObserver` — с фильтрацией событий

### 3️⃣ Изучите наблюдателей в `observers/`
- `WhoisService` — самый простой (реагирует на все)
- `BillingService` — использует фильтрацию
- `SecurityAudit` — пишет в файл
- `BackorderService` — самый сложный (логика бизнеса)

### 4️⃣ Посмотрите на `tests/test_domain_registry.py`
Здесь показан весь сценарий использования системы

---

## Что нужно будет написать на экзамене?

### Вариант 1: Если экзамен — это код
Вам, вероятно, попросят:
1. **Создать новый Observer** — например, `EmailNotificationService`
   ```python
   class EmailNotificationService(DomainObserver):
       def update(self, event: DomainEvent) -> None:
           # Отправить email владельцу домена
           pass
   ```

2. **Добавить новый тип события** — например, `DOMAIN_RENEWED`
   ```python
   class EventType(Enum):
       DOMAIN_RENEWED = "domain_renewed"
   ```

3. **Расширить функциональность DomainRegistry** — например, метод `renew()`

### Вариант 2: Если экзамен — это вопросы
Подготовьтесь ответить на:
- Что такое паттерн Observer?
- Почему DomainRegistry не знает о BillingService?
- Как работает фильтрация событий?
- Что произойдет, если один Observer выбросит исключение?
- Как добавить нового Observer'а?

---

## Типичные ошибки (избегайте их!)

### ❌ ОШИБКА 1: Жесткая связь
```python
# НЕПРАВИЛЬНО:
class DomainRegistry:
    def register(self, domain):
        billing = BillingService()
        billing.issue_invoice()
```

Правильно использовать Observer'ов через `_observers`

### ❌ ОШИБКА 2: Нет обработки исключений
```python
# НЕПРАВИЛЬНО:
def _notify_observers(self, event):
    for observer in self._observers:
        observer.update(event)  # Если здесь ошибка, остальные не получат событие!
```

Правильно обернуть в try-except

### ❌ ОШИБКА 3: Нет Type Hinting
```python
# НЕПРАВИЛЬНО:
def register(self, domain):  # Что за domain? Строка? Объект?
    pass

# ПРАВИЛЬНО:
def register(self, domain: Domain) -> None:
    pass
```

### ❌ ОШИБКА 4: Observer зависит от конкретного Event'а
```python
# НЕПРАВИЛЬНО:
class BillingService(DomainObserver):
    def update(self, event):
        if isinstance(event, DomainRegisteredEvent):  # Жесткая связь!
            pass

# ПРАВИЛЬНО:
class BillingService(FilteredDomainObserver):
    def __init__(self):
        super().__init__(subscribed_events=[EventType.DOMAIN_REGISTERED])
```

---

## Дополнительные задания

Если хотите получить оценку выше, попробуйте:

### 1. Добавить новый Observer
Создайте свой Observer, например:
```python
class StatisticsService(DomainObserver):
    """Собирает статистику по доменам"""
    def update(self, event: DomainEvent) -> None:
        # Увеличить счетчик регистраций
        # Вычислить среднее количество DNS-серверов
        # и т.д.
        pass
```

### 2. Добавить новый тип события
Например, `DOMAIN_RENEWED` или `DOMAIN_TRANSFERRED`

### 3. Реализовать историю событий
```python
class EventHistory:
    """Сохраняет историю событий для воспроизведения"""
    def record(self, event: DomainEvent) -> None:
        pass
    
    def replay(self, since: datetime) -> List[DomainEvent]:
        pass
```

### 4. Добавить приоритеты Observer'ов
```python
registry.subscribe(billing, priority=1)  # Выполнится первым
registry.subscribe(audit, priority=2)    # Выполнится вторым
```

### 5. Реализовать асинхронные операции
Сделать `update()` асинхронным с использованием `asyncio`

---

## Полезные команды

### Запуск демонстрации
```bash
python tests/test_domain_registry.py
```

### Запуск тестов
```bash
python -m unittest tests.unit_tests -v
python -m pytest tests/unit_tests.py -v
```

### Просмотр аудит-лога
```bash
cat audit.log  # или type audit.log на Windows
```

### Очистка аудит-лога
```bash
rm audit.log  # Linux/Mac
del audit.log # Windows
```

### Интерактивное меню
```bash
python run.py
```

---

## Что дальше?

После того как разберетесь с этим проектом, можно изучить:
1. **Паттерн Mediator** — похож на Observer, но наоборот
2. **Паттерн Pub/Sub** — расширенная версия Observer
3. **Event Bus** — глобальная система событий
4. **Message Queue** (RabbitMQ, Kafka) — асинхронная обработка событий

---

## Вопросы и помощь

Если что-то не понятно:
1. Прочитайте комментарии в коде
2. Запустите демонстрацию и посмотрите на вывод
3. Отредактируйте код и экспериментируйте
4. Обратитесь к преподавателю

**Удачи! 🚀**

