from django_q.tasks import schedule
from django.utils.timezone import make_aware

def schedule_task(planned_post):
    """
    Ставит задачу через django-q на указанное время.
    Возвращает ID задачи (str).
    """

    task = schedule(
        'posting.publish.publish_post', # Путь к функции, которая отправит пост
        planned_post.id,
        schedule_type='O', # One-off
        next_run=planned_post.effective_datetime,
        hook="posting.planned_post.status_hook"
    )
    return str(task.id) if task else None
