# Полезные команды для работы с проектом

## Docker Compose команды

### Запуск всех сервисов
```bash
docker-compose up -d
```

### Остановка всех сервисов
```bash
docker-compose down
```

### Остановка с удалением volumes (очистка БД)
```bash
docker-compose down -v
```

### Просмотр статуса сервисов
```bash
docker-compose ps
```

### Просмотр логов всех сервисов
```bash
docker-compose logs -f
```

### Просмотр логов конкретного сервиса
```bash
docker-compose logs -f user-service
docker-compose logs -f postgres
```

### Пересборка образов
```bash
docker-compose build
```

### Пересборка и запуск
```bash
docker-compose up -d --build
```

### Выполнение команды в контейнере
```bash
docker-compose exec user-service bash
docker-compose exec postgres psql -U postgres
```

## Локальная разработка User Service

### Создание виртуального окружения
```bash
cd services/user-service
python -m venv venv
```

### Активация виртуального окружения
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск сервиса локально
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Запуск тестов
```bash
pytest
```

### Запуск тестов с покрытием
```bash
pytest --cov=app --cov-report=html
```

### Запуск конкретного теста
```bash
pytest tests/test_api_auth.py::test_login_success
```

## Форматирование и линтинг

### Black - форматирование кода
```bash
cd services/user-service
black app/
```

### isort - сортировка импортов
```bash
isort app/
```

### flake8 - проверка стиля кода
```bash
flake8 app/
```

### Запуск всех проверок
```bash
black app/ && isort app/ && flake8 app/
```

## Работа с базой данных

### Подключение к PostgreSQL в Docker
```bash
docker-compose exec postgres psql -U postgres -d online_teaching
```

### Список баз данных
```sql
\l
```

### Подключение к базе user_service_db
```sql
\c user_service_db
```

### Список таблиц
```sql
\dt
```

### Просмотр структуры таблицы
```sql
\d users
```

### Выход из psql
```sql
\q
```

## API тестирование с curl

### Health check
```bash
curl http://localhost:8001/health
```

### Регистрация пользователя
```bash
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "phone": "+79990001122",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "role": "student"
  }'
```

### Логин
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Получение профиля (с токеном)
```bash
# Сначала сохраните токен из логина
export TOKEN="your_access_token_here"

curl -X GET http://localhost:8001/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Обновление профиля
```bash
curl -X PATCH http://localhost:8001/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name"
  }'
```

## Git команды

### Инициализация репозитория (если еще не сделано)
```bash
git init
git add .
git commit -m "Initial commit: Complete user service implementation"
```

### Создание .gitignore
```bash
# Уже создан в проекте
```

### Добавление remote repository
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

### Создание новой ветки для фичи
```bash
git checkout -b feature/homework-service
```

### Commit и push изменений
```bash
git add .
git commit -m "Add new feature"
git push origin feature/homework-service
```

## Alembic (миграции базы данных)

### Инициализация Alembic (уже настроено)
```bash
cd services/user-service
alembic init alembic
```

### Создание миграции
```bash
alembic revision --autogenerate -m "Initial migration"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграции
```bash
alembic downgrade -1
```

### История миграций
```bash
alembic history
```

## Мониторинг и отладка

### Просмотр использования ресурсов Docker
```bash
docker stats
```

### Просмотр сетей Docker
```bash
docker network ls
docker network inspect online-teaching-platform_app-network
```

### Просмотр volumes
```bash
docker volume ls
docker volume inspect online-teaching-platform_postgres_data
```

### Очистка неиспользуемых Docker ресурсов
```bash
docker system prune -a
```

### Проверка портов
**Windows:**
```powershell
netstat -ano | findstr :8001
netstat -ano | findstr :5432
```

**Linux/Mac:**
```bash
lsof -i :8001
lsof -i :5432
```

## Production команды

### Сборка production образа
```bash
docker build -t user-service:latest services/user-service/
```

### Запуск в production режиме
```bash
# Измените ENV в .env на "prod"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Backup базы данных
```bash
docker-compose exec postgres pg_dump -U postgres online_teaching > backup.sql
```

### Восстановление базы данных
```bash
docker-compose exec -T postgres psql -U postgres online_teaching < backup.sql
```

## Troubleshooting

### Перезапуск конкретного сервиса
```bash
docker-compose restart user-service
```

### Пересборка одного сервиса
```bash
docker-compose up -d --build user-service
```

### Проверка переменных окружения в контейнере
```bash
docker-compose exec user-service env
```

### Удаление конкретного volume
```bash
docker volume rm online-teaching-platform_postgres_data
```

### Полная очистка Docker
```bash
# ВНИМАНИЕ: Удалит ВСЕ контейнеры, образы, сети и volumes
docker system prune -a --volumes
```

## Полезные алиасы (добавьте в .bashrc или .zshrc)

```bash
# Docker Compose shortcuts
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcrestart='docker-compose restart'

# User Service shortcuts
alias us-logs='docker-compose logs -f user-service'
alias us-test='cd services/user-service && pytest'
alias us-shell='docker-compose exec user-service bash'

# Database shortcuts
alias db-shell='docker-compose exec postgres psql -U postgres -d online_teaching'
alias db-backup='docker-compose exec postgres pg_dump -U postgres online_teaching > backup_$(date +%Y%m%d_%H%M%S).sql'
```

## CI/CD команды (GitHub Actions)

### Локальное тестирование CI
```bash
# Установите act (https://github.com/nektos/act)
act -j lint-and-test-user-service
```

### Проверка синтаксиса workflow файлов
```bash
# Используйте GitHub CLI
gh workflow view ci.yml
```

---

**Совет:** Добавьте этот файл в закладки для быстрого доступа к командам!

