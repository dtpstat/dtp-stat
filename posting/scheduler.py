from django_q.tasks import schedule

from .socials.socials import socials

def schedule_task(planned_post):
    """
    Ставит задачу через django-q на указанное время.
    Возвращает ID задачи (str).
    """

    task = schedule(
        'posting.sheduler.publish_post', # Путь к функции, которая отправит пост
        planned_post.id,
        schedule_type='O', # One-off
        next_run=planned_post.effective_datetime,
        hook="posting.planned_post.status_hook"
    )
    return str(task.id) if task else None

def publish_post(planned_post_id):
    from .planned_post import PlannedPost
    
    post = PlannedPost.objects.get(pk=planned_post_id)
    social = post.account.social_network
    
    print(f"Публикуем пост {post.short} в {post.account}")

    try:
        result = socials[social].send(post)
        post.status = 'success'
        
    except Exception as e:
        post.status = 'failed'
        result = e
    
    post.save(update_fields=['status'])
    print(result)