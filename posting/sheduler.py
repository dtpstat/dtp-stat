def schedule_task(planned_post):
    """
    Заглушка — здесь интеграция с Celery / cron.
    Должна:
      - запланировать выполнение задачи в planned_post.datetime_planned
      - вернуть идентификатор задачи (строку) или None
    """
    # TODO: интегрируй Celery / django-celery-beat:
    #   - создать celery task, добавить запись в PeriodicTask или очередь отложенной задачи
    #   - вернуть task_id или name
    return None