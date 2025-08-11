from django.db import models
from django.utils import timezone


class GoalManager(models.Manager):
    def active_goal(self):
        """Returns a queryset of all goals that are currently active."""
        today = timezone.now().date()
        return self.get_queryset().filter(start_date__lte=today, end_date__gte=today).first()
