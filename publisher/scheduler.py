from django_q.tasks import schedule as q_schedule

def schedule_task(planned_post):
    """
    Ставит задачу через django-q на указанное время.
    Возвращает объект Schedule (или None).
    """
    job = q_schedule(
        'publisher.scheduler.publish_post',
        args=[planned_post.id],
        schedule_type='O',                # One-off
        next_run=planned_post.effective_datetime,
        hook='publisher.scheduler.status_hook',
        name=f'publish-post:{planned_post.id}',  # helps avoid duplicates
        timeout=60
    )
    if job:
        # persist schedule id for later management (cancel/reschedule)
        planned_post.schedule_id = job.id
        planned_post.save(update_fields=['schedule_id'])
    return job or None

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
    post_id = task.args[0] if getattr(task, 'args', None) else None  # мы в задачу передали post_id
    if post_id is None:
        return  # мы в задачу передали post_id
    
    try:
        post = PlannedPost.objects.get(id=post_id)
    except PlannedPost.DoesNotExist:
        return

    post.task_id = task.id
    
    if not task.success:
        post.status = "uncaughtError"
    post.save()