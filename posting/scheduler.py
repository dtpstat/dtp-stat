from django_q.tasks import schedule
from django.utils.timezone import make_aware

def schedule_task(planned_post):
    """
    Ставит задачу через django-q на указанное время.
    Возвращает ID задачи (str).
    """
    # Приводим дату к aware (с учётом таймзоны)
    run_time = planned_post.datetime_planned
    if run_time.tzinfo is None:
        run_time = make_aware(run_time)

    task = schedule(
        'posting.publish.publish_post', # Путь к функции, которая отправит пост
        planned_post.id,
        schedule_type='O', # One-off
        next_run=run_time,
        hook="posting.planned_post.status_hook"
    )
    return str(task.id) if task else None
