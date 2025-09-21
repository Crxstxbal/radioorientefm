from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    path('users/', views.dashboard_users, name='dashboard_users'),
    path('blog/', views.dashboard_blog, name='dashboard_blog'),
    path('radio/', views.dashboard_radio, name='dashboard_radio'),
    path('chat/', views.dashboard_chat, name='dashboard_chat'),
    path('analytics/', views.dashboard_analytics, name='dashboard_analytics'),
    path('api/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),

    # Bandas Emergentes CRUD
    path('emergentes/', views.dashboard_emergentes, name='dashboard_emergentes'),
    path('emergentes/<int:banda_id>/<str:nuevo_estado>/', views.cambiar_estado_banda, name='cambiar_estado_banda'),
    path('emergentes/<int:banda_id>/eliminar/', views.delete_banda, name='delete_banda'),
    path('emergentes/<int:banda_id>/detalle/', views.view_banda, name='view_banda'),

    
    # User CRUD
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # Blog CRUD
    path('blog/create/', views.create_post, name='create_post'),
    path('blog/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('blog/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    # Radio CRUD
    path('radio/create-program/', views.create_program, name='create_program'),
    path('radio/edit-program/<int:program_id>/', views.edit_program, name='edit_program'),
    path('radio/delete-program/<int:program_id>/', views.delete_program, name='delete_program'),
    path('radio/create-news/', views.create_news, name='create_news'),
    path('radio/delete-news/<int:news_id>/', views.delete_news, name='delete_news'),
    path('radio/update_station/', views.update_station, name='update_station'),

    # Chat Moderation
    path('chat/delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
]

