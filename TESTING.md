# 🧪 Testing Guide

Этот документ описывает стратегию тестирования проекта и инструкции по запуску тестов.

## 📊 Текущее состояние тестов

### ✅ Реализовано

| Сервис | Unit Tests | Integration Tests | Coverage |
|--------|-----------|-------------------|----------|
| **user-service** | ✅ 2 теста | ✅ ~15-20 тестов | 🟡 Medium |
| **homework-service** | ✅ 2 теста | ✅ ~10-15 тестов | 🟡 Medium |
| **gradebook-service** | ✅ 2 теста | ✅ ~10-15 тестов | 🟡 Medium |
| **profile-service** | ✅ 2 теста | ✅ ~10-15 тестов | 🟡 Medium |
| **notifications-service** | ✅ 2 теста | ✅ ~10-15 тестов | 🟡 Medium |
| **tests-service** | ✅ 2 теста | ✅ ~10-15 тестов | 🟡 Medium |
| **schedule-service** | ✅ 2 теста | ✅ ~15-20 тестов | 🟡 Medium |
| **reports-service** | ✅ 2 теста | ✅ ~18-20 тестов | 🟡 Medium |

**Всего:** ~16 unit тестов + ~130 integration тестов = **~146 тестов**

## 🏗️ Структура тестов

Каждый сервис имеет следующую структуру:

```
services/<service-name>/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures (db, client, auth)
├── unit/                    # Unit-тесты (новое!)
│   ├── __init__.py
│   └── test_*_service.py    # Тесты бизнес-логики
└── test_api_*.py            # Integration тесты API endpoints
```

## 🚀 Запуск тестов

### Локально для одного сервиса

```bash
# Перейти в директорию сервиса
cd services/user-service

# Установить зависимости
pip install -r requirements.txt

# Запустить все тесты
pytest

# Запустить только unit тесты
pytest tests/unit/

# Запустить только integration тесты
pytest tests/test_api_*.py

# С coverage отчетом
pytest --cov=app --cov-report=html --cov-report=term

# Открыть HTML отчет
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### Запуск всех тестов для всех сервисов

```bash
# Из корневой директории проекта
for service in user-service homework-service gradebook-service profile-service \
                notifications-service tests-service schedule-service reports-service; do
  echo "Testing $service..."
  cd services/$service
  pytest -v
  cd ../..
done
```

### Запуск через Docker Compose (TODO)

```bash
# Будет добавлено позже
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🤖 CI/CD Pipeline

### GitHub Actions CI

Конфигурация: `.github/workflows/ci.yml`

**Триггеры:**
- Push в ветки `main`, `develop`
- Pull Request в `main`, `develop`

**Что делает:**
1. ✅ Запускает **все 8 сервисов параллельно** (matrix strategy)
2. ✅ Проверяет код с помощью:
   - **flake8** (синтаксис и стиль)
   - **black** (форматирование)
   - **isort** (сортировка импортов)
3. ✅ Запускает **все тесты** (unit + integration)
4. ✅ Генерирует **coverage отчеты**
5. ✅ Загружает coverage в **Codecov**

**Пример запуска локально для проверки:**

```bash
# Из любого сервиса
cd services/user-service

# Linting
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
black --check app
isort --check-only app

# Tests
pytest -v --cov=app --cov-report=xml --cov-report=term-missing
```

### Как посмотреть результаты CI

1. Перейти на GitHub в раздел **Actions**
2. Выбрать workflow **"CI - Lint and Test All Services"**
3. Посмотреть статус каждого сервиса в matrix
4. При ошибке - кликнуть на сервис и посмотреть логи

## 📝 Типы тестов

### 1. Unit Tests (`tests/unit/`)

**Что тестируют:**
- Бизнес-логику в изоляции
- Service слой с mock репозиториями
- Валидацию данных
- Обработку ошибок

**Пример:**

```python
def test_create_homework_validates_due_date():
    """Test that create_homework validates due date is in future"""
    mock_repo = Mock()
    service = HomeworksService(mock_repo)
    
    past_date = datetime.utcnow() - timedelta(days=1)
    homework_data = HomeworkCreate(
        title="Test", 
        due_at=past_date
    )
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_homework(...)
    
    assert exc_info.value.status_code == 400
```

### 2. Integration Tests (`tests/test_api_*.py`)

**Что тестируют:**
- HTTP endpoints через TestClient
- Полный flow: API → Service → Repository → DB
- Авторизацию и роли
- Статус коды и форматы ответов

**Пример:**

```python
def test_create_homework_success(client, teacher_token):
    """Test successful homework creation"""
    response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == homework_data["title"]
```

### 3. E2E Tests (TODO - не реализовано)

**Что будут тестировать:**
- Взаимодействие между сервисами
- Полные пользовательские сценарии
- Работу с реальной PostgreSQL в Docker

**Планируемая структура:**

```
tests/
├── e2e/
│   ├── test_homework_workflow.py
│   ├── test_schedule_workflow.py
│   └── test_reports_workflow.py
```

## 🎯 Рекомендации по написанию тестов

### DO ✅

- ✅ Используйте понятные имена тестов: `test_what_when_expected`
- ✅ Следуйте паттерну AAA: **Arrange → Act → Assert**
- ✅ Mock внешние зависимости в unit тестах
- ✅ Используйте fixtures из `conftest.py`
- ✅ Проверяйте не только success cases, но и error cases
- ✅ Изолируйте тесты друг от друга

### DON'T ❌

- ❌ Не используйте реальную БД в unit тестах
- ❌ Не делайте тесты зависимыми друг от друга
- ❌ Не тестируйте фреймворк (FastAPI, SQLAlchemy)
- ❌ Не делайте слишком большие тесты (один тест = одна проверка)

## 📈 Следующие шаги

### Краткосрочные (1-2 недели)
1. ⏳ Увеличить coverage до 80%+ для всех сервисов
2. ⏳ Добавить больше unit тестов для repository слоя
3. ⏳ Настроить pre-commit hooks

### Среднесрочные (1 месяц)
4. ⏳ Создать E2E тесты для критичных workflow
5. ⏳ Добавить contract тесты между сервисами
6. ⏳ Настроить Docker Compose для тестирования

### Долгосрочные (2-3 месяца)
7. ⏳ Performance тесты (Locust)
8. ⏳ Security тесты (Bandit, Safety)
9. ⏳ Mutation testing (mutmut)

## 🔧 Troubleshooting

### Тесты падают локально, но проходят в CI

```bash
# Проверьте версию Python
python --version  # Должна быть 3.11

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall

# Очистите pytest cache
pytest --cache-clear
```

### Coverage не генерируется

```bash
# Убедитесь что pytest-cov установлен
pip install pytest-cov

# Проверьте что coverage.xml создается
ls -la coverage.xml
```

### Import ошибки в тестах

```bash
# Убедитесь что запускаете из директории сервиса
pwd  # Должно быть .../services/<service-name>

# Или установите PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📚 Полезные ссылки

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Последнее обновление:** 01.12.2025

