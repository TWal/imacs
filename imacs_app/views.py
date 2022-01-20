from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.forms import models as model_forms
from django import forms
from django.contrib import auth
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from .models import TaskList, TaskCategory, Task, TaskDone

class UserCanViewTaskListMixin(UserPassesTestMixin):
    def test_func(self):
        task_id = self.kwargs['task_list_id']
        return TaskList.objects.filter(pk=task_id, users=self.request.user).exists()

class UserCanViewTaskCategoryMixin(UserPassesTestMixin):
    def test_func(self):
        task_category_id = self.kwargs['task_category_id']
        return TaskCategory.objects.filter(pk=task_category_id, task_list__users=self.request.user).exists()

class UserCanViewTaskMixin(UserPassesTestMixin):
    def test_func(self):
        task_id = self.kwargs['task_id']
        return Task.objects.filter(pk=task_id, task_category__task_list__users=self.request.user).exists()

class UserCanViewTaskDoneMixin(UserPassesTestMixin):
    def test_func(self):
        task_done_id = self.kwargs['task_done_id']
        return TaskDone.objects.filter(pk=task_done_id, task__task_category__task_list__users=self.request.user).exists()

class TaskListList(generic.ListView):
    template_name = 'imacs_app/task_list_list.html'
    context_object_name = 'task_lists'
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return TaskList.objects.filter(users=self.request.user)
        else:
            return []

class TaskListCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = TaskList
    template_name = 'imacs_app/task_list_create.html'
    fields = ['name']
    def form_valid(self, form):
        #TODO: there may be a better way to do it?
        response = super().form_valid(form)
        self.object.users.add(self.request.user)
        self.object.save()
        return response

class MultipleFormsMixin(generic.base.ContextMixin):
    active_form_keyword = "selected_form"
    form_classes = []

    def get_initial(self, form_id):
        return None

    def get_prefix(self, form_id):
        return None

    def get_success_url(self, active_form_id):
        return None

    def get_form_classes(self):
        return self.form_classes

    def get_active_form_id(self):
        if self.request.method in ('POST', 'PUT'):
            try:
                return self.request.POST[self.active_form_keyword]
            except KeyError:
                raise ImproperlyConfigured("You must include hidden field with form_id in every form!")

    def get_form_kwargs(self, form_id, fill_with_request=False):
        kwargs = {
            'initial': self.get_initial(form_id),
            'prefix': self.get_prefix(form_id),
        }
        if self.request.method in ('POST', 'PUT') and fill_with_request:
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_forms(self, active_invalid_form=None):
        all_form_classes = self.get_form_classes()
        all_forms = {form_id: form_class(**self.get_form_kwargs(form_id)) for (form_id, form_class) in all_form_classes.items()}
        if active_invalid_form is not None:
            active_form_id = self.get_active_form_id()
            if active_form_id is not None:
                all_forms[active_form_id] = active_invalid_form
        return all_forms

    def get_form(self):
        active_form_id = self.get_active_form_id()
        if active_form_id is not None:
            all_forms_classes = self.get_form_classes()
            if active_form_id in all_forms_classes:
                active_form_class = all_forms_classes[active_form_id]
                return active_form_class(**self.get_form_kwargs(active_form_id, fill_with_request=True))

    def get_context_data(self, **kwargs):
        if 'forms' not in kwargs:
            #'active_form' is set by the `form_invalid` function
            kwargs['forms'] = self.get_forms(kwargs.get('active_form'))
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        return HttpResponseRedirect(self.get_success_url(self.get_active_form_id()))

    def form_invalid(self, form):
        """If the form is invalid, re-render the context data with the data-filled forms and errors."""
        return self.render_to_response(self.get_context_data(active_form=form))

class MultipleFormsView(generic.base.TemplateResponseMixin, MultipleFormsMixin, generic.edit.ProcessFormView):
    pass

class TaskListModify(generic.detail.SingleObjectMixin, UserCanViewTaskListMixin, MultipleFormsView):
    class UserForm(forms.Form):
        user = auth.forms.UsernameField()
        def clean_user(self):
            username = self.cleaned_data['user']
            try:
                user = auth.models.User.objects.get(username=username)
            except auth.models.User.DoesNotExist:
                raise forms.ValidationError("User does not exists")
            return user

    model = TaskList
    template_name = 'imacs_app/task_list_modify.html'
    pk_url_kwarg = 'task_list_id'
    fields = ['name']
    context_object_name = 'task_list'
    form_classes = {
        'task_list_name': model_forms.modelform_factory(TaskList, fields=['name']),
        'new_user': UserForm,
        'delete_user': UserForm,
    }

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self, form_id, fill_with_request=False):
        kwargs = super().get_form_kwargs(form_id, fill_with_request)
        if form_id == 'task_list_name':
            kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        active_form_id = self.get_active_form_id()
        if active_form_id == 'task_list_name':
            self.object = form.save()
        elif active_form_id == 'new_user':
            user = form.cleaned_data['user']
            self.object.users.add(user)
            self.object.save()
        elif active_form_id == 'delete_user':
            user = form.cleaned_data['user']
            self.object.users.remove(user)
            self.object.save()
        return super().form_valid(form)

    def get_success_url(self, active_form_id):
        if active_form_id == 'task_list_name':
            return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.id})
        else:
            return reverse('imacs_app:task_list_modify', kwargs={'task_list_id': self.object.id})

class TaskListDelete(UserCanViewTaskListMixin, generic.edit.DeleteView):
    model = TaskList
    template_name = 'imacs_app/task_list_delete.html'
    context_object_name = 'task_list'
    pk_url_kwarg = 'task_list_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_list')


class TaskListTodo(UserCanViewTaskListMixin, generic.ListView):
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

class TaskListSummary(UserCanViewTaskListMixin, generic.DetailView):
    model = TaskList
    template_name = 'imacs_app/task_list_summary.html'
    context_object_name = 'task_list'
    pk_url_kwarg = 'task_list_id'

class TaskCategoryCreate(UserCanViewTaskListMixin, generic.edit.CreateView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_create.html'
    fields = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = get_object_or_404(TaskList, pk=self.kwargs['task_list_id'])
        return context

    def get_success_url(self):
        return reverse('imacs_app:task_list_create_task', kwargs={'task_list_id': self.kwargs['task_list_id']})

    def form_valid(self, form):
        form.instance.task_list_id = self.kwargs['task_list_id']
        return super().form_valid(form)

class TaskCategoryModify(UserCanViewTaskCategoryMixin, generic.edit.UpdateView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_modify.html'
    pk_url_kwarg = 'task_category_id'
    fields = ['name']
    context_object_name = 'task_category'

    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_list.id})

class TaskCategoryDelete(UserCanViewTaskCategoryMixin, generic.edit.DeleteView):
    model = TaskCategory
    template_name = 'imacs_app/task_category_delete.html'
    context_object_name = 'task_category'
    pk_url_kwarg = 'task_category_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_list.id})

def task_model_form_factory(task_list_id, include_random_completion_checkbox):
    class TheForm(model_forms.ModelForm):
        task_category = forms.ModelChoiceField(queryset=TaskCategory.objects.filter(task_list__pk=task_list_id))
        tasked_user = forms.ModelChoiceField(queryset=auth.models.User.objects.filter(tasklist__pk=task_list_id), required=False)
        class Meta:
            model = Task
            fields = ['task_category', 'name', 'duration', 'period', 'description', 'tasked_user']
    class TheForm2(TheForm):
        add_random_completion = forms.BooleanField(required=False, initial=True)
    return TheForm2 if include_random_completion_checkbox else TheForm

class TaskCreate(UserCanViewTaskListMixin, generic.edit.CreateView):
    template_name = 'imacs_app/task_create.html'

    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.kwargs['task_list_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_list_id = self.kwargs['task_list_id']
        task_list = get_object_or_404(TaskList, pk=task_list_id)
        context['task_list'] = task_list
        return context

    def form_valid(self, form):
        #TODO: there may be a better way to do it?
        response = super().form_valid(form)
        if form.cleaned_data['add_random_completion']:
            self.object.get_random_taskdone().save()
        return response

    def get_form_class(self):
        return task_model_form_factory(self.kwargs['task_list_id'], True)

class TaskModify(UserCanViewTaskMixin, generic.edit.UpdateView):
    model = Task
    template_name = 'imacs_app/task_modify.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        task_dones = task.taskdone_set.order_by("-when")
        context['task_dones'] = task_dones
        return context

    def get_form_class(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        return task_model_form_factory(task.task_category.task_list.pk, False)

class TaskDelete(UserCanViewTaskMixin, generic.edit.DeleteView):
    model = Task
    template_name = 'imacs_app/task_delete.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    def get_success_url(self):
        return reverse('imacs_app:task_list_summary', kwargs={'task_list_id': self.object.task_category.task_list.id})

def task_modify_tasked_user_form_factory(task_list_id):
    class TheForm(model_forms.ModelForm):
        tasked_user = forms.ModelChoiceField(queryset=auth.models.User.objects.filter(tasklist__pk=task_list_id), required=False)
        class Meta:
            model = Task
            fields = ['tasked_user']
    return TheForm

class TaskModifyTaskedUser(UserCanViewTaskMixin, generic.edit.UpdateView):
    model = Task
    template_name = 'imacs_app/task_modify_tasked_user.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_form_class(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        return task_modify_tasked_user_form_factory(task.task_category.task_list.pk)

    def get_success_url(self):
        return reverse('imacs_app:task_list_todo', kwargs={'task_list_id': self.object.task_category.task_list.id})

class TaskDoneAddNow(UserCanViewTaskMixin, generic.edit.CreateView):
    model = TaskDone
    template_name = 'imacs_app/task_add_done_now.html'
    fields = ['duration']
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = get_object_or_404(Task, pk=self.kwargs['task_id'])
        return context

    def get_success_url(self):
        return reverse('imacs_app:task_list_todo', kwargs={'task_list_id': self.object.task.task_category.task_list.id})

    def form_valid(self, form):
        # TODO is there a better way to do this?
        form.instance.task_id = self.kwargs['task_id']
        response = super().form_valid(form)
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        task.tasked_user = None
        task.save()
        return response

class TaskDoneAdd(UserCanViewTaskMixin, generic.edit.CreateView):
    model = TaskDone
    template_name = 'imacs_app/task_add_done.html'
    fields = ['when', 'duration']
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = get_object_or_404(Task, pk=self.kwargs['task_id'])
        return context

    def get_success_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.object.task.id})

    def form_valid(self, form):
        form.instance.task_id = self.kwargs['task_id']
        return super().form_valid(form)

class TaskDoneAddRandom(UserCanViewTaskMixin, generic.detail.SingleObjectMixin, generic.edit.FormView):
    model = Task
    template_name = 'imacs_app/task_done_add_random.html'
    pk_url_kwarg = 'task_id'
    form_class = forms.Form # Empty form

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.object.id})

    def form_valid(self, form):
        self.object.get_random_taskdone().save()
        return super().form_valid(form)

class TaskDoneDelete(UserCanViewTaskDoneMixin, generic.edit.DeleteView):
    model = TaskDone
    template_name = 'imacs_app/task_done_delete.html'
    context_object_name = 'task_done'
    pk_url_kwarg = 'task_done_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_done'] = get_object_or_404(TaskDone, pk=self.kwargs['task_done_id'])
        return context

    def get_success_url(self):
        return reverse('imacs_app:task_modify', kwargs={'task_id': self.object.task.id})
