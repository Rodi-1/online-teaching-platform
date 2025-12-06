# 🚀 Как запустить тесты

## ✅ Быстрый старт (для одного сервиса)

### 1. Перейдите в директорию сервиса

```powershell
cd services/user-service
```

### 2. Установите зависимости

```powershell
python -m pip install -r requirements.txt
```

### 3. Запустите тесты

```powershell
# Все тесты
python -m pytest tests/ -v

# С coverage отчетом
python -m pytest tests/ --cov=app --cov-report=term-missing

# С HTML coverage отчетом
python -m pytest tests/ --cov=app --cov-report=html
# Откройте htmlcov/index.html в браузере
```

---

## 📋 Запуск тестов для всех сервисов

### PowerShell скрипт:

```powershell
$services = @(
    "user-service",
    "homework-service",
    "gradebook-service",
    "profile-service",
    "notifications-service",
    "tests-service",
    "schedule-service",
    "reports-service"
)

foreach ($service in $services) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Testing $service..." -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    cd "services\$service"
    python -m pip install -r requirements.txt --quiet
    python -m pytest tests/ -v --tb=short
    $exitCode = $LASTEXITCODE
    cd ..\..
    
    if ($exitCode -ne 0) {
        Write-Host "`n❌ Tests failed for $service" -ForegroundColor Red
    } else {
        Write-Host "`n✅ Tests passed for $service" -ForegroundColor Green
    }
}
```

Сохраните это как `run_all_tests.ps1` и запустите:

```powershell
.\run_all_tests.ps1
```

---

## 🔍 Полезные команды pytest

```powershell
# Показать список тестов без запуска
python -m pytest tests/ --collect-only

# Запустить только тесты auth
python -m pytest tests/test_api_auth.py -v

# Запустить конкретный тест
python -m pytest tests/test_api_auth.py::test_login_success -v

# Показать вывод print()
python -m pytest tests/ -v -s

# Остановить после первой ошибки
python -m pytest tests/ -v -x

# Показать N самых медленных тестов
python -m pytest tests/ --durations=10

# Coverage с указанием минимального порога
python -m pytest tests/ --cov=app --cov-fail-under=70
```

---

## 📊 Текущий статус тестов

| Сервис | Integration Tests | Status |
|--------|------------------|---------|
| **user-service** | 13 тестов | ✅ 74% coverage |
| **homework-service** | ~10-15 тестов | ⏳ Нужно проверить |
| **gradebook-service** | ~10-15 тестов | ⏳ Нужно проверить |
| **profile-service** | ~10-15 тестов | ⏳ Нужно проверить |
| **notifications-service** | ~10-15 тестов | ⏳ Нужно проверить |
| **tests-service** | ~10-15 тестов | ⏳ Нужно проверить |
| **schedule-service** | ~15-20 тестов | ⏳ Нужно проверить |
| **reports-service** | ~18-20 тестов | ⏳ Нужно проверить |

---

## ⚠️ Важные замечания

### 1. Unit-тесты временно отключены

Unit-тесты (в папках `tests/unit/`) были созданы, но не совместимы с текущей архитектурой сервисов. Они требуют переработки и были временно удалены.

**Что нужно для unit-тестов:**
- Сервисы принимают `db: Session`, а не репозитории напрямую
- Нужно либо мокировать SQLAlchemy Session, либо использовать другой подход
- Integration тесты покрывают основную функциональность

### 2. conftest.py был обновлен

В `services/user-service/tests/conftest.py` было внесено изменение:
- Создается тестовое FastAPI приложение **без lifespan**
- Это предотвращает попытку подключения к реальной PostgreSQL
- Используется in-memory SQLite база данных

**Это изменение нужно применить к остальным сервисам!**

### 3. Зависимости

Убедитесь что в `requirements.txt` есть:

```txt
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.27.2
```

---

## 🐛 Troubleshooting

### Ошибка: `psycopg2.OperationalError: connection refused`

**Проблема:** Тесты пытаются подключиться к реальной PostgreSQL.

**Решение:** Обновите `conftest.py` как в `user-service` - создайте тестовое app без lifespan.

### Ошибка: `ImportError: cannot import name 'XXXService'`

**Проблема:** Неправильное имя класса в unit-тестах.

**Решение:** Проверьте реальное имя класса:

```powershell
# Найти класс в сервисе
grep -r "^class.*Service" services/user-service/app/services/
```

### Ошибка: `pip: command not found`

**Решение:** Используйте `python -m pip` вместо `pip`.

### Warning: `asyncio_default_fixture_loop_scope is unset`

**Решение:** Добавьте в `pytest.ini`:

```ini
[pytest]
asyncio_default_fixture_loop_scope = function
```

---

## 🎯 Следующие шаги

1. ✅ **Обновить conftest.py для всех сервисов** (как в user-service)
2. ⏳ Запустить тесты для всех 8 сервисов
3. ⏳ Исправить ошибки если есть
4. ⏳ Создать unit-тесты заново (под текущую архитектуру)
5. ⏳ Довести coverage до 80%+

---

## 📖 Дополнительная документация

- `TESTING.md` - полное руководство по тестированию
- `UNIT_TESTS_SUMMARY.md` - сводка по unit-тестам (требует обновления)
- `.github/workflows/ci.yml` - CI конфигурация

---

**Последнее обновление:** 02.12.2025  
**Статус:** ✅ Integration тесты работают для user-service  
**Требуется:** Проверить остальные 7 сервисов




