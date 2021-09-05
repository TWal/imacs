from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import TaskList, TaskCategory, Task, TaskDone

class TaskListList(generic.ListView):
    template_name = 'imacs_app/task_list_list.html'
    context_object_name = 'task_lists'
    model = TaskList

class TaskListCreate(generic.edit.CreateView):
    model = TaskList
    template_name = 'imacs_app/task_list_create.html'
    fields = ['name']

class TaskListModify(generic.edit.UpdateView):
    model = TaskList
    template_name = 'imacs_app/task_list_modify.html'
    pk_url_kwarg = 'task_list_id'
    fields = ['name']
    context_object_name = 'task_list'

    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_list.id})

class TaskListDelete(generic.edit.DeleteView):
    model = TaskList
    template_name = 'imacs_app/task_list_delete.html'
    context_object_name = 'task_list'
    pk_url_kwarg = 'task_list_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_list')


class TaskListTodo(generic.ListView):
    template_name = 'imacs_app/task_list_todo.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        task_list_id = self.kwargs['task_list_id']
        self.task_list = get_object_or_404(TaskList, pk=task_list_id)
        tasks = Task.objects.filter(task_category__task_list__id = task_list_id).all()
        return sorted(tasks, key=lambda x: x.priority(), reverse=True)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = self.task_list
        return context

class TaskListSummary(generic.DetailView):
    model = TaskList
    template_name = 'imacs_app/task_list_summary.html'
    context_object_name = 'task_list'
    pk_url_kwarg = 'task_list_id'

class TaskCategoryCreate(generic.edit.CreateView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_create.html'
    fields = ['name']

    def get_success_url(self):
        return reverse('imacs_app:task_list_create_task', kwargs={'task_list_id': self.kwargs['task_list_id']})

    def form_valid(self, form):
        form.instance.task_list_id = self.kwargs['task_list_id']
        return super().form_valid(form)

class TaskCategoryModify(generic.edit.UpdateView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_modify.html'
    pk_url_kwarg = 'task_category_id'
    fields = ['name']
    context_object_name = 'task_category'

    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_list.id})

class TaskCategoryDelete(generic.edit.DeleteView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_delete.html'
    context_object_name = 'task_category'
    pk_url_kwarg = 'task_category_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_list.id})

class TaskCreate(generic.edit.CreateView):
    model = Task
    template_name = 'imacs_app/task_create.html'
    fields = ['task_category', 'name', 'duration', 'period', 'description']

    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.kwargs['task_list_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_list_id = self.kwargs['task_list_id']
        task_list = get_object_or_404(TaskList, pk=task_list_id)
        context['task_list'] = task_list
        return context

class TaskModify(generic.edit.UpdateView):
    model = Task
    template_name = 'imacs_app/task_modify.html'
    context_object_name = 'task'
    fields = ['name', 'duration', 'period', 'description']
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        task_dones = task.taskdone_set.order_by("-when")
        context['task_dones'] = task_dones
        return context

class TaskDelete(generic.edit.DeleteView):
    model = Task
    template_name = 'imacs_app/task_delete.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_category.task_list.id})

class TaskDoneAddNow(generic.edit.CreateView):
    model = TaskDone
    template_name = 'imacs_app/task_add_done_now.html'
    fields = ['duration']
    pk_url_kwarg = 'task_id'

    def get_success_url(self):
        return reverse('imacs_app:task_list_todo', kwargs={'task_list_id': self.object.task.task_category.task_list.id})

    def form_valid(self, form):
        form.instance.task_id = self.kwargs['task_id']
        return super().form_valid(form)

class TaskDoneAdd(generic.edit.CreateView):
    model = TaskDone
    template_name = 'imacs_app/task_add_done.html'
    fields = ['when', 'duration']
    pk_url_kwarg = 'task_id'

    def get_success_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.object.task.id})

    def form_valid(self, form):
        form.instance.task_id = self.kwargs['task_id']
        return super().form_valid(form)


class TaskDoneDelete(generic.edit.DeleteView):
    model = TaskDone
    template_name = 'imacs_app/task_done_delete.html'
    context_object_name = 'task_done'
    pk_url_kwarg = 'task_done_id'
    def get_success_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.object.task.id})

