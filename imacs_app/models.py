from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class TaskList(models.Model):
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name
    def get_name(self):
        return self.name
    def get_absolute_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.pk})

    def minute_per_day(self):
        tasks = Task.objects.filter(task_category__task_list = self)
        result = tasks.aggregate(minute_per_day=models.Sum((1.0*models.F('duration'))/models.F('period')))
        return result['minute_per_day']

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
        tasks = self.task_set
        result = tasks.aggregate(minute_per_day=models.Sum((1.0*models.F('duration'))/models.F('period')))
        return result['minute_per_day']

class Task(models.Model):
    task_category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(validators=[MinValueValidator(0)]) # in minutes
    period = models.IntegerField(validators=[MinValueValidator(1)]) # in days
    tasked_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    def clean(self):
        if self.tasked_user:
            if self.tasked_user not in self.task_category.task_list.users:
                raise ValidationError('Tasked user is not allowed to view the task')

    def __str__(self):
        return str(self.task_category) + "/" + self.name
    def get_name(self):
        return self.name
    def get_absolute_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.pk})


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
