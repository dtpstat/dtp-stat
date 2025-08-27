from django.db import models

class RegularPost(models.Model):
    class Meta:
        verbose_name = 'Регулярный пост'
        verbose_name_plural = 'Регулярные посты'

    def __str__(self) -> str:
        return f'Регулярный пост #{self.pk}'
