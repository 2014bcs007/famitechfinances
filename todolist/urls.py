from django.urls import path
from . import views

urlpatterns = [
    path('', views.task,name='task'),
    path('taskdetails/<str:pk>', views.taskDetail,name='taskdetails'),
    path('taskcreate', views.taskCreate,name='taskcreate'),
    path('taskupdate/<str:pk>',views.taskUpdate,name='taskupdate'),
    path('taskdelete/<str:pk>',views.taskDelete,name='taskdelete'),
    
]