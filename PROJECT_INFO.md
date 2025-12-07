# Информация о проекте - Система онлайн-преподавания

> **Общий файл с информацией о проекте для быстрого составления отчёта**

**Дата обновления:** Декабрь 2025  
**Версия:** 1.0.0  
**Статус:** Production Ready

---

## 1. Общее описание

**Название:** Система онлайн-преподавания (Online Teaching Platform)  
**Тип:** Микросервисная платформа для онлайн-обучения  
**Архитектура:** Микросервисная архитектура с REST API  
**Язык:** Python 3.11+  
**Framework:** FastAPI

### Цель проекта
Спроектировать и реализовать систему онлайн-преподавания, состоящую из независимых микросервисов, взаимодействующих друг с другом через REST API.

---

## 2. Технологический стек

### Backend
- **Python 3.11+** - Основной язык разработки
- **FastAPI 0.115.0** - Веб-фреймворк для создания REST API
- **SQLAlchemy 2.0.36** - ORM для работы с базой данных
- **Pydantic 2.9.2** - Валидация и сериализация данных
- **JWT** - Аутентификация и авторизация
- **bcrypt** - Хеширование паролей

### База данных
- **PostgreSQL 15** - Основная СУБД (отдельная БД для каждого сервиса)

### Инфраструктура
- **Docker** - Контейнеризация сервисов
- **Docker Compose** - Оркестрация контейнеров
- **Nginx** - API Gateway / Reverse Proxy (опционально)

### Мониторинг и логирование
- **Prometheus** - Сбор и хранение метрик
- **Grafana** - Визуализация метрик и логов
- **Loki** - Централизованное хранение логов
- **Promtail** - Сборщик логов из Docker контейнеров
- **PostgreSQL Exporter** - Экспорт метрик БД

### Тестирование
- **pytest 8.3.4** - Фреймворк для тестирования
- **httpx 0.27.2** - HTTP-клиент для тестов API
- **pytest-cov** - Покрытие кода тестами

### DevOps
- **GitHub Actions** - CI/CD pipeline
- **Docker Compose** - Multi-container orchestration

---

## 3. Архитектура системы

### 3.1 Общая схема

```
┌─────────────────────────────────────────────────────────┐
│                    КЛИЕНТЫ                              │
│         (Web-браузер, Мобильное приложение)             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              API GATEWAY (Nginx)                         │
│                    Порт: 80                             │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ User Service  │ │   Homework    │ │  Gradebook    │
│   :8001       │ │   Service     │ │   Service     │
│               │ │    :8002      │ │    :8003      │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL                           │
│                    Порт: 5432                           │
│   ┌──────────────┬──────────────┬──────────────┐        │
│   │user_service  │homework_     │gradebook_    │        │
│   │_db           │service_db    │service_db    │        │
│   └──────────────┴──────────────┴──────────────┘        │
│   ┌──────────────┬──────────────┬──────────────┐        │
│   │notifications_│tests_        │schedule_     │        │
│   │service_db    │service_db    │service_db    │        │
│   └──────────────┴──────────────┴──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Слоистая архитектура каждого микросервиса

```
┌─────────────────────────────────────┐
│      API Layer (Routers)            │  ← HTTP endpoints
├─────────────────────────────────────┤
│     Service Layer (Logic)           │  ← Бизнес-логика
├─────────────────────────────────────┤
│   Repository Layer (Data)           │  ← Доступ к данным
├─────────────────────────────────────┤
│      Database (PostgreSQL)          │  ← Хранение данных
└─────────────────────────────────────┘
```

### 3.3 Принципы микросервисной архитектуры

- ✅ **Декомпозиция по бизнес-функциям** - Каждый сервис отвечает за свою доменную область
- ✅ **Независимое развёртывание** - Сервисы могут быть развёрнуты независимо
- ✅ **Изоляция данных** - Каждый сервис имеет собственную базу данных
- ✅ **API-First подход** - Взаимодействие через REST API
- ✅ **Контейнеризация** - Каждый сервис упакован в Docker-контейнер
- ✅ **Единая точка входа** - API Gateway (Nginx)

---

## 4. Реализованные микросервисы (8 сервисов)

### 4.1 User Service (Сервис пользователей)
**Порт:** 8001 | **База данных:** user_service_db | **Статус:** ✅ Реализован

**Назначение:** Управление пользователями и аутентификация

**Функциональность:**
- Регистрация пользователей (студенты, преподаватели, администраторы)
- Аутентификация с JWT токенами
- Управление профилем пользователя
- Подтверждение email и телефона
- Восстановление пароля
- Административные функции

**API Endpoints:**
- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/logout` - Выход из системы
- `POST /api/users` - Регистрация пользователя
- `GET /api/users/me` - Получить текущего пользователя
- `PATCH /api/users/me` - Обновить профиль
- `POST /api/users/confirm-email` - Подтвердить email
- `POST /api/users/confirm-phone` - Подтвердить телефон
- `POST /api/users:request-password-reset` - Запросить сброс пароля
- `POST /api/users:reset-password` - Сбросить пароль
- `GET /api/users` - Список пользователей (админ)

**Тесты:** 13 integration тестов, 74% coverage

---

### 4.2 Homework Service (Сервис домашних заданий)
**Порт:** 8002 | **База данных:** homework_service_db | **Статус:** ✅ Реализован

**Назначение:** Управление домашними заданиями

**Функциональность:**
- Создание домашних заданий преподавателями
- Управление статусами ДЗ (draft/assigned/closed)
- Отправка решений студентами
- Просмотр решений с контролем доступа
- Выставление оценок преподавателями
- Интеграция с Gradebook Service

**API Endpoints:**
- `POST /api/courses/{course_id}/homeworks` - Создать ДЗ
- `GET /api/courses/{course_id}/homeworks` - Список ДЗ по курсу
- `GET /api/students/me/homeworks` - Мои домашние задания
- `POST /api/homeworks/{homework_id}/submissions` - Отправить решение
- `GET /api/homeworks/{homework_id}/submissions/{submission_id}` - Просмотр решения
- `POST /api/homeworks/{homework_id}/submissions/{submission_id}:grade` - Выставить оценку

**Тесты:** ~10-15 integration тестов

---

### 4.3 Gradebook Service (Сервис электронного журнала)
**Порт:** 8003 | **База данных:** gradebook_service_db | **Статус:** ✅ Реализован

**Назначение:** Электронный журнал и оценки

**Функциональность:**
- Запись оценок за домашние задания и тесты
- Просмотр оценок студента с фильтрами
- Журнал по курсу для преподавателей
- Автоматический расчёт процентов и оценок (5-балльная система)

**API Endpoints:**
- `POST /api/gradebook/homework` - Записать оценку за ДЗ
- `POST /api/gradebook/tests` - Записать оценку за тест
- `GET /api/students/{student_id}/grades` - Оценки студента
- `GET /api/courses/{course_id}/gradebook` - Журнал курса

**Тесты:** 7 unit тестов, ~10-15 integration тестов

---

### 4.4 Profile Service (Сервис профилей)
**Порт:** 8004 | **База данных:** profile_service_db | **Статус:** ✅ Реализован

**Назначение:** Профили и достижения пользователей

**Функциональность:**
- Хранение и выдача профиля пользователя (аватар, описание, ссылки)
- Хранение и выдача достижений (ачивок)
- Обновление базовой статистики прогресса

**API Endpoints:**
- `GET /api/profile/me` - Получить свой профиль
- `PATCH /api/profile/me` - Обновить профиль
- `GET /api/profile/users/{user_id}/achievements` - Достижения пользователя
- `POST /api/profile/users/{user_id}/achievements` - Выдать достижение
- `POST /api/profile/users/{user_id}/stats:update` - Обновить статистику

**Тесты:** 3 unit теста, ~10-15 integration тестов

---

### 4.5 Notifications Service (Сервис уведомлений)
**Порт:** 8005 | **База данных:** notifications_service_db | **Статус:** ✅ Реализован

**Назначение:** Система уведомлений

**Функциональность:**
- Хранение уведомлений для пользователей
- Получение списка уведомлений
- Пометка уведомлений как прочитанных
- Подсчёт непрочитанных уведомлений
- Приём запросов от других сервисов

**Типы уведомлений:** homework, test, schedule, achievement, system

**API Endpoints:**
- `GET /api/notifications/me` - Мои уведомления
- `POST /api/notifications/{id}/read` - Отметить прочитанным
- `POST /api/notifications:mark-all-read` - Прочитать все
- `GET /api/notifications/me/unread-count` - Количество непрочитанных
- `POST /api/notifications` - Создать уведомление

**Тесты:** 3 unit теста, ~10-15 integration тестов

---

### 4.6 Tests Service (Сервис тестов)
**Порт:** 8006 | **База данных:** tests_service_db | **Статус:** ✅ Реализован

**Назначение:** Тесты и экзамены

**Функциональность:**
- Создание и публикация тестов преподавателями
- Хранение структуры теста и вопросов
- Старт попытки прохождения теста
- Приём и автопроверка ответов
- Хранение результатов попыток

**Типы вопросов:** single_choice, multiple_choice, text, number

**API Endpoints:**
- `POST /api/courses/{course_id}/tests` - Создать тест
- `POST /api/tests/{test_id}:publish` - Опубликовать тест
- `POST /api/tests/{test_id}/attempts:start` - Начать попытку
- `POST /api/tests/{test_id}/attempts/{id}/submit` - Отправить ответы
- `GET /api/tests/{test_id}/attempts/{id}` - Результат попытки
- `GET /api/tests/{test_id}/attempts` - Список попыток

**Тесты:** 10 unit тестов, ~10-15 integration тестов

---

### 4.7 Schedule Service (Сервис расписания)
**Порт:** 8007 | **База данных:** schedule_service_db | **Статус:** ✅ Реализован

**Назначение:** Расписание занятий

**Функциональность:**
- Хранение и управление занятиями (уроками)
- Выдача расписания для пользователя
- Выдача расписания по курсу
- Фиксация и просмотр посещаемости

**API Endpoints:**
- `POST /api/courses/{course_id}/lessons` - Создать занятие
- `PATCH /api/lessons/{lesson_id}` - Изменить занятие
- `GET /api/lessons/{lesson_id}` - Информация о занятии
- `GET /api/schedule/me` - Моё расписание
- `GET /api/courses/{course_id}/schedule` - Расписание курса
- `POST /api/lessons/{lesson_id}/attendance` - Отметить посещаемость
- `GET /api/lessons/{lesson_id}/attendance` - Посещаемость занятия

**Тесты:** 7 unit тестов, ~15-20 integration тестов

---

### 4.8 Reports Service (Сервис отчётов)
**Порт:** 8008 | **База данных:** reports_service_db | **Статус:** ✅ Реализован

**Назначение:** Отчёты и аналитика

**Функциональность:**
- Генерация отчётов (асинхронно)
- Хранение метаданных операций
- Хранение готовых отчётов
- Получение ссылок для скачивания
- Перегенерация отчётов

**Типы отчётов:** course_performance, student_progress, attendance  
**Форматы:** PDF, XLSX

**API Endpoints:**
- `POST /api/reports:generate` - Запустить генерацию
- `GET /api/reports/operations/{id}` - Статус операции
- `GET /api/reports` - Список отчётов
- `GET /api/reports/{id}` - Информация об отчёте
- `GET /api/reports/{id}/download` - Ссылка для скачивания
- `POST /api/reports/{id}:regenerate` - Перегенерировать

**Тесты:** 8 unit тестов, ~18-20 integration тестов

---

## 5. Структура проекта

```
online-teaching-platform/
├── services/                          # Все микросервисы
│   ├── user-service/                  # Сервис пользователей
│   ├── homework-service/              # Сервис домашних заданий
│   ├── gradebook-service/             # Сервис электронного журнала
│   ├── profile-service/               # Сервис профилей
│   ├── notifications-service/         # Сервис уведомлений
│   ├── tests-service/                 # Сервис тестов
│   ├── schedule-service/              # Сервис расписания
│   └── reports-service/               # Сервис отчётов
│
├── common/                            # Общие библиотеки
│   ├── libs/                          # Общие питоновские модули
│   └── proto/                         # gRPC схемы (если будет)
│
├── infra/                             # Инфраструктура
│   ├── db/
│   │   └── init.sql                   # Инициализация БД
│   ├── nginx/
│   │   └── nginx.conf                 # Конфигурация API Gateway
│   ├── prometheus/
│   │   └── prometheus.yml            # Конфигурация Prometheus
│   ├── loki/
│   │   └── loki-config.yml           # Конфигурация Loki
│   ├── promtail/
│   │   └── promtail-config.yml        # Конфигурация Promtail
│   └── grafana/
│       ├── datasources.yml            # Источники данных
│       ├── dashboards.yml             # Конфигурация дашбордов
│       ├── dashboard-services.json    # Дашборд микросервисов
│       └── dashboard-postgres.json    # Дашборд PostgreSQL
│
├── docker-compose.yml                 # Оркестрация контейнеров
├── .env                               # Переменные окружения
├── .gitignore
└── .github/
    └── workflows/
        ├── ci.yml                     # CI pipeline
        └── cd.yml                     # CD pipeline
```

### Структура каждого микросервиса:

```
service-name/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── endpoints.py          # HTTP endpoints
│   │   └── dependencies.py            # Зависимости для авторизации
│   ├── core/
│   │   ├── config.py                  # Конфигурация
│   │   ├── security.py                # JWT и безопасность
│   │   ├── logging_config.py          # Настройка логирования
│   │   └── metrics.py                 # Prometheus метрики
│   ├── db/
│   │   └── session.py                 # Сессии БД
│   ├── models/
│   │   ├── db_models.py               # ORM модели
│   │   └── schemas.py                 # Pydantic схемы
│   ├── repositories/
│   │   └── repo.py                    # Работа с БД
│   ├── services/
│   │   └── service.py                 # Бизнес-логика
│   └── main.py                         # Точка входа FastAPI
├── tests/                             # Тесты
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_api_*.py                  # Integration тесты
│   └── unit/                          # Unit-тесты
│       └── test_*_service.py
├── Dockerfile                         # Docker-образ
├── requirements.txt                   # Зависимости
└── README.md                          # Документация
```

---

## 6. Инфраструктура

### 6.1 Docker Compose

Все сервисы оркестрируются через Docker Compose. Конфигурация включает:

- **PostgreSQL** — общая база данных с отдельными БД для каждого сервиса
- **8 микросервисов** — каждый в своём контейнере
- **Nginx** — API Gateway (опционально)
- **Prometheus** — сбор метрик
- **Grafana** — визуализация
- **Loki** — хранение логов
- **Promtail** — сбор логов
- **PostgreSQL Exporter** — метрики БД
- **Сеть** — изолированная bridge-сеть `app-network`
- **Volumes** — постоянное хранилище для БД, метрик и логов

### 6.2 База данных

Для каждого микросервиса создаётся:
- Отдельная база данных
- Отдельный пользователь с ограниченными правами

| Сервис | База данных | Пользователь |
|--------|-------------|--------------|
| User Service | user_service_db | user_service |
| Homework Service | homework_service_db | homework_service |
| Gradebook Service | gradebook_service_db | gradebook_service |
| Profile Service | profile_service_db | profile_service |
| Notifications Service | notifications_service_db | notifications_service |
| Tests Service | tests_service_db | tests_service |
| Schedule Service | schedule_service_db | schedule_service |
| Reports Service | reports_service_db | reports_service |

### 6.3 API Gateway (Nginx)

Nginx выступает как единая точка входа для всех API запросов:
- Маршрутизация запросов к соответствующим сервисам
- Проксирование заголовков
- Health check endpoint

---

## 7. Мониторинг и логирование

### 7.1 Архитектура мониторинга

```
Микросервисы → /metrics endpoint
       ↓
  Prometheus (сбор каждые 15 сек)
       ↓
    Grafana (визуализация)
```

### 7.2 Компоненты

**Prometheus** (http://localhost:9090)
- Сбор метрик с 8 микросервисов
- Сбор метрик PostgreSQL через exporter
- Интервал сбора: 15 секунд

**Grafana** (http://localhost:3000, admin/admin)
- Визуализация метрик и логов
- Источники данных: Prometheus, Loki
- Предустановленные дашборды:
  - Microservices Overview
  - PostgreSQL Database Monitoring

**Loki** (http://localhost:3100)
- Централизованное хранение логов
- Retention: 7 дней
- Индексация по labels

**Promtail**
- Сбор логов из Docker контейнеров
- Парсинг JSON логов
- Отправка в Loki

**PostgreSQL Exporter** (http://localhost:9187)
- Экспорт метрик PostgreSQL

### 7.3 Метрики

**HTTP метрики (автоматические):**
- `http_requests_total` - Общее количество запросов
- `http_request_duration_seconds` - Время ответа (histogram)
- `http_requests_in_progress` - Активные запросы

**Кастомные метрики приложения:**
- `app_info` - Информация о сервисе
- `db_queries_total` - Счетчик запросов к БД
- `db_query_duration_seconds` - Время выполнения запросов к БД
- `db_connections_active` - Активные подключения к БД
- `business_operations_total` - Счетчик бизнес-операций
- `business_operation_duration_seconds` - Время бизнес-операций

**PostgreSQL метрики:**
- Подключения к БД
- Количество запросов в секунду
- Cache hit ratio
- Transaction rate
- Размер баз данных
- Операции с записями
- Статистика блокировок

### 7.4 Логирование

**Формат:** Структурированный JSON

**Обязательные поля:**
- `timestamp` - время в ISO 8601 (UTC)
- `level` - уровень (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service` - имя микросервиса
- `logger` - имя логгера
- `module`, `function`, `line` - информация о месте вызова
- `message` - сообщение

**Дополнительные поля:**
- `request_id` - уникальный ID запроса для трейсинга
- `user_id` - ID пользователя
- `method`, `path` - HTTP метод и путь
- `status_code` - HTTP статус код
- `duration_ms` - длительность выполнения
- `error`, `exception` - информация об ошибках

**Поток логов:**
```
Микросервисы → stdout/stderr (Docker)
       ↓
    Promtail (сбор из Docker)
       ↓
     Loki (хранение и индексация)
       ↓
   Grafana (поиск и визуализация)
```

---

## 8. Тестирование

### 8.1 Статистика тестов

| Сервис | Unit Tests | Integration Tests | Coverage |
|--------|-----------|-------------------|----------|
| user-service | - | 13 | 74% |
| homework-service | 4 | ~10-15 | Medium |
| gradebook-service | 7 | ~10-15 | Medium |
| profile-service | 3 | ~10-15 | Medium |
| notifications-service | 3 | ~10-15 | Medium |
| tests-service | 10 | ~10-15 | Medium |
| schedule-service | 7 | ~15-20 | Medium |
| reports-service | 8 | ~18-20 | Medium |
| **ИТОГО** | **42** | **~130** | - |

### 8.2 Типы тестов

**Unit-тесты:**
- Тестирование бизнес-логики изолированно
- Используют моки вместо реальных зависимостей
- Быстрое выполнение

**Integration тесты:**
- Тестирование API endpoints через HTTP-запросы
- Используют TestClient (FastAPI) и SQLite in-memory
- Проверяют полный цикл: запрос → бизнес-логика → БД → ответ

### 8.3 Запуск тестов

**Для одного сервиса:**
```powershell
cd services/user-service
python -m pip install -r requirements.txt
python -m pytest tests/ -v
```

**Для всех сервисов:**
```powershell
.\run_all_tests.ps1
```

---

## 9. Безопасность

### 9.1 Аутентификация
- **JWT токены** для идентификации пользователей
- Токен передаётся в заголовке `Authorization: Bearer <token>`
- Настраиваемое время жизни токена

### 9.2 Авторизация
- **Role-Based Access Control (RBAC)**
- Роли: student, teacher, admin, manager
- Проверка прав на уровне API endpoints

### 9.3 Защита данных
- Хеширование паролей с bcrypt
- Валидация всех входных данных через Pydantic
- Защита от SQL-инъекций через SQLAlchemy ORM
- Переменные окружения для секретов
- CORS конфигурация

---

## 10. Запуск проекта

### 10.1 Быстрый старт

```bash
# Клонировать репозиторий
git clone <repository-url>
cd online-teaching-platform

# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps
```

### 10.2 Доступ к сервисам

| Сервис | URL | Документация API |
|--------|-----|------------------|
| User Service | http://localhost:8001 | http://localhost:8001/docs |
| Homework Service | http://localhost:8002 | http://localhost:8002/docs |
| Gradebook Service | http://localhost:8003 | http://localhost:8003/docs |
| Profile Service | http://localhost:8004 | http://localhost:8004/docs |
| Notifications Service | http://localhost:8005 | http://localhost:8005/docs |
| Tests Service | http://localhost:8006 | http://localhost:8006/docs |
| Schedule Service | http://localhost:8007 | http://localhost:8007/docs |
| Reports Service | http://localhost:8008 | http://localhost:8008/docs |

### 10.3 Инфраструктура

| Сервис | URL | Credentials |
|--------|-----|-------------|
| PostgreSQL | localhost:5432 | postgres/postgres123 |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Loki | http://localhost:3100 | - |
| PostgreSQL Exporter | http://localhost:9187 | - |

### 10.4 Полезные команды

**Docker Compose:**
```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Просмотр логов
docker compose logs -f [service-name]

# Пересборка
docker compose up -d --build

# Статус
docker compose ps
```

**Тестирование:**
```bash
# Запуск тестов одного сервиса
cd services/user-service
pytest -v

# Запуск всех тестов
.\run_all_tests.ps1
```

---

## 11. CI/CD Pipeline

### 11.1 Continuous Integration (CI)

Файл: `.github/workflows/ci.yml`

**Этапы:**
1. Линтинг (flake8, black, isort)
2. Unit-тесты (pytest + моки)
3. Integration тесты (pytest + TestClient)

**Триггеры:**
- Push в ветки `main`, `develop`
- Pull Request в ветки `main`, `develop`

### 11.2 Continuous Deployment (CD)

Файл: `.github/workflows/cd.yml`

**Этапы:**
1. Запуск тестов (unit + integration)
2. Сборка Docker образов
3. Деплой на production

**Триггеры:**
- Push в ветку `main`
- Ручной запуск (workflow_dispatch)

---

## 12. Взаимодействие между сервисами

### 12.1 Схема взаимодействия

```
User Service ← JWT токен → Все сервисы

Homework Service → Оценка за ДЗ → Gradebook Service

Tests Service → Обновление статистики → Profile Service

Все сервисы → Уведомление → Notifications Service

Gradebook/Schedule → Данные для отчётов → Reports Service
```

### 12.2 Примеры интеграций

1. **Homework → Gradebook:** При выставлении оценки за ДЗ она автоматически записывается в журнал
2. **Tests → Profile:** После прохождения теста обновляется статистика в профиле
3. **Все сервисы → Notifications:** Создание уведомлений о событиях

---

## 13. Статистика проекта

### 13.1 Общая статистика

- **Микросервисов:** 8
- **API endpoints:** ~60+
- **ORM моделей:** 20+
- **Pydantic схем:** 100+
- **Тестов:** ~172 (42 unit + ~130 integration)
- **Строк кода:** ~15000+
- **Docker контейнеров:** 13 (8 сервисов + 5 инфраструктурных)

### 13.2 Технологии

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL 15
- **Infrastructure:** Docker, Docker Compose, Nginx
- **Monitoring:** Prometheus, Grafana, Loki, Promtail
- **Testing:** pytest, httpx
- **CI/CD:** GitHub Actions

---

## 14. Полезные команды

### 14.1 Docker

```bash
# Запуск всех сервисов
docker compose up -d

# Остановка
docker compose down

# Просмотр логов
docker compose logs -f [service-name]

# Пересборка
docker compose up -d --build

# Выполнение команды в контейнере
docker compose exec user-service bash
```

### 14.2 База данных

```bash
# Подключение к PostgreSQL
docker compose exec postgres psql -U postgres -d online_teaching

# Backup БД
docker compose exec postgres pg_dump -U postgres online_teaching > backup.sql
```

### 14.3 Тестирование

```bash
# Тесты одного сервиса
cd services/user-service
pytest -v

# Тесты с coverage
pytest --cov=app --cov-report=html

# Все тесты
.\run_all_tests.ps1
```

### 14.4 Мониторинг

```bash
# Проверка метрик сервиса
curl http://localhost:8001/metrics

# Проверка Prometheus targets
curl http://localhost:9090/api/v1/targets

# Просмотр логов в JSON
docker logs user-service | head -5
```

---

## 15. Заключение

Проект **"Система онлайн-преподавания"** успешно реализован с полностью работающими 8 микросервисами.


- ✅ **8 микросервисов** с чётко разделённой ответственностью
- ✅ **REST API** для каждого сервиса с автодокументацией (Swagger)
- ✅ **Единая база данных PostgreSQL** с изолированными БД
- ✅ **Docker-контейнеризация** всех компонентов
- ✅ **Docker Compose** для оркестрации
- ✅ **API Gateway** на базе Nginx
- ✅ **JWT-аутентификация** и RBAC-авторизация
- ✅ **Два вида тестов**: Unit-тесты (42 шт.) и Интеграционные тесты (~130 шт.)
- ✅ **CI/CD Pipeline** с автоматическим запуском тестов
- ✅ **Layered Architecture** в каждом сервисе
- ✅ **Мониторинг и логирование** (Prometheus, Grafana, Loki)


---

*Дата создания: Декабрь 2025*  
*Дисциплина: Микросервисная архитектура*  
*Версия: 1.0.0*

