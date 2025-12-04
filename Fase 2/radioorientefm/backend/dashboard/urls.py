from django.urls import path
from . import views
from . import publicidad_views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('password-reset/', views.dashboard_password_reset, name='dashboard_password_reset'),

    path('calendario/', views.dashboard_calendario, name='dashboard_calendario'),
    path('api/calendario/eventos/', views.api_get_calendar_events, name='api_get_calendar_events'),

    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    path('users/', views.dashboard_users, name='dashboard_users'),
    path('articulos/', views.dashboard_articulos, name='dashboard_articulos'),
    path('radio/', views.dashboard_radio, name='dashboard_radio'),
    path('conductores/crear/', views.crear_conductor, name='crear_conductor'),
    path('conductores/editar/<int:conductor_id>/', views.editar_conductor, name='editar_conductor'),
    path('conductores/toggle-activo/<int:conductor_id>/', views.toggle_activo_conductor, name='toggle_activo_conductor'),
    path('conductores/eliminar/<int:conductor_id>/', views.eliminar_conductor, name='eliminar_conductor'),
    path('chat/', views.dashboard_chat, name='dashboard_chat'),
    path('analytics/', views.dashboard_analytics, name='dashboard_analytics'),
    path('api/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('publicidad/', views.dashboard_publicidad, name='dashboard_publicidad'),
    path('publicidad/ubicaciones/', views.ubicaciones_publicidad, name='dashboard_publicidad_ubicaciones'),
    #api pública para frontend
    path('api/publicidad/ubicaciones/', views.api_publicidad_ubicaciones, name='api_publicidad_ubicaciones'),
    path('api/publicidad/activas/', views.api_publicidad_activas, name='api_publicidad_activas'),
    path('api/publicidad/media/<int:campania_id>/', publicidad_views.api_publicidad_media, name='api_publicidad_media'),
    path('api/publicidad/solicitar/', views.api_publicidad_solicitar, name='api_publicidad_solicitar'),
    path('api/publicidad/solicitud/<int:solicitud_id>/', views.api_ver_solicitud, name='api_ver_solicitud'),
    path('api/publicidad/campanias/<int:campania_id>/', views.api_ver_campania, name='api_ver_campania'),
    #api de administración de publicidad web
    path('api/publicidad/solicitudes/<int:solicitud_id>/aprobar/', views.api_aprobar_solicitud, name='api_aprobar_solicitud'),
    #api de seguimiento de publicidad
    path('api/publicidad/campanias/<int:campania_id>/impresion/', views.api_track_impression, name='api_track_impression'),
    path('api/publicidad/campanias/<int:campania_id>/click/', views.api_track_click, name='api_track_click'),
    path('api/publicidad/solicitudes/<int:solicitud_id>/estado/', views.api_cambiar_estado_solicitud, name='api_cambiar_estado_solicitud'),
    path('api/publicidad/campanias-web/<int:campania_id>/', views.eliminar_campania_web, name='api_eliminar_campania_web'),
    path('api/publicidad/campanias-web/<int:campania_id>/actualizar_web/', views.api_actualizar_campania_web, name='api_actualizar_campania_web'),
    #subida de imágenes para campañas
    path('api/publicidad/subir-imagen/', views.api_subir_imagen_campania, name='api_subir_imagen_campania'),
    #imágenes por item de solicitud web
    path('api/publicidad/items/<int:item_id>/imagenes/', views.api_item_imagenes, name='api_item_imagenes'),
    path('api/publicidad/items/<int:item_id>/imagenes/subir/', views.api_item_subir_imagen, name='api_item_subir_imagen'),
    path('api/publicidad/imagenes/<int:imagen_id>/eliminar/', views.api_item_eliminar_imagen, name='api_item_eliminar_imagen'),
    path('api/publicidad/solicitudes/<int:solicitud_id>/eliminar/', views.eliminar_solicitud, name='api_eliminar_solicitud'),

    #estados crud
    path('estados/agregar/', views.agregar_estado, name='agregar_estado'),
    path('estados/eliminar/<int:estado_id>/', views.eliminar_estado, name='eliminar_estado'),

    #bandas emergentes crud
    path('emergentes/', views.dashboard_emergentes, name='dashboard_emergentes'),
    path('emergentes/crear/', views.crear_banda_emergente, name='crear_banda_emergente'),
    path('emergentes/editar/<int:banda_id>/', views.editar_banda_emergente, name='editar_banda_emergente'),
    path('emergentes/<int:banda_id>/<str:nuevo_estado>/', views.cambiar_estado_banda, name='cambiar_estado_banda'),
    path('emergentes/borrar/<int:banda_id>/', views.eliminar_banda_emergente, name='eliminar_banda_emergente'),
    path('emergentes/<int:banda_id>/detalle/', views.view_banda, name='view_banda'),
    path('emergentes/generos/agregar/', views.agregar_genero, name='agregar_genero'),
    path('emergentes/generos/eliminar/<int:genero_id>/', views.eliminar_genero, name='eliminar_genero'),
    path('api/comunas/', views.get_comunas_ajax, name='get_comunas_ajax'),  # API para cargar comunas por región

    #contactos crud
    path('contactos/', views.dashboard_contactos, name='dashboard_contactos'),
    path('contactos/<int:contacto_id>/update/', views.update_contacto, name='update_contacto'),
    path('contactos/<int:contacto_id>/delete/', views.delete_contacto, name='delete_contacto'),
    path('contactos/tipos/agregar/', views.agregar_tipo_asunto, name='agregar_tipo_asunto'),
    path('contactos/tipos/<int:tipo_id>/eliminar/', views.eliminar_tipo_asunto, name='eliminar_tipo_asunto'),

    #suscripciones
    path('suscripciones/', views.dashboard_suscripciones, name='dashboard_suscripciones'),
    path('suscripciones/<int:suscripcion_id>/toggle/', views.toggle_suscripcion, name='toggle_suscripcion'),
    path('suscripciones/<int:suscripcion_id>/delete/', views.delete_suscripcion, name='delete_suscripcion'),

    #user crud
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    #articulos crud
    path('articulos/create/', views.create_articulo, name='create_articulo'),
    path('articulos/edit/<int:articulo_id>/', views.edit_articulo, name='edit_articulo'),
    path('articulos/delete/<int:articulo_id>/', views.delete_articulo, name='delete_articulo'),
    path('articulos/categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('articulos/categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    #radio crud
    path('radio/create-program/', views.create_program, name='create_program'),
    path('radio/edit-program/<int:program_id>/', views.edit_program, name='edit_program'),
    path('radio/delete-program/<int:program_id>/', views.delete_program, name='delete_program'),
    path('radio/create-news/', views.create_news, name='create_news'),
    path('radio/delete-news/<int:news_id>/', views.delete_news, name='delete_news'),
    path('radio/toggle-status/', views.toggle_station_status, name='toggle_station_status'),
    path('radio/update_station/', views.update_station, name='update_station'),

    #chat moderation
    path('chat/delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('chat/clear/', views.clear_chat_messages, name='clear_chat_messages'),

    #notificaciones
    path('notificaciones/', views.dashboard_notificaciones, name='dashboard_notificaciones'),
    path('notificaciones/marcar-leida/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/eliminar/<int:notificacion_id>/', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
]

