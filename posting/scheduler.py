from django_q.tasks import schedule

def schedule_task(planned_post):
    """
    Ставит задачу через django-q на указанное время.
    Возвращает ID задачи (str).
    """

    task = schedule(
        'posting.scheduler.publish_post', # Путь к функции, которая отправит пост
        planned_post.id,
        schedule_type='O', # One-off
        next_run=planned_post.effective_datetime,
        hook="posting.planned_post.status_hook"
    )
    return str(task.id) if task else None

def publish_post(planned_post_id):
    from .planned_post import PlannedPost
    
    post = PlannedPost.objects.get(pk=planned_post_id)

    result = post.account.social.send(post)
    
    if result.startswith("[ERROR]"):
        post.status = 'failed'
    else:
        post.status = 'success'
    
    post.save()

    return result