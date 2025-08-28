from django.db import models

class RegularPost(models.Model):
    class Meta:
        verbose_name = 'Регулярный постинг'
        verbose_name_plural = 'Регулярный постинг'

    def __str__(self) -> str:
        return f'Регулярный пост #{self.pk}'
