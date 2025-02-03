from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_seating, name='create_seating'),
    path('preview/<int:pk>/', views.preview_seating, name='preview_seating'),
    path('download_pdf/<int:pk>/', views.download_pdf, name='download_pdf'),
    path('register/', views.register, name='register'),  # New registration route
    path('add_branch/', views.add_branch, name='add_branch'),
    path('add_semester/', views.add_semester, name='add_semester'),
    path('delete_branch/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('delete_semester/<int:semester_id>/', views.delete_semester, name='delete_semester'),    
]



