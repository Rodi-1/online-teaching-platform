# Unit-тесты — Сводка

## ✅ Статус: Все Unit-тесты работают

---

## Статистика по сервисам

| Сервис | Unit-тестов | Статус |
|--------|-------------|--------|
| **gradebook-service** | 7 | ✅ Passed |
| **tests-service** | 10 | ✅ Passed |
| **schedule-service** | 7 | ✅ Passed |
| **reports-service** | 8 | ✅ Passed |
| **notifications-service** | 3 | ✅ Passed |
| **profile-service** | 3 | ✅ Passed |
| **homework-service** | 4 | ✅ Passed |
| **ИТОГО** | **42** | ✅ **Passed** |

---

## Что тестируют Unit-тесты

### gradebook-service (7 тестов)
Тестирование метода `calculate_grade()`:
- ✅ Оценка 5 (≥90%)
- ✅ Оценка 4 (75-89%)
- ✅ Оценка 3 (60-74%)
- ✅ Оценка 2 (<60%)
- ✅ Ошибка при отрицательном score
- ✅ Ошибка при score > max_score
- ✅ Ошибка при max_score ≤ 0

### tests-service (10 тестов)
Тестирование методов `_calculate_grade()` и `_check_answer()`:
- ✅ Расчёт оценок (5, 4, 3, 2)
- ✅ Проверка single_choice (правильный/неправильный)
- ✅ Проверка multiple_choice (правильный/неправильный)
- ✅ Проверка text ответа
- ✅ Ответ без эталона (manual grading)

### schedule-service (7 тестов)
Тестирование методов `_check_teacher_or_admin()` и `_validate_dates()`:
- ✅ Роль teacher разрешена
- ✅ Роль admin разрешена
- ✅ Роль student запрещена
- ✅ Неизвестная роль запрещена
- ✅ Валидные даты
- ✅ Ошибка если end_at < start_at
- ✅ Ошибка если end_at == start_at

### reports-service (8 тестов)
Тестирование методов `_check_teacher_or_admin()`, `_generate_file_path()`, `_build_download_url()`:
- ✅ Роли teacher/admin/manager разрешены
- ✅ Роль student запрещена
- ✅ Генерация пути для PDF
- ✅ Генерация пути для XLSX
- ✅ Построение URL скачивания

### notifications-service (3 теста)
Тестирование метода `mark_notification_read()`:
- ✅ Владелец может отметить прочитанным
- ✅ Не-владелец получает 403
- ✅ Несуществующее уведомление — 404

### profile-service (3 теста)
Тестирование метода `create_achievement()`:
- ✅ Успешное создание
- ✅ Дубликат вызывает ошибку
- ✅ Пропуск проверки дубликата

### homework-service (4 теста)
Тестирование методов `grade_submission()` и `create_homework()`:
- ✅ Score > max_score — ошибка
- ✅ Отрицательный score — ошибка
- ✅ Submission не найден — 404
- ✅ Due date в прошлом — ошибка

---

## Запуск тестов

### Запуск unit-тестов для одного сервиса:
```powershell
cd services/gradebook-service
python -m pytest tests/unit/ -v
```

### Запуск всех unit-тестов:
```powershell
# gradebook-service
cd services/gradebook-service; python -m pytest tests/unit/ -v; cd ../..

# tests-service  
cd services/tests-service; python -m pytest tests/unit/ -v; cd ../..

# schedule-service
cd services/schedule-service; python -m pytest tests/unit/ -v; cd ../..

# И так далее...
```

---

## Отличие от интеграционных тестов

| Критерий | Unit-тесты | Интеграционные тесты |
|----------|-----------|---------------------|
| **Что тестируют** | Бизнес-логику изолированно | API endpoints целиком |
| **База данных** | Не требуется (моки) | SQLite in-memory |
| **HTTP-запросы** | Нет | TestClient (FastAPI) |
| **Скорость** | Очень быстро (~0.1s) | Медленнее (~3s) |
| **Зависимости** | Замоканы | Реальные |

---

## Архитектура unit-тестов

```
tests/
├── conftest.py           # Фикстуры для интеграционных тестов
├── test_api_*.py         # Интеграционные тесты API
└── unit/
    ├── __init__.py
    └── test_*_service.py # Unit-тесты бизнес-логики
```

---

*Дата обновления: 02.12.2025*
