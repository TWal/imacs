from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from datetime import timedelta
from random import random

def none_to_zero(x):
    return x if x is not None else 0

def compute_minute_per_day(tasks):
    result = tasks.aggregate(minute_per_day=models.Sum((1.0*models.F('duration'))/models.F('period')))
    return none_to_zero(result['minute_per_day'])

def compute_duration(tasks):
    result = tasks.aggregate(duration=models.Sum('duration'))
    return none_to_zero(result['duration'])

class TaskList(models.Model):
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name
    def get_name(self):
        return self.name
    def get_absolute_url(self):
        return reverse('imacs_app:task_list_todo', kwargs={'task_list_id': self.pk})

    def minute_per_day(self):
        return compute_minute_per_day(Task.objects.filter(task_category__task_list = self))
    def hour_per_week(self):
        return self.minute_per_day()*7/60
    def hour_per_week_per_user(self):
        return self.hour_per_week()/self.users.count()

    def minute_done_since(self, delta):
        tasks = Task.objects.filter(task_category__task_list = self, taskdone__when__gte = timezone.now() - delta).distinct()
        return compute_duration(tasks)

    def minute_done_since_last_week(self):
        return self.minute_done_since(timedelta(days=7))

    def hour_done_since_last_week(self):
        return self.minute_done_since_last_week()/60

    def remaining_hours_this_week(self):
        return max(0, self.hour_per_week() - self.hour_done_since_last_week())

    def minutes_for_user(self, user):
        return compute_duration(Task.objects.filter(task_category__task_list = self, tasked_user = user))

class TaskCategory(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.task_list) + "/" + self.name
    def get_name(self):
        return self.name
    def get_absolute_url(self):
        return reverse('imacs_app:task_category_modify', kwargs={'task_category_id': self.pk})

    def minute_per_day(self):
        return compute_minute_per_day(self.task_set)

class Task(models.Model):
    task_category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(validators=[MinValueValidator(0)]) # in minutes
    period = models.IntegerField(validators=[MinValueValidator(1)]) # in days
    tasked_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    def clean(self):
        if self.tasked_user:
            if self.tasked_user not in self.task_category.task_list.users.all():
                raise ValidationError('Tasked user is not allowed to view the task')

    def __str__(self):
        return str(self.task_category) + "/" + self.name
    def get_name(self):
        return self.name
    def get_absolute_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.pk})

    def get_random_taskdone(self):
        return TaskDone(task=self, when = timezone.now() - timedelta(days=random()*self.period))

    def last_done(self):
        try:
            return self.taskdone_set.order_by('-when')[0].when
        except IndexError:
            return None
    def priority(self):
        last_done = self.last_done()
        if last_done == None:
            return float("inf")
        else:
            delta = timezone.now()-last_done
            return (delta.days + (delta.seconds/24/3600))/self.period

class TaskDone(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    when = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True) # in minutes
