# Gradebook Service

Микросервис электронного журнала для платформы онлайн-обучения.

## Возможности

- Запись оценок за домашние задания и тесты
- Просмотр оценок студента с фильтрами
- Журнал по курсу для преподавателей
- Автоматический расчет процентов и оценок (5-балльная система)

## API Endpoints

- `POST /api/gradebook/homework` - Записать оценку за ДЗ
- `POST /api/gradebook/tests` - Записать оценку за тест
- `GET /api/students/{student_id}/grades` - Оценки студента
- `GET /api/courses/{course_id}/gradebook` - Журнал курса

## Запуск

```bash
docker-compose up -d gradebook-service
```

API: http://localhost:8003/docs

