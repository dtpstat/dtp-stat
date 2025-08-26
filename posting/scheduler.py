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
        hook="posting.scheduler.status_hook"
    )
    return task if task else None

def publish_post(planned_post_id):
    from .planned_post import PlannedPost
    
    post = PlannedPost.objects.get(pk=planned_post_id)

    result = post.account.social.post(post)
    
    if result.startswith("[ERROR]"):
        post.status = 'caughtError'
    else:
        post.status = 'success'
    
    post.save()

    return result

def status_hook(task):
    from .planned_post import PlannedPost
    
    # task — это объект Task из django_q
    post_id = task.args[0]  # мы в задачу передали post_id
    
    try:
        post = PlannedPost.objects.get(id=post_id)
    except PlannedPost.DoesNotExist:
        return

    post.task_id = task.id
    
    if not task.success:
        post.status = "uncaughtError"
    post.save()