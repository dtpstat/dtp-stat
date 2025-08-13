from django.db import models

class ManualPost(models.Model):
    class Meta:
        verbose_name = 'Ручной постинг'
        verbose_name_plural = 'Ручной постинг'

class RegularPost(models.Model):
    class Meta:
        verbose_name = 'Регулярный постинг'
        verbose_name_plural = 'Регулярный постинг'
