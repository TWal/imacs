from django.urls import path, include

from . import views
import django.contrib.auth.views as auth_views

app_name = 'imacs_app'
urlpatterns = [
    path('', views.TaskListList.as_view(), name='task_list_list'),
    path('task_list/create', views.TaskListCreate.as_view(), name='task_list_create'),
    path('task_list/<int:task_list_id>/summary', views.TaskListSummary.as_view(), name='task_list_summary'),
    path('task_list/<int:task_list_id>/todo', views.TaskListTodo.as_view(), name='task_list_todo'),
    path('task_list/<int:task_list_id>/modify', views.TaskListModify.as_view(), name='task_list_modify'),
    path('task_list/<int:task_list_id>/my_tasks', views.TaskListMyTasks.as_view(), name='task_list_my_tasks'),
    path('task_list/<int:task_list_id>/delete', views.TaskListDelete.as_view(), name='task_list_delete'),
    path('task_list/<int:task_list_id>/create_task', views.TaskCreate.as_view(), name='task_list_create_task'),
    path('task_list/<int:task_list_id>/create_category', views.TaskCategoryCreate.as_view(), name='task_list_create_task_category'),
    path('task_category/<int:task_category_id>/modify', views.TaskCategoryModify.as_view(), name='task_category_modify'),
    path('task_category/<int:task_category_id>/delete', views.TaskCategoryDelete.as_view(), name='task_category_delete'),
    path('task/<int:task_id>/modify', views.TaskModify.as_view(), name='task_modify'),
    path('task/<int:task_id>/modify_tasked_user', views.TaskModifyTaskedUser.as_view(), name='task_modify_tasked_user'),
    path('task/<int:task_id>/delete', views.TaskDelete.as_view(), name='task_delete'),
    path('task/<int:task_id>/add_done_now', views.TaskDoneAddNow.as_view(), name='task_done_add_now'),
    path('task/<int:task_id>/add_done', views.TaskDoneAdd.as_view(), name='task_done_add'),
    path('task/<int:task_id>/add_done_random', views.TaskDoneAddRandom.as_view(), name='task_done_add_random'),
    path('task_done/<int:task_done_id>/delete', views.TaskDoneDelete.as_view(), name='task_done_delete'),

    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
]

