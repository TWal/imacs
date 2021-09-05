from django.contrib import admin

from .models import TaskList, TaskCategory, Task, TaskDone

admin.site.register(TaskList)
admin.site.register(TaskCategory)
admin.site.register(Task)
admin.site.register(TaskDone)
