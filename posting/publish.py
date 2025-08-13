def publish_post(planned_post_id):
    from posting.planned_post import PlannedPost
    
    post = PlannedPost.objects.get(pk=planned_post_id)
    # здесь логика отправки поста в соцсеть
    print(f"Публикуем пост {post.short} в {post.target}")
    # можно обновить статус поста, если хочешь
