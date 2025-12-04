from datetime import datetime as dt_datetime
from datetime import timezone as dt_timezone
import traceback
import os
from django.conf import settings
from django.http import JsonResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.db import transaction
from django.views.decorators.http import require_POST
from django.db.models import F
from django.db import transaction
from django.core import serializers
from datetime import datetime, timedelta
import json

from .forms import BandaEmergenteForm
from .forms import ConductorForm

from apps.users.models import User
from apps.articulos.models import Articulo, Categoria
from .models import Notificacion
from apps.radio.models import Programa, EstacionRadio, HorarioPrograma, GeneroMusical, ReproduccionRadio, Conductor, ProgramaConductor
from apps.chat.models import ChatMessage, InfraccionUsuario
from apps.contact.models import Contacto, Suscripcion, Estado, TipoAsunto
from apps.emergente.models import BandaEmergente, BandaLink, Integrante, BandaIntegrante
from apps.ubicacion.models import Pais, Ciudad, Comuna
from apps.publicidad.models import Publicidad, SolicitudPublicidadWeb, UbicacionPublicidadWeb, TipoUbicacion, ItemSolicitudWeb, PublicidadWeb
from apps.notifications.models import Notification as UserNotification
from rest_framework.authtoken.models import Token

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """dashboard principal con metricas generales"""
    #estadisticas generales
    total_users = User.objects.count()
    total_posts = Articulo.objects.count()
    total_programs = Programa.objects.count()
    total_subscriptions = Suscripcion.objects.count()
    
    #estadisticas de la ultima semana
    last_week = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(fecha_creacion__gte=last_week).count()
    new_posts_week = Articulo.objects.filter(fecha_creacion__gte=last_week).count()
    new_messages_week = ChatMessage.objects.filter(fecha_envio__gte=last_week).count()
    
    #articulos mas populares por fecha de publicacion reciente
    popular_posts = Articulo.objects.filter(publicado=True).order_by('-fecha_publicacion')[:5]
    
    #mensajes de contacto recientes
    recent_contacts = Contacto.objects.order_by('-fecha_envio')[:5]
    
    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_programs': total_programs,
        'total_subscriptions': total_subscriptions,
        'new_users_week': new_users_week,
        'new_posts_week': new_posts_week,
        'new_messages_week': new_messages_week,
        'popular_posts': popular_posts,
        'recent_contacts': recent_contacts,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def dashboard_calendario(request):
    context = {} 
    return render(request, 'dashboard/calendario.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """gestion de usuarios con paginacion y busqueda"""
    #obtener parametro de busqueda
    search_query = request.GET.get('search', '').strip()

    #filtrar usuarios
    users = User.objects.all()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    users = users.order_by('-fecha_creacion')

    #paginacion 10 usuarios por pagina
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/users.html', {
        'users': page_obj,
        'search_query': search_query,
        'paginator': paginator,
    })

@login_required
@user_passes_test(is_staff_user)
def dashboard_articulos(request):
    """gestion de articulos con paginacion y busqueda"""
    #obtener parametros de busqueda y filtro
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')

    #filtrar articulos
    articulos = Articulo.objects.select_related('autor', 'categoria').all()

    if search_query:
        articulos = articulos.filter(
            Q(titulo__icontains=search_query) |
            Q(resumen__icontains=search_query) |
            Q(contenido__icontains=search_query)
        )

    if status_filter == 'publicado':
        articulos = articulos.filter(publicado=True)
    elif status_filter == 'borrador':
        articulos = articulos.filter(publicado=False)

    articulos = articulos.order_by('-fecha_creacion')

    #paginacion 10 articulos por pagina
    paginator = Paginator(articulos, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    #obtener categorias
    categorias = Categoria.objects.all().order_by('nombre')

    #contadores para tarjetas total publicados y borradores
    total_articles = Articulo.objects.count()
    published_count = Articulo.objects.filter(publicado=True).count()
    draft_count = Articulo.objects.filter(publicado=False).count()

    return render(request, 'dashboard/articulos.html', {
        'articulos': page_obj,
        'categorias': categorias,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'paginator': paginator,
    })

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_categoria(request):
    """agregar una nueva categoría de artículo, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')

    if not nombre:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre de la categoría es obligatorio.'}, status=400)
        messages.error(request, 'El nombre de la categoría es obligatorio.')
        return redirect('dashboard_articulos')

    try:
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            message = f'La categoría "{nombre}" ya existe.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            message = f'Categoría "{categoria.nombre}" creada exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'categoria': {
                        'id': categoria.id,
                        'nombre': categoria.nombre,
                        'descripcion': categoria.descripcion or ''
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear la categoría: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_articulos')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_categoria(request, categoria_id):
    """eliminar una categoría de artículo, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        nombre_categoria = categoria.nombre
        
        if Articulo.objects.filter(categoria=categoria).exists():
            message = f'No se puede eliminar la categoría "{nombre_categoria}" porque tiene artículos asociados.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect('dashboard_articulos')
            
        categoria.delete()
        message = f'Categoría "{nombre_categoria}" eliminada correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar la categoría: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)
    
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def dashboard_radio(request):
    """gestion de radio y programas con paginacion"""
    #paginacion para programas
    programs_list = Programa.objects.all().order_by('nombre')
    programs_paginator = Paginator(programs_list, 10) # 10 programas por página
    programs_page_number = request.GET.get('programs_page', 1)
    programs = programs_paginator.get_page(programs_page_number)

    try:
        station = EstacionRadio.objects.first()
    except EstacionRadio.DoesNotExist:
        station = None

    articulos_recientes = Articulo.objects.filter(
        publicado=True
    ).select_related('categoria', 'autor').order_by('-fecha_publicacion')[:3]

    total_articulos = Articulo.objects.count()
    conductores_list = Conductor.objects.all().order_by('nombre')
    conductores_paginator = Paginator(conductores_list, 10) # 10 conductores por página
    conductores_page_number = request.GET.get('conductores_page', 1)
    conductores_paginados = conductores_paginator.get_page(conductores_page_number)
    
    all_conductores = conductores_list 

    context = {
        'programs': programs,
        'station': station,
        'articulos_recientes': articulos_recientes,
        'total_articulos': total_articulos,
        'total_articulos_count': total_articulos,
        'conductores': conductores_paginados,
        'all_conductores': all_conductores,
    }
    return render(request, 'dashboard/radio.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_chat(request):
    """moderación del chat"""
    messages = ChatMessage.objects.all().order_by('-fecha_envio')[:50]
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    messages_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).count()

    active_users_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).values('usuario_id').distinct().count()

    from django.db.models import Count
    top_users = ChatMessage.objects.values('usuario_id', 'usuario_nombre').annotate(
        message_count=Count('id')
    ).order_by('-message_count')[:10]

    User = get_user_model()
    top_users_list = []
    for user_data in top_users:
        if user_data['usuario_id']:
            try:
                user_obj = User.objects.get(id=user_data['usuario_id'])
                top_users_list.append({
                    'id': user_data['usuario_id'],
                    'username': user_data['usuario_nombre'],
                    'message_count': user_data['message_count'],
                    'is_blocked': user_obj.chat_bloqueado
                })
            except User.DoesNotExist:
                top_users_list.append({
                    'id': user_data['usuario_id'],
                    'username': user_data['usuario_nombre'],
                    'message_count': user_data['message_count'],
                    'is_blocked': False
                })

    context = {
        'messages': messages,
        'messages_today': messages_today,
        'active_users_today': active_users_today,
        'top_users': top_users_list,
    }

    return render(request, 'dashboard/chat.html', context)

@require_http_methods(["POST"])
@login_required
@user_passes_test(is_staff_user)
def clear_chat_messages(request):
    """limpiar todos los mensajes del chat - vista de django pura"""
    print(f"=== CLEAR CHAT MESSAGES (Django View) ===")
    print(f"User: {request.user}")
    print(f"Is staff: {request.user.is_staff}")

    try:
        data = json.loads(request.body) if request.body else {}
        sala = data.get('sala', 'radio-oriente')

        print(f"Eliminando mensajes de sala: {sala}")
        deleted_count = ChatMessage.objects.filter(sala=sala).delete()[0]
        print(f"Mensajes eliminados: {deleted_count}")

        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Se eliminaron {deleted_count} mensajes correctamente'
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@user_passes_test(is_staff_user)
def dashboard_analytics(request):
    """analytics y estadisticas detalladas"""
    #datos para graficos
    last_30_days = timezone.now() - timedelta(days=30)
    
    #usuarios por día (últimos 30 días)
    users_by_day = []
    for i in range(30):
        date = timezone.now() - timedelta(days=i)
        count = User.objects.filter(fecha_creacion__date=date.date()).count()
        users_by_day.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    #posts por mes (últimos 6 meses)
    posts_by_month = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        count = Articulo.objects.filter(
            fecha_creacion__year=date.year,
            fecha_creacion__month=date.month
        ).count()
        posts_by_month.append({'month': date.strftime('%Y-%m'), 'count': count})
    
    context = {
        'users_by_day': users_by_day,
        'posts_by_month': posts_by_month,
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_publicidad(request):
    """gestion de publicidad web: solicitudes y campañas publicadas"""
    #solicitudes con paginacion
    solicitudes_list = SolicitudPublicidadWeb.objects.select_related('usuario').order_by('-fecha_solicitud')
    solicitudes_paginator = Paginator(solicitudes_list, 10)
    solicitudes_page = request.GET.get('solicitudes_page')
    solicitudes = solicitudes_paginator.get_page(solicitudes_page)

    #campañas con paginacion
    campanias_list = Publicidad.objects.filter(tipo='WEB').select_related('web_config').order_by('-fecha_creacion')
    campanias_paginator = Paginator(campanias_list, 10)
    campanias_page = request.GET.get('campanias_page')
    campanias = campanias_paginator.get_page(campanias_page)

    return render(request, 'dashboard/publicidad.html', {
        'solicitudes': solicitudes,
        'campanias': campanias,
    })

@login_required
@user_passes_test(is_staff_user)
def ubicaciones_publicidad(request):
    """gestion de ubicaciones de publicidad (carousels, banners, etc.)"""
    ubicaciones = (
        UbicacionPublicidadWeb.objects
        .select_related('tipo')
        .annotate(items_count=Count('items_solicitud_web'))
        .all()
        .order_by('orden', 'nombre')
    )
    tipos_ubicacion_select = TipoUbicacion.objects.filter(activo=True).order_by('nombre')
    tipos_ubicacion_all = TipoUbicacion.objects.annotate(ubicaciones_count=Count('ubicaciones')).order_by('nombre')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        #gestion de eliminacion de ubicacion
        if form_type == 'delete_ubicacion':
            del_id = request.POST.get('ubicacion_id')
            try:
                ubic = UbicacionPublicidadWeb.objects.get(id=del_id)
                #evitar borrar si tiene items asociados
                if ubic.items_solicitud_web.exists():
                    messages.warning(request, 'No se puede eliminar: la ubicación tiene elementos asociados.')
                else:
                    ubic.delete()
                    messages.success(request, 'Ubicación eliminada correctamente')
            except ProtectedError:
                messages.error(request, 'No se puede eliminar la ubicación porque está protegida por relaciones.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la ubicación: {str(e)}')
            return redirect('dashboard_publicidad_ubicaciones')

        #gestion de eliminacion de tipo
        if form_type == 'delete_tipo':
            del_tipo_id = request.POST.get('tipo_id')
            try:
                t = TipoUbicacion.objects.get(id=del_tipo_id)
                if t.ubicaciones.exists():
                    messages.warning(request, 'No se puede eliminar: el tipo tiene ubicaciones asociadas.')
                else:
                    t.delete()
                    messages.success(request, 'Tipo de ubicación eliminado correctamente')
            except ProtectedError:
                messages.error(request, 'No se puede eliminar el tipo porque está protegido por relaciones.')
            except Exception as e:
                messages.error(request, f'Error al eliminar el tipo de ubicación: {str(e)}')
            return redirect('dashboard_publicidad_ubicaciones')

        #gestion de tipos de ubicacion
        if form_type == 'tipo':
            tipo_id_form = request.POST.get('tipo_id')
            nombre_tipo = request.POST.get('tipo_nombre')
            codigo_tipo = request.POST.get('tipo_codigo')
            descripcion_tipo = request.POST.get('tipo_descripcion', '')
            activo_tipo = 'tipo_activo' in request.POST

            try:
                if tipo_id_form:
                    tipo = TipoUbicacion.objects.get(id=tipo_id_form)
                    tipo.nombre = nombre_tipo
                    #mantener codigo inmutable al editar (como en admin)
                    tipo.descripcion = descripcion_tipo
                    tipo.activo = activo_tipo
                    tipo.save()
                    messages.success(request, 'Tipo de ubicación actualizado correctamente')
                else:
                    TipoUbicacion.objects.create(
                        codigo=codigo_tipo,
                        nombre=nombre_tipo,
                        descripcion=descripcion_tipo,
                        activo=activo_tipo
                    )
                    messages.success(request, 'Tipo de ubicación creado correctamente')
                return redirect('dashboard_publicidad_ubicaciones')
            except Exception as e:
                messages.error(request, f'Error al guardar el tipo de ubicación: {str(e)}')

        #gestion de ubicaciones
        else:
            ubicacion_id = request.POST.get('ubicacion_id')
            nombre = request.POST.get('nombre')
            tipo_id = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion', '')
            dimensiones = request.POST.get('dimensiones')
            precio_mensual = request.POST.get('precio_mensual')
            activo = 'activo' in request.POST
            orden = request.POST.get('orden', 0)
            
            try:
                tipo = TipoUbicacion.objects.get(id=tipo_id)
                
                if ubicacion_id: 
                    ubicacion = UbicacionPublicidadWeb.objects.get(id=ubicacion_id)
                    ubicacion.nombre = nombre
                    ubicacion.tipo = tipo
                    ubicacion.descripcion = descripcion
                    ubicacion.dimensiones = dimensiones
                    ubicacion.precio_mensual = precio_mensual
                    ubicacion.activo = activo
                    ubicacion.orden = orden
                    ubicacion.save()
                    messages.success(request, 'Ubicación actualizada correctamente')
                else:
                    UbicacionPublicidadWeb.objects.create(
                        nombre=nombre,
                        tipo=tipo,
                        descripcion=descripcion,
                        dimensiones=dimensiones,
                        precio_mensual=precio_mensual,
                        activo=activo,
                        orden=orden
                    )
                    messages.success(request, 'Ubicación creada correctamente')
                return redirect('dashboard_publicidad_ubicaciones')
                
            except TipoUbicacion.DoesNotExist:
                messages.error(request, 'El tipo de ubicación seleccionado no existe')
            except Exception as e:
                messages.error(request, f'Error al guardar la ubicación: {str(e)}')
    
    #paginacion para ubicaciones
    ubicaciones_paginator = Paginator(ubicaciones, 10)
    ubicaciones_page = request.GET.get('ubicaciones_page')
    ubicaciones_paginadas = ubicaciones_paginator.get_page(ubicaciones_page)

    #paginacion para tipos de ubicacion
    tipos_paginator = Paginator(tipos_ubicacion_all, 10)
    tipos_page = request.GET.get('tipos_page')
    tipos_paginados = tipos_paginator.get_page(tipos_page)

    return render(request, 'dashboard/ubicaciones_publicidad.html', {
        'ubicaciones': ubicaciones_paginadas,
        'tipos_ubicacion': tipos_ubicacion_select,
        'tipos_ubicacion_all': tipos_paginados,
    })

def dashboard_login(request):
    """login especifico para el dashboard"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard_home')
        else:
            return render(request, 'dashboard/login.html', {
                'error': 'Credenciales inválidas o sin permisos de administrador'
            })
    
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    """logout del dashboard"""
    logout(request)
    return redirect('dashboard_login')

@login_required
@user_passes_test(is_staff_user)
def api_dashboard_stats(request):
    """api endpoint para estadisticas del dashboard con filtros de tiempo"""
    from django.db.models.functions import TruncDate

    #obtener el filtro de tiempo
    time_filter = request.GET.get('filter', 'hoy')

    #calcular las fechas según el filtro
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if time_filter == 'hoy':
        start_date = today_start
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif time_filter == 'semana':
        start_date = today_start - timedelta(days=7)
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
    elif time_filter == 'mes':
        start_date = today_start - timedelta(days=30)
        prev_start = start_date - timedelta(days=30)
        prev_end = start_date
    else:  #todos
        start_date = None
        prev_start = None
        prev_end = None

    #filtrar por fecha si es necesario
    def filter_by_date(queryset, date_field='created_at'):
        if start_date:
            return queryset.filter(**{f'{date_field}__gte': start_date})
        return queryset

    #kpis - totales actuales
    total_users = filter_by_date(User.objects.all(), 'fecha_creacion').count()
    total_messages = filter_by_date(ChatMessage.objects.all(), 'fecha_envio').count()
    total_articles = filter_by_date(Articulo.objects.all(), 'fecha_creacion').count()
    total_subscriptions = filter_by_date(Suscripcion.objects.all(), 'fecha_suscripcion').count()
    total_contacts = filter_by_date(Contacto.objects.all(), 'fecha_envio').count()
    total_publicidad = Publicidad.objects.filter(activo=True).count()
    total_bandas_emergentes = filter_by_date(BandaEmergente.objects.all(), 'fecha_envio').count()
    total_reproducciones_unicas = filter_by_date(ReproduccionRadio.objects.all(), 'fecha_reproduccion').count()

    #kpis - período anterior para comparación
    users_change = 0
    messages_change = 0
    if prev_start and prev_end:
        prev_users = User.objects.filter(fecha_creacion__gte=prev_start, fecha_creacion__lt=prev_end).count()
        prev_messages = ChatMessage.objects.filter(fecha_envio__gte=prev_start, fecha_envio__lt=prev_end).count()

        users_change = ((total_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
        messages_change = ((total_messages - prev_messages) / prev_messages * 100) if prev_messages > 0 else 0

    #gráfico 1: usuarios por día
    users_by_day = list(
        filter_by_date(User.objects.all(), 'fecha_creacion')
        .annotate(date=TruncDate('fecha_creacion'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 2: mensajes por día
    messages_by_day = list(
        filter_by_date(ChatMessage.objects.all(), 'fecha_envio')
        .annotate(date=TruncDate('fecha_envio'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 3: articulos por categoría
    articles_by_category = list(
        filter_by_date(Articulo.objects.all(), 'fecha_creacion')
        .values('categoria__nombre')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('categoria__nombre', 'count')
    )

    #gráfico 4: contactos por tipo
    contacts_by_type = list(
        filter_by_date(Contacto.objects.all(), 'fecha_envio')
        .values('tipo_asunto__nombre')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('tipo_asunto__nombre', 'count')
    )

    #gráfico 5: suscripciones por día
    subscriptions_by_day = list(
        filter_by_date(Suscripcion.objects.all(), 'fecha_suscripcion')
        .annotate(date=TruncDate('fecha_suscripcion'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 6: infracciones por tipo
    infractions_by_type = list(
        filter_by_date(InfraccionUsuario.objects.all(), 'fecha_infraccion')
        .values('tipo_infraccion')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('tipo_infraccion', 'count')
    )

    #gráfico 7: top articulos mas vistos (solo con vistas > 0)
    top_articles = list(
        filter_by_date(Articulo.objects.all(), 'fecha_creacion')
        .filter(vistas__gt=0)
        .order_by('-vistas')[:5]
        .values_list('titulo', 'vistas')
    )

    #gráfico 8: estado de publicidad
    publicidad_activa = Publicidad.objects.filter(activo=True).count()
    publicidad_inactiva = Publicidad.objects.filter(activo=False).count()

    #respuesta en el formato esperado por el frontend
    response_data = {
        'kpis': {
            'total_users': total_users,
            'total_messages': total_messages,
            'total_articles': total_articles,
            'total_subscriptions': total_subscriptions,
            'total_contacts': total_contacts,
            'total_publicidad': total_publicidad,
            'total_bandas_emergentes': total_bandas_emergentes,
            'total_reproducciones_unicas': total_reproducciones_unicas,
            'users_change': round(users_change, 1),
            'messages_change': round(messages_change, 1),
        },
        'charts': {
            'users_by_day': [{'date': str(date), 'count': count} for date, count in users_by_day],
            'messages_by_day': [{'date': str(date), 'count': count} for date, count in messages_by_day],
            'articles_by_category': [{'category': str(cat) if cat else 'Sin categoría', 'count': count} for cat, count in articles_by_category],
            'contacts_by_type': [{'type': str(tipo) if tipo else 'Sin tipo', 'count': count} for tipo, count in contacts_by_type],
            'subscriptions_by_day': [{'date': str(date), 'count': count} for date, count in subscriptions_by_day],
            'infractions_by_type': [{'type': str(tipo) if tipo else 'Sin tipo', 'count': count} for tipo, count in infractions_by_type],
            'top_articles': [{'title': str(title) if title else 'Sin título', 'views': views or 0} for title, views in top_articles],
            'publicidad_status': {
                'activa': publicidad_activa,
                'inactiva': publicidad_inactiva
            }
        },
        'filter': time_filter
    }

    return JsonResponse(response_data)

def api_publicidad_ubicaciones(request):
    """api json para el frontend: lista tipos activos y sus ubicaciones activas"""
    from django.http import JsonResponse
    from apps.publicidad.models import TipoUbicacion, UbicacionPublicidadWeb
    
    try:
        include_all = request.GET.get('all') == '1'
        
        #obtener tipos de ubicacion
        tipos_qs = TipoUbicacion.objects.all() if include_all else TipoUbicacion.objects.filter(activo=True)
        tipos = list(
            tipos_qs.order_by('nombre').values('id', 'nombre', 'codigo', 'descripcion', 'activo')
        )
        
        #obtener ubicaciones
        ubic_qs = UbicacionPublicidadWeb.objects.select_related('tipo')
        if not include_all:
            ubic_qs = ubic_qs.filter(activo=True, tipo__activo=True)
            
        ubicaciones = list(
            ubic_qs.order_by('orden', 'nombre').values(
                'id', 'nombre', 'descripcion', 'dimensiones', 'precio_mensual',
                'orden', 'activo', 'tipo_id', 'tipo__nombre', 'tipo__codigo', 'tipo__activo'
            )
        )
        
        #devolver la respuesta json
        return JsonResponse({
            'success': True,
            'tipos': tipos,
            'ubicaciones': ubicaciones
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener ubicaciones: {str(e)}'
        }, status=500)

def api_publicidad_activas(request):
    """API pública para el frontend: lista campañas WEB activas con detalles de ubicación.
    Filtros opcionales:
      - q: texto a buscar en ubicacion.nombre (case-insensitive)
      - dimensiones: ej "300x600"
      - limit: máximo de resultados (por defecto 50)
    """
    from django.http import JsonResponse
    from django.utils import timezone
    from django.db.models import Q
    from apps.publicidad.models import Publicidad, ItemSolicitudWeb
    import re

    try:
        hoy = timezone.now().date()
        q = (request.GET.get('q') or '').strip().lower()
        dimensiones_filter = (request.GET.get('dimensiones') or '').strip().lower()
        try:
            limit = int(request.GET.get('limit') or 50)
        except Exception:
            limit = 50
        limit = max(1, min(limit, 200))

        #cargar campañas web activas en rango de fechas y publicadas/aprobadas
        #considera
        #- solicitudes aprobadas o activas
        #- campañas creadas manualmente (sin solicitud asociada)
        pubs = (Publicidad.objects
                .filter(
                    tipo='WEB',
                    activo=True,
                    fecha_inicio__lte=hoy,
                    fecha_fin__gte=hoy,
                )
                .filter(Q(solicitud_web__estado__in=['aprobada', 'activa']) | Q(solicitud_web__isnull=True))
                .select_related('web_config')
                .order_by('-fecha_creacion')
                .distinct()[:500])

        items = []
        for pub in pubs:
            wc = getattr(pub, 'web_config', None)
            if not wc:
                continue
            #obtener media url
            media_val = getattr(wc, 'archivo_media', None)
            media_url = None
            if media_val:
                media_url = getattr(media_val, 'url', None) or str(media_val)

            #intentar resolver ubicacion desde la descripcion (item #id)
            ubic = None
            item_from_desc = None
            try:
                desc = getattr(pub, 'descripcion', '') or ''
                m = re.search(r'Item\s*#(\d+)', desc)
                if m:
                    item_id = int(m.group(1))
                    item = ItemSolicitudWeb.objects.select_related('ubicacion__tipo').get(id=item_id)
                    item_from_desc = item
                    if item.ubicacion:
                        #normalizar dimensiones de la ubicacion a formato 000x000
                        dims_raw = getattr(item.ubicacion, 'dimensiones', None) or ''
                        dims_norm = None
                        try:
                            m_dims = re.search(r"(\d+\s*[xX]\s*\d+)", str(dims_raw), re.I)
                            if m_dims:
                                dims_norm = m_dims.group(1).lower().replace(' ', '')
                        except Exception:
                            pass
                        ubic = {
                            'nombre': getattr(item.ubicacion, 'nombre', None),
                            'dimensiones': dims_norm or (getattr(item.ubicacion, 'dimensiones', None) or ''),
                            'tipo': getattr(getattr(item.ubicacion, 'tipo', None), 'nombre', None),
                        }
            except Exception:
                pass

            #fallback desde formato
            if not ubic:
                formato = getattr(wc, 'formato', '') or ''
                nombre = None
                tipo = None
                dims = None
                if '—' in formato:
                    partes = [p.strip() for p in formato.split('—', 1)]
                    if partes:
                        nombre = partes[0] or None
                    if len(partes) > 1:
                        right = partes[1]
                        m2 = re.match(r'^([^\d]+)?\s*(\d+\s*x\s*\d+)', right, re.I)
                        if m2:
                            tipo = (m2.group(1) or '').strip() or None
                            dims = (m2.group(2) or '').replace(' ', '')
                        else:
                            #buscar dimensiones en cualquier parte
                            m3 = re.search(r'(\d+\s*x\s*\d+)', formato, re.I)
                            if m3:
                                dims = m3.group(1).replace(' ', '')
                else:
                    #solo dimensiones presentes
                    m4 = re.search(r'(\d+\s*x\s*\d+)', formato, re.I)
                    dims = m4.group(1).replace(' ', '') if m4 else None
                ubic = {
                    'nombre': nombre,
                    'tipo': tipo,
                    'dimensiones': dims,
                }

            #si aún no hay ubicacion, intentar desde la solicitud asociada
            if not ubic:
                try:
                    sol_rel = getattr(pub, 'solicitud_web', None)
                    if sol_rel:
                        item_sol = (ItemSolicitudWeb.objects
                                    .select_related('ubicacion__tipo')
                                    .filter(solicitud_id=getattr(sol_rel, 'id', None))
                                    .order_by('id')
                                    .first())
                        if item_sol and item_sol.ubicacion:
                            dims_raw2 = getattr(item_sol.ubicacion, 'dimensiones', None) or ''
                            dims_norm2 = None
                            try:
                                m_dims2 = re.search(r"(\d+\s*[xX]\s*\d+)", str(dims_raw2), re.I)
                                if m_dims2:
                                    dims_norm2 = m_dims2.group(1).lower().replace(' ', '')
                            except Exception:
                                pass
                            ubic = {
                                'nombre': getattr(item_sol.ubicacion, 'nombre', None),
                                'dimensiones': dims_norm2 or (getattr(item_sol.ubicacion, 'dimensiones', None) or ''),
                                'tipo': getattr(getattr(item_sol.ubicacion, 'tipo', None), 'nombre', None),
                            }
                            #media fallback desde imagen del item si sigue faltando
                            if not media_url:
                                try:
                                    img2 = item_sol.imagenes_web.order_by('orden', 'fecha_subida').first()
                                    if img2 and getattr(img2, 'imagen', None):
                                        media_url = getattr(img2.imagen, 'url', None) or str(img2.imagen)
                                except Exception:
                                    pass
                except Exception:
                    pass

            #fallback de media desde la primera imagen del item asociado
            if not media_url and item_from_desc is not None:
                try:
                    img = item_from_desc.imagenes_web.order_by('orden', 'fecha_subida').first()
                    if img and getattr(img, 'imagen', None):
                        media_url = getattr(img.imagen, 'url', None) or str(img.imagen)
                except Exception:
                    pass

            if not media_url:
                continue

            #asegurar url absoluta para el frontend
            try:
                if isinstance(media_url, str) and media_url.startswith('/'):
                    media_url = request.build_absolute_uri(media_url)
            except Exception:
                pass

            #aplicar filtros
            if q:
                nombre_l = (ubic.get('nombre') or '').lower()
                tipo_l = (ubic.get('tipo') or '').lower()
                if (q not in nombre_l) and (q not in tipo_l):
                    continue
            if dimensiones_filter and (ubic.get('dimensiones') or '').lower() != dimensiones_filter:
                continue

            #forzar uso de proxy anti-adblock (ruta neutral)
            try:
                from django.urls import reverse
                try:
                    proxy_path = reverse('api_adimg_media', args=[pub.id])
                except Exception:
                    proxy_path = reverse('api_publicidad_media', args=[pub.id])  #compatibilidad
                media_url_proxy = request.build_absolute_uri(proxy_path)
            except Exception:
                media_url_proxy = media_url

            items.append({
                'id': pub.id,
                'media_url': media_url_proxy,
                'url_destino': getattr(wc, 'url_destino', None),
                'formato': getattr(wc, 'formato', None),
                'fecha_inicio': pub.fecha_inicio.isoformat() if pub.fecha_inicio else None,
                'fecha_fin': pub.fecha_fin.isoformat() if pub.fecha_fin else None,
                'ubicacion': ubic,
            })
            if len(items) >= limit:
                break

        return JsonResponse({'success': True, 'items': items})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Error al obtener campañas: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_staff_user)
def dashboard_chat(request):
    """moderación del chat"""
    #obtener todos los mensajes
    messages = ChatMessage.objects.all().order_by('-fecha_envio')[:50]

    #estadisticas del dia
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    messages_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).count()

    #usuarios unicos activos hoy (basado en mensajes)
    active_users_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).values('usuario_id').distinct().count()

    #obtener usuarios mas activos (top 10 con mas mensajes)
    from django.db.models import Count
    top_users = ChatMessage.objects.values('usuario_id', 'usuario_nombre').annotate(
        message_count=Count('id')
    ).order_by('-message_count')[:10]

    #obtener informacion de bloqueo para cada usuario
    User = get_user_model()
    top_users_list = []
    for user_data in top_users:
        if user_data['usuario_id']:
            try:
                user_obj = User.objects.get(id=user_data['usuario_id'])
                top_users_list.append({
                    'id': user_data['usuario_id'],
                    'username': user_data['usuario_nombre'],
                    'message_count': user_data['message_count'],
                    'is_blocked': user_obj.chat_bloqueado
                })
            except User.DoesNotExist:
                top_users_list.append({
                    'id': user_data['usuario_id'],
                    'username': user_data['usuario_nombre'],
                    'message_count': user_data['message_count'],
                    'is_blocked': False
                })

    context = {
        'messages': messages,
        'messages_today': messages_today,
        'active_users_today': active_users_today,
        'top_users': top_users_list,
    }

    return render(request, 'dashboard/chat.html', context)

@require_http_methods(["POST"])
@login_required
@user_passes_test(is_staff_user)
def clear_chat_messages(request):
    """limpiar todos los mensajes del chat - vista de django pura"""
    print(f"=== CLEAR CHAT MESSAGES (Django View) ===")
    print(f"User: {request.user}")
    print(f"Is staff: {request.user.is_staff}")

    try:
        data = json.loads(request.body) if request.body else {}
        sala = data.get('sala', 'radio-oriente')

        print(f"Eliminando mensajes de sala: {sala}")
        deleted_count = ChatMessage.objects.filter(sala=sala).delete()[0]
        print(f"Mensajes eliminados: {deleted_count}")

        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Se eliminaron {deleted_count} mensajes correctamente'
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@user_passes_test(is_staff_user)
def dashboard_analytics(request):
    """analytics y estadisticas detalladas"""
    #datos para graficos
    last_30_days = timezone.now() - timedelta(days=30)
    
    #usuarios por día (últimos 30 días)
    users_by_day = []
    for i in range(30):
        date = timezone.now() - timedelta(days=i)
        count = User.objects.filter(fecha_creacion__date=date.date()).count()
        users_by_day.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    #posts por mes (últimos 6 meses)
    posts_by_month = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        count = Articulo.objects.filter(
            fecha_creacion__year=date.year,
            fecha_creacion__month=date.month
        ).count()
        posts_by_month.append({'month': date.strftime('%Y-%m'), 'count': count})
    
    context = {
        'users_by_day': users_by_day,
        'posts_by_month': posts_by_month,
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_publicidad(request):
    """gestion de publicidad web: solicitudes y campañas publicadas"""
    #solicitudes con paginacion
    solicitudes_list = SolicitudPublicidadWeb.objects.select_related('usuario').order_by('-fecha_solicitud')
    solicitudes_paginator = Paginator(solicitudes_list, 10)
    solicitudes_page = request.GET.get('solicitudes_page')
    solicitudes = solicitudes_paginator.get_page(solicitudes_page)

    #campañas con paginacion
    campanias_list = Publicidad.objects.filter(tipo='WEB').select_related('web_config').order_by('-fecha_creacion')
    campanias_paginator = Paginator(campanias_list, 10)
    campanias_page = request.GET.get('campanias_page')
    campanias = campanias_paginator.get_page(campanias_page)

    return render(request, 'dashboard/publicidad.html', {
        'solicitudes': solicitudes,
        'campanias': campanias,
    })

@login_required
@user_passes_test(is_staff_user)
def ubicaciones_publicidad(request):
    """gestion de ubicaciones de publicidad (carousels, banners, etc.)"""
    ubicaciones = (
        UbicacionPublicidadWeb.objects
        .select_related('tipo')
        .annotate(items_count=Count('items_solicitud_web'))
        .all()
        .order_by('orden', 'nombre')
    )
    tipos_ubicacion_select = TipoUbicacion.objects.filter(activo=True).order_by('nombre')
    tipos_ubicacion_all = TipoUbicacion.objects.annotate(ubicaciones_count=Count('ubicaciones')).order_by('nombre')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        #gestion de eliminacion de ubicacion
        if form_type == 'delete_ubicacion':
            del_id = request.POST.get('ubicacion_id')
            try:
                ubic = UbicacionPublicidadWeb.objects.get(id=del_id)
                #evitar borrar si tiene items asociados
                if ubic.items_solicitud_web.exists():
                    messages.warning(request, 'No se puede eliminar: la ubicación tiene elementos asociados.')
                else:
                    ubic.delete()
                    messages.success(request, 'Ubicación eliminada correctamente')
            except ProtectedError:
                messages.error(request, 'No se puede eliminar la ubicación porque está protegida por relaciones.')
            except Exception as e:
                messages.error(request, f'Error al eliminar la ubicación: {str(e)}')
            return redirect('dashboard_publicidad_ubicaciones')

        #gestion de eliminacion de tipo
        if form_type == 'delete_tipo':
            del_tipo_id = request.POST.get('tipo_id')
            try:
                t = TipoUbicacion.objects.get(id=del_tipo_id)
                if t.ubicaciones.exists():
                    messages.warning(request, 'No se puede eliminar: el tipo tiene ubicaciones asociadas.')
                else:
                    t.delete()
                    messages.success(request, 'Tipo de ubicación eliminado correctamente')
            except ProtectedError:
                messages.error(request, 'No se puede eliminar el tipo porque está protegido por relaciones.')
            except Exception as e:
                messages.error(request, f'Error al eliminar el tipo de ubicación: {str(e)}')
            return redirect('dashboard_publicidad_ubicaciones')

        #gestion de tipos de ubicacion
        if form_type == 'tipo':
            tipo_id_form = request.POST.get('tipo_id')
            nombre_tipo = request.POST.get('tipo_nombre')
            codigo_tipo = request.POST.get('tipo_codigo')
            descripcion_tipo = request.POST.get('tipo_descripcion', '')
            activo_tipo = 'tipo_activo' in request.POST

            try:
                if tipo_id_form:
                    tipo = TipoUbicacion.objects.get(id=tipo_id_form)
                    tipo.nombre = nombre_tipo
                    #mantener codigo inmutable al editar (como en admin)
                    tipo.descripcion = descripcion_tipo
                    tipo.activo = activo_tipo
                    tipo.save()
                    messages.success(request, 'Tipo de ubicación actualizado correctamente')
                else:
                    TipoUbicacion.objects.create(
                        codigo=codigo_tipo,
                        nombre=nombre_tipo,
                        descripcion=descripcion_tipo,
                        activo=activo_tipo
                    )
                    messages.success(request, 'Tipo de ubicación creado correctamente')
                return redirect('dashboard_publicidad_ubicaciones')
            except Exception as e:
                messages.error(request, f'Error al guardar el tipo de ubicación: {str(e)}')

        #gestion de ubicaciones
        else:
            #procesar formulario
            ubicacion_id = request.POST.get('ubicacion_id')
            nombre = request.POST.get('nombre')
            tipo_id = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion', '')
            dimensiones = request.POST.get('dimensiones')
            precio_mensual = request.POST.get('precio_mensual')
            activo = 'activo' in request.POST
            orden = request.POST.get('orden', 0)

            try:
                tipo = TipoUbicacion.objects.get(id=tipo_id)

                if ubicacion_id:
                    #actualizar existente
                    ubicacion = UbicacionPublicidadWeb.objects.get(id=ubicacion_id)
                    ubicacion.nombre = nombre
                    ubicacion.tipo = tipo
                    ubicacion.descripcion = descripcion
                    ubicacion.dimensiones = dimensiones
                    ubicacion.precio_mensual = precio_mensual
                    ubicacion.activo = activo
                    ubicacion.orden = orden
                    ubicacion.save()
                    messages.success(request, 'Ubicación actualizada correctamente')
                else:
                    #crear nuevo
                    UbicacionPublicidadWeb.objects.create(
                        nombre=nombre,
                        tipo=tipo,
                        descripcion=descripcion,
                        dimensiones=dimensiones,
                        precio_mensual=precio_mensual,
                        activo=activo,
                        orden=orden
                    )
                    messages.success(request, 'Ubicación creada correctamente')

                return redirect('dashboard_publicidad_ubicaciones')

            except TipoUbicacion.DoesNotExist:
                messages.error(request, 'El tipo de ubicación seleccionado no existe')
            except Exception as e:
                messages.error(request, f'Error al guardar la ubicación: {str(e)}')
    
    #paginacion para ubicaciones
    ubicaciones_paginator = Paginator(ubicaciones, 10)
    ubicaciones_page = request.GET.get('ubicaciones_page')
    ubicaciones_paginadas = ubicaciones_paginator.get_page(ubicaciones_page)

    #paginacion para tipos de ubicacion
    tipos_paginator = Paginator(tipos_ubicacion_all, 10)
    tipos_page = request.GET.get('tipos_page')
    tipos_paginados = tipos_paginator.get_page(tipos_page)

    return render(request, 'dashboard/ubicaciones_publicidad.html', {
        'ubicaciones': ubicaciones_paginadas,
        'tipos_ubicacion': tipos_ubicacion_select,
        'tipos_ubicacion_all': tipos_paginados,
    })

def dashboard_login(request):
    """login especifico para el dashboard"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard_home')
        else:
            return render(request, 'dashboard/login.html', {
                'error': 'Credenciales inválidas o sin permisos de administrador'
            })
    
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    """logout del dashboard"""
    logout(request)
    return redirect('dashboard_login')

@login_required
@user_passes_test(is_staff_user)
def api_dashboard_stats(request):
    """api endpoint para estadisticas del dashboard con filtros de tiempo"""
    from django.db.models.functions import TruncDate

    #obtener el filtro de tiempo
    time_filter = request.GET.get('filter', 'hoy')

    #calcular las fechas según el filtro
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if time_filter == 'hoy':
        start_date = today_start
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif time_filter == 'semana':
        start_date = today_start - timedelta(days=7)
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
    elif time_filter == 'mes':
        start_date = today_start - timedelta(days=30)
        prev_start = start_date - timedelta(days=30)
        prev_end = start_date
    else:  #todos
        start_date = None
        prev_start = None
        prev_end = None

    #filtrar por fecha si es necesario
    def filter_by_date(queryset, date_field='created_at'):
        if start_date:
            return queryset.filter(**{f'{date_field}__gte': start_date})
        return queryset

    #kpis - totales actuales
    total_users = filter_by_date(User.objects.all(), 'fecha_creacion').count()
    total_messages = filter_by_date(ChatMessage.objects.all(), 'fecha_envio').count()
    total_articles = filter_by_date(Articulo.objects.all(), 'fecha_creacion').count()
    total_subscriptions = filter_by_date(Suscripcion.objects.all(), 'fecha_suscripcion').count()
    total_contacts = filter_by_date(Contacto.objects.all(), 'fecha_envio').count()
    total_publicidad = Publicidad.objects.filter(activo=True).count()
    total_bandas_emergentes = filter_by_date(BandaEmergente.objects.all(), 'fecha_envio').count()
    total_reproducciones_unicas = filter_by_date(ReproduccionRadio.objects.all(), 'fecha_reproduccion').count()

    #kpis - período anterior para comparación
    users_change = 0
    messages_change = 0
    if prev_start and prev_end:
        prev_users = User.objects.filter(fecha_creacion__gte=prev_start, fecha_creacion__lt=prev_end).count()
        prev_messages = ChatMessage.objects.filter(fecha_envio__gte=prev_start, fecha_envio__lt=prev_end).count()

        users_change = ((total_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
        messages_change = ((total_messages - prev_messages) / prev_messages * 100) if prev_messages > 0 else 0

    #gráfico 1: usuarios por día
    users_by_day = list(
        filter_by_date(User.objects.all(), 'fecha_creacion')
        .annotate(date=TruncDate('fecha_creacion'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 2: mensajes por día
    messages_by_day = list(
        filter_by_date(ChatMessage.objects.all(), 'fecha_envio')
        .annotate(date=TruncDate('fecha_envio'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 3: articulos por categoría
    articles_by_category = list(
        filter_by_date(Articulo.objects.all(), 'fecha_creacion')
        .values('categoria__nombre')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('categoria__nombre', 'count')
    )

    #gráfico 4: contactos por tipo
    contacts_by_type = list(
        filter_by_date(Contacto.objects.all(), 'fecha_envio')
        .values('tipo_asunto__nombre')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('tipo_asunto__nombre', 'count')
    )

    #gráfico 5: suscripciones por día
    subscriptions_by_day = list(
        filter_by_date(Suscripcion.objects.all(), 'fecha_suscripcion')
        .annotate(date=TruncDate('fecha_suscripcion'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values_list('date', 'count')
    )

    #gráfico 6: infracciones por tipo
    infractions_by_type = list(
        filter_by_date(InfraccionUsuario.objects.all(), 'fecha_infraccion')
        .values('tipo_infraccion')
        .annotate(count=Count('id'))
        .order_by('-count')
        .values_list('tipo_infraccion', 'count')
    )

    #gráfico 7: top articulos mas vistos (solo con vistas > 0)
    top_articles = list(
        filter_by_date(Articulo.objects.all(), 'fecha_creacion')
        .filter(vistas__gt=0)
        .order_by('-vistas')[:5]
        .values_list('titulo', 'vistas')
    )

    #gráfico 8: estado de publicidad
    publicidad_activa = Publicidad.objects.filter(activo=True).count()
    publicidad_inactiva = Publicidad.objects.filter(activo=False).count()

    #respuesta en el formato esperado por el frontend
    response_data = {
        'kpis': {
            'total_users': total_users,
            'total_messages': total_messages,
            'total_articles': total_articles,
            'total_subscriptions': total_subscriptions,
            'total_contacts': total_contacts,
            'total_publicidad': total_publicidad,
            'total_bandas_emergentes': total_bandas_emergentes,
            'total_reproducciones_unicas': total_reproducciones_unicas,
            'users_change': round(users_change, 1),
            'messages_change': round(messages_change, 1),
        },
        'charts': {
            'users_by_day': [{'date': str(date), 'count': count} for date, count in users_by_day],
            'messages_by_day': [{'date': str(date), 'count': count} for date, count in messages_by_day],
            'articles_by_category': [{'category': str(cat) if cat else 'Sin categoría', 'count': count} for cat, count in articles_by_category],
            'contacts_by_type': [{'type': str(tipo) if tipo else 'Sin tipo', 'count': count} for tipo, count in contacts_by_type],
            'subscriptions_by_day': [{'date': str(date), 'count': count} for date, count in subscriptions_by_day],
            'infractions_by_type': [{'type': str(tipo) if tipo else 'Sin tipo', 'count': count} for tipo, count in infractions_by_type],
            'top_articles': [{'title': str(title) if title else 'Sin título', 'views': views or 0} for title, views in top_articles],
            'publicidad_status': {
                'activa': publicidad_activa,
                'inactiva': publicidad_inactiva
            }
        },
        'filter': time_filter
    }

    return JsonResponse(response_data)

def api_publicidad_ubicaciones(request):
    """api json para el frontend: lista tipos activos y sus ubicaciones activas"""
    from django.http import JsonResponse
    from apps.publicidad.models import TipoUbicacion, UbicacionPublicidadWeb
    
    try:
        include_all = request.GET.get('all') == '1'
        
        #obtener tipos de ubicacion
        tipos_qs = TipoUbicacion.objects.all() if include_all else TipoUbicacion.objects.filter(activo=True)
        tipos = list(
            tipos_qs.order_by('nombre').values('id', 'nombre', 'codigo', 'descripcion', 'activo')
        )
        
        #obtener ubicaciones
        ubic_qs = UbicacionPublicidadWeb.objects.select_related('tipo')
        if not include_all:
            ubic_qs = ubic_qs.filter(activo=True, tipo__activo=True)
            
        ubicaciones = list(
            ubic_qs.order_by('orden', 'nombre').values(
                'id', 'nombre', 'descripcion', 'dimensiones', 'precio_mensual',
                'orden', 'activo', 'tipo_id', 'tipo__nombre', 'tipo__codigo', 'tipo__activo'
            )
        )
        
        #devolver la respuesta json
        return JsonResponse({
            'success': True,
            'tipos': tipos,
            'ubicaciones': ubicaciones
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener ubicaciones: {str(e)}'
        }, status=500)

def api_publicidad_activas(request):
    """API pública para el frontend: lista campañas WEB activas con detalles de ubicación.
    Filtros opcionales:
      - q: texto a buscar en ubicacion.nombre (case-insensitive)
      - dimensiones: ej "300x600"
      - limit: máximo de resultados (por defecto 50)
    """
    from django.http import JsonResponse
    from django.utils import timezone
    from django.db.models import Q
    from apps.publicidad.models import Publicidad, ItemSolicitudWeb
    import re

    try:
        hoy = timezone.now().date()
        q = (request.GET.get('q') or '').strip().lower()
        dimensiones_filter = (request.GET.get('dimensiones') or '').strip().lower()
        try:
            limit = int(request.GET.get('limit') or 50)
        except Exception:
            limit = 50
        limit = max(1, min(limit, 200))

        #cargar campañas web activas en rango de fechas y publicadas/aprobadas
        #considera
        #- solicitudes aprobadas o activas
        #- campañas creadas manualmente (sin solicitud asociada)
        pubs = (Publicidad.objects
                .filter(
                    tipo='WEB',
                    activo=True,
                    fecha_inicio__lte=hoy,
                    fecha_fin__gte=hoy,
                )
                .filter(Q(solicitud_web__estado__in=['aprobada', 'activa']) | Q(solicitud_web__isnull=True))
                .select_related('web_config')
                .order_by('-fecha_creacion')
                .distinct()[:500])

        items = []
        for pub in pubs:
            wc = getattr(pub, 'web_config', None)
            if not wc:
                continue
            #obtener media url
            media_val = getattr(wc, 'archivo_media', None)
            media_url = None
            if media_val:
                media_url = getattr(media_val, 'url', None) or str(media_val)

            #intentar resolver ubicacion desde la descripcion (item #id)
            ubic = None
            item_from_desc = None
            try:
                desc = getattr(pub, 'descripcion', '') or ''
                m = re.search(r'Item\s*#(\d+)', desc)
                if m:
                    item_id = int(m.group(1))
                    item = ItemSolicitudWeb.objects.select_related('ubicacion__tipo').get(id=item_id)
                    item_from_desc = item
                    if item.ubicacion:
                        #normalizar dimensiones de la ubicacion a formato 000x000
                        dims_raw = getattr(item.ubicacion, 'dimensiones', None) or ''
                        dims_norm = None
                        try:
                            m_dims = re.search(r"(\d+\s*[xX]\s*\d+)", str(dims_raw), re.I)
                            if m_dims:
                                dims_norm = m_dims.group(1).lower().replace(' ', '')
                        except Exception:
                            pass
                        ubic = {
                            'nombre': getattr(item.ubicacion, 'nombre', None),
                            'dimensiones': dims_norm or (getattr(item.ubicacion, 'dimensiones', None) or ''),
                            'tipo': getattr(getattr(item.ubicacion, 'tipo', None), 'nombre', None),
                        }
            except Exception:
                pass

            #fallback desde formato
            if not ubic:
                formato = getattr(wc, 'formato', '') or ''
                nombre = None
                tipo = None
                dims = None
                if '—' in formato:
                    partes = [p.strip() for p in formato.split('—', 1)]
                    if partes:
                        nombre = partes[0] or None
                    if len(partes) > 1:
                        right = partes[1]
                        m2 = re.match(r'^([^\d]+)?\s*(\d+\s*x\s*\d+)', right, re.I)
                        if m2:
                            tipo = (m2.group(1) or '').strip() or None
                            dims = (m2.group(2) or '').replace(' ', '')
                        else:
                            #buscar dimensiones en cualquier parte
                            m3 = re.search(r'(\d+\s*x\s*\d+)', formato, re.I)
                            if m3:
                                dims = m3.group(1).replace(' ', '')
                else:
                    #solo dimensiones presentes
                    m4 = re.search(r'(\d+\s*x\s*\d+)', formato, re.I)
                    dims = m4.group(1).replace(' ', '') if m4 else None
                ubic = {
                    'nombre': nombre,
                    'tipo': tipo,
                    'dimensiones': dims,
                }

            #si aún no hay ubicacion, intentar desde la solicitud asociada
            if not ubic:
                try:
                    sol_rel = getattr(pub, 'solicitud_web', None)
                    if sol_rel:
                        item_sol = (ItemSolicitudWeb.objects
                                    .select_related('ubicacion__tipo')
                                    .filter(solicitud_id=getattr(sol_rel, 'id', None))
                                    .order_by('id')
                                    .first())
                        if item_sol and item_sol.ubicacion:
                            dims_raw2 = getattr(item_sol.ubicacion, 'dimensiones', None) or ''
                            dims_norm2 = None
                            try:
                                m_dims2 = re.search(r"(\d+\s*[xX]\s*\d+)", str(dims_raw2), re.I)
                                if m_dims2:
                                    dims_norm2 = m_dims2.group(1).lower().replace(' ', '')
                            except Exception:
                                pass
                            ubic = {
                                'nombre': getattr(item_sol.ubicacion, 'nombre', None),
                                'dimensiones': dims_norm2 or (getattr(item_sol.ubicacion, 'dimensiones', None) or ''),
                                'tipo': getattr(getattr(item_sol.ubicacion, 'tipo', None), 'nombre', None),
                            }
                            #media fallback desde imagen del item si sigue faltando
                            if not media_url:
                                try:
                                    img2 = item_sol.imagenes_web.order_by('orden', 'fecha_subida').first()
                                    if img2 and getattr(img2, 'imagen', None):
                                        media_url = getattr(img2.imagen, 'url', None) or str(img2.imagen)
                                except Exception:
                                    pass
                except Exception:
                    pass

            #fallback de media desde la primera imagen del item asociado
            if not media_url and item_from_desc is not None:
                try:
                    img = item_from_desc.imagenes_web.order_by('orden', 'fecha_subida').first()
                    if img and getattr(img, 'imagen', None):
                        media_url = getattr(img.imagen, 'url', None) or str(img.imagen)
                except Exception:
                    pass

            if not media_url:
                continue

            #asegurar url absoluta para el frontend
            try:
                if isinstance(media_url, str) and media_url.startswith('/'):
                    media_url = request.build_absolute_uri(media_url)
            except Exception:
                pass

            #aplicar filtros
            if q:
                nombre_l = (ubic.get('nombre') or '').lower()
                tipo_l = (ubic.get('tipo') or '').lower()
                if (q not in nombre_l) and (q not in tipo_l):
                    continue
            if dimensiones_filter and (ubic.get('dimensiones') or '').lower() != dimensiones_filter:
                continue

            #forzar uso de proxy anti-adblock (ruta neutral)
            try:
                from django.urls import reverse
                try:
                    proxy_path = reverse('api_adimg_media', args=[pub.id])
                except Exception:
                    proxy_path = reverse('api_publicidad_media', args=[pub.id])  #compatibilidad
                media_url_proxy = request.build_absolute_uri(proxy_path)
            except Exception:
                media_url_proxy = media_url

            items.append({
                'id': pub.id,
                'media_url': media_url_proxy,
                'url_destino': getattr(wc, 'url_destino', None),
                'formato': getattr(wc, 'formato', None),
                'fecha_inicio': pub.fecha_inicio.isoformat() if pub.fecha_inicio else None,
                'fecha_fin': pub.fecha_fin.isoformat() if pub.fecha_fin else None,
                'ubicacion': ubic,
            })
            if len(items) >= limit:
                break

        return JsonResponse({'success': True, 'items': items})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Error al obtener campañas: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_staff_user)
def api_aprobar_solicitud(request, solicitud_id: int):
    """aprobar una solicitudpublicidadweb y generar la campaña publicidad + publicidadweb"""
    from django.core.files import File
    from django.conf import settings
    import os
    from django.db import transaction
    
    try:
        #obtener la solicitud con todas las relaciones necesarias
        sol = (SolicitudPublicidadWeb.objects
              .select_related('usuario')
              .prefetch_related(
                  'items_web__ubicacion',
  #incluir las imagenes relacionadas
              ).get(id=solicitud_id))
    except SolicitudPublicidadWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)

    #si ya tiene publicacion asociada, verificar si ya está aprobada
    if sol.publicacion_id:
        if sol.estado != 'aprobada':
            #si tiene publicacion pero no está marcada como aprobada, actualizar estado
            sol.estado = 'aprobada'
            sol.fecha_aprobacion = timezone.now()
            sol.save(update_fields=['estado', 'fecha_aprobacion'])
            
            #intentar notificar al usuario (ignorar errores)
            try:
                notificar_aprobacion_solicitud(sol, request.user)
            except Exception:
                pass
                
        return JsonResponse({
            'success': True,
            'message': 'La solicitud ya tenía una campaña asociada. Se ha actualizado el estado a aprobada.',
            'redirect': '/dashboard/publicidad/'
        })

    try:
        with transaction.atomic():
            #crear una campaña por cada item de la solicitud
            created_campaign_ids = []
            nombre_cliente = sol.nombre_contacto or sol.usuario.get_full_name() or sol.usuario.username
            #definir rango de publicacion a partir de la aprobación
            from datetime import timedelta
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30)

            for item_solicitud in sol.items_web.all():
                pub = Publicidad.objects.create(
                    nombre_cliente=nombre_cliente,
                    descripcion=f"Solicitud #{sol.id} - Item #{item_solicitud.id}",
                    tipo='WEB',
                    fecha_inicio=start_date,
                    fecha_fin=end_date,
                    costo_total=getattr(item_solicitud, 'precio_acordado', None) or sol.costo_total_estimado,
                    activo=True,
                )

                #construir formato combinando nombre de ubicacion, tipo y dimensiones si existen
                formato_str = item_solicitud.formato or ''
                try:
                    if item_solicitud.ubicacion:
                        ubic_nombre = getattr(item_solicitud.ubicacion, 'nombre', '') or ''
                        tipo_nombre = getattr(getattr(item_solicitud.ubicacion, 'tipo', None), 'nombre', '') or ''
                        dims = getattr(item_solicitud.ubicacion, 'dimensiones', '') or ''
                        #ej: "home header — banner 728x90"
                        left = (ubic_nombre or '').strip()
                        right = (tipo_nombre + (' ' if tipo_nombre and dims else '') + (dims or '')).strip()
                        combinado = (left + (' — ' if left and right else '') + right).strip()
                        formato_str = combinado or formato_str or dims
                except Exception:
                    pass

                #configuracion web por item
                pub_web = PublicidadWeb.objects.create(
                    publicidad=pub,
                    url_destino=item_solicitud.url_destino or '',
                    formato=formato_str,
                    impresiones=0,
                    clics=0
                )

                #copiar la primera imagen asociada al ítem (si existe)
                if item_solicitud.imagenes_web.exists():
                    img = item_solicitud.imagenes_web.first()
                    if img and img.imagen:
                        nombre_original = os.path.basename(img.imagen.name)
                        nombre_destino = f"{pub.id}_{nombre_original}"

                        ruta_origen = os.path.join(settings.MEDIA_ROOT, img.imagen.name)
                        carpeta_destino = os.path.join(settings.MEDIA_ROOT, 'publicidad', 'web')
                        ruta_destino = os.path.join(carpeta_destino, nombre_destino)

                        if os.path.exists(ruta_origen):
                            os.makedirs(carpeta_destino, exist_ok=True)
                            with open(ruta_origen, 'rb') as fsrc, open(ruta_destino, 'wb') as fdst:
                                fdst.write(fsrc.read())
                            media_url = getattr(settings, 'MEDIA_URL', '/media/')
                            pub_web.archivo_media = f"{media_url}publicidad/web/{nombre_destino}"
                            if item_solicitud.url_destino:
                                pub_web.url_destino = item_solicitud.url_destino
                            pub_web.save()
                        else:
                            print(f"Advertencia: No se encontró el archivo {ruta_origen}")

                created_campaign_ids.append(pub.id)

            #actualizar la solicitud
            if created_campaign_ids:
                #asociar publicacion creada
                try:
                    sol.publicacion_id = created_campaign_ids[0]
                except Exception:
                    pass
            sol.estado = 'aprobada'
            sol.fecha_aprobacion = timezone.now()
            #actualizar fechas solicitadas
            try:
                sol.fecha_inicio_solicitada = start_date
                sol.fecha_fin_solicitada = end_date
                sol.save(update_fields=['estado', 'fecha_aprobacion', 'fecha_inicio_solicitada', 'fecha_fin_solicitada', 'publicacion_id'])
            except Exception:
                sol.save(update_fields=['estado', 'fecha_aprobacion'])

            #notificar al usuario solicitante
            try:
                titulo = f"Solicitud de publicidad #{sol.id} aprobada"
                mensaje = (
                    f"Tu solicitud fue aprobada. Rango: {start_date} a {end_date}. "
                    f"Pronto verás tu campaña publicada."
                )
                UserNotification.objects.create(
                    usuario=sol.usuario,
                    tipo='publicidad',
                    titulo=titulo,
                    mensaje=mensaje,
                    enlace=None,
                    content_type='solicitud_publicidad',
                    object_id=sol.id,
                )
            except Exception:
                pass
                
            return JsonResponse({
                'success': True,
                'message': f'Solicitud aprobada: {len(created_campaign_ids)} campañas creadas',
                'created_campaign_ids': created_campaign_ids,
                'redirect': '/dashboard/publicidad/'
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al aprobar la solicitud: {str(e)}'
        }, status=500)

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["PATCH", "POST"])
def api_cambiar_estado_solicitud(request, solicitud_id: int):
    """cambia el estado de una solicitud: pendiente | en_revision | aprobada | rechazada"""
    try:
        sol = SolicitudPublicidadWeb.objects.get(id=solicitud_id)
    except SolicitudPublicidadWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)

    try:
        data = json.loads(request.body or '{}')
    except Exception:
        data = {}

    nuevo = data.get('estado')
    if nuevo not in {'pendiente', 'en_revision', 'aprobada', 'rechazada'}:
        return JsonResponse({'success': False, 'message': 'Estado inválido'}, status=400)

    #si es aprobación, delegamos a la funcion específica
    if nuevo == 'aprobada':
        return api_aprobar_solicitud(request, solicitud_id)

    #revisión / rechazo
    if 'notas_admin' in data:
        sol.notas_admin = data.get('notas_admin') or None
    if nuevo == 'rechazada' and 'motivo' in data:
        sol.motivo_rechazo = data.get('motivo') or None
    
    sol.estado = nuevo
    sol.save(update_fields=['estado', 'notas_admin', 'motivo_rechazo'])

    #notificar al usuario sobre el cambio de estado (en revisión / rechazado)
    try:
        if nuevo == 'en_revision':
            titulo = f"Solicitud de publicidad #{sol.id} en revisión"
            extra = f" Nota: {sol.notas_admin}" if sol.notas_admin else ""
            mensaje = f"Tu solicitud está en revisión. Nos pondremos en contacto contigo pronto.{extra}"
        elif nuevo == 'rechazada':
            titulo = f"Solicitud de publicidad #{sol.id} rechazada"
            extra = f" Motivo: {sol.motivo_rechazo}" if sol.motivo_rechazo else ""
            mensaje = f"Tu solicitud ha sido rechazada.{extra}"
        else:
            titulo = f"Estado actualizado: {sol.get_estado_display()}"
            mensaje = f"Tu solicitud cambió a estado: {sol.get_estado_display()}"

        UserNotification.objects.create(
            usuario=sol.usuario,
            tipo='publicidad',
            titulo=titulo,
            mensaje=mensaje,
            enlace=None,
            content_type='solicitud_publicidad',
            object_id=sol.id,
        )
    except Exception:
        pass
    
    return JsonResponse({
        'success': True, 
        'message': f'Solicitud actualizada a {nuevo}'
    })

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["PATCH"]) 
def api_actualizar_campania_web(request, campania_id: int):
    """actualizar datos web (url_destino, formato, archivo_media) de una campaña web"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
    if not is_staff_user(request.user):
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)

    try:
        pub = Publicidad.objects.select_related('web_config').get(id=campania_id, tipo='WEB')
    except Publicidad.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Campaña no encontrada'}, status=404)
    try:
        data = json.loads(request.body or '{}')
    except Exception:
        data = {}
    web = getattr(pub, 'web_config', None)
    try:
        #permitir activar/desactivar la campaña
        if 'activo' in data:
            try:
                pub.activo = bool(data.get('activo'))
                pub.save(update_fields=['activo'])
            except Exception:
                pass

        if web is None:
            web = PublicidadWeb.objects.create(
                publicidad=pub,
                url_destino=data.get('url_destino', ''),
                formato=data.get('formato', ''),
                impresiones=0,
                clics=0,
                archivo_media=data.get('archivo_media', '') or None,
            )
        else:
            changed = False
            if 'url_destino' in data:
                web.url_destino = data['url_destino']
                changed = True
            if 'formato' in data:
                web.formato = data['formato']
                changed = True
            if 'archivo_media' in data:
                web.archivo_media = data['archivo_media'] or None
                changed = True
            if changed:
                web.save()
        return JsonResponse({'success': True, 'activo': pub.activo})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al actualizar: {str(e)}'}, status=500)

@require_http_methods(["GET"]) 
def api_ver_campania(request, campania_id: int):
    """devuelve los detalles de una campaña publicidad (web) para la vista de dashboard. estructura esperada por el frontend (verdetallescampania): { id, nombre_cliente, activo, fecha_inicio, fecha_fin, web_config: { url_destino, formato, archivo_media, impresiones, clics } }"""
    try:
        pub = Publicidad.objects.select_related('web_config').get(id=campania_id, tipo='WEB')
    except Publicidad.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Campaña no encontrada'}, status=404)

    #construir respuesta
    data = {
        'id': pub.id,
        'nombre_cliente': getattr(pub, 'nombre_cliente', '') or '',
        'activo': getattr(pub, 'activo', True),
        'fecha_inicio': pub.fecha_inicio.isoformat() if getattr(pub, 'fecha_inicio', None) else None,
        'fecha_fin': pub.fecha_fin.isoformat() if getattr(pub, 'fecha_fin', None) else None,
        'web_config': None,
        'ubicacion': None,
    }
    wc = getattr(pub, 'web_config', None)
    if wc:
        media_val = getattr(wc, 'archivo_media', None)
        media_url = None
        if media_val:
            if hasattr(media_val, 'url'):
                media_url = media_val.url
            else:
                media_url = str(media_val)
        data['web_config'] = {
            'url_destino': getattr(wc, 'url_destino', '') or None,
            'formato': getattr(wc, 'formato', '') or None,
            'archivo_media': media_url,
            'impresiones': getattr(wc, 'impresiones', 0) or 0,
            'clics': getattr(wc, 'clics', 0) or 0,
        }

    #intenta obtener la ubicacion como el nombre, tipo, dimensiones desde el item original
    try:
        desc = getattr(pub, 'descripcion', '') or ''
        import re
        m = re.search(r'Item\s*#(\d+)', desc)
        if m:
            item_id = int(m.group(1))
            item = ItemSolicitudWeb.objects.select_related('ubicacion__tipo').get(id=item_id)
            if item.ubicacion:
                data['ubicacion'] = {
                    'nombre': getattr(item.ubicacion, 'nombre', None),
                    'dimensiones': getattr(item.ubicacion, 'dimensiones', None),
                    'tipo': getattr(getattr(item.ubicacion, 'tipo', None), 'nombre', None),
                }
    except Exception:
        pass
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"])
def api_publicidad_solicitar(request):
    """crea una solicitud de publicidad web. requiere autenticacion. espera json con: nombre, email, telefono, preferencia_contacto, ubicacion_id, url_destino, fecha_inicio, fecha_fin, mensaje (opcional)"""
    #resolver usuario autenticado (sesión o token)
    auth_user = request.user if request.user.is_authenticated else None
    if not auth_user:
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if isinstance(auth_header, str) and auth_header.startswith('Token '):
                token_key = auth_header.split(' ', 1)[1].strip()
                token_obj = Token.objects.select_related('user').get(key=token_key)
                auth_user = token_obj.user
        except Token.DoesNotExist:
            auth_user = None
        except Exception:
            auth_user = None

    #verificar autenticacion primero
    if not auth_user:
        #para api, nunca redirigimos: devolvemos 401 consistente
        return JsonResponse(
            {'success': False, 'message': 'Debes iniciar sesión para enviar una solicitud de publicidad'}, 
            status=401
        )

    try:
        data = json.loads(request.body or '{}')
    except Exception:
        return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)

    #datos del usuario autenticado
    if not data.get('email'):
        data['email'] = auth_user.email
    if not data.get('nombre'):
        data['nombre'] = auth_user.get_full_name() or auth_user.username

    #puede venir 'ubicacion_id' (uno), 'ubicacion_ids' (lista) o 'ubicaciones' (lista de ids u objetos con id)
    required = ['nombre', 'email']
    missing = [k for k in required if not data.get(k)]
    if missing:
        return JsonResponse({'success': False, 'message': f'Faltan campos: {", ".join(missing)}'}, status=400)

    ubicacion_ids = data.get('ubicacion_ids')
    if not ubicacion_ids:
        single = data.get('ubicacion_id')
        ubicacion_ids = [single] if single else []

    #otra variante: 'ubicaciones'
    if not ubicacion_ids and data.get('ubicaciones'):
        ub = data.get('ubicaciones')
        if isinstance(ub, list):
            #aceptar lista de ids o lista de objetos {id: ...}
            ubicacion_ids = [ (x.get('id') if isinstance(x, dict) else x) for x in ub ]
    ubicacion_ids = [uid for uid in ubicacion_ids if uid]
    if not ubicacion_ids:
        return JsonResponse({'success': False, 'message': 'Debe seleccionar al menos una ubicación'}, status=400)

    ubics = list(UbicacionPublicidadWeb.objects.select_related('tipo').filter(id__in=ubicacion_ids))
    if not ubics:
        return JsonResponse({'success': False, 'message': 'Ubicaciones no encontradas'}, status=404)

    nombre = data.get('nombre')
    email = data.get('email')
    telefono = data.get('telefono')
    preferencia = data.get('preferencia_contacto', 'telefono')
    url_destino = data.get('url_destino', '')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    mensaje = data.get('mensaje', '')

    #crear solicitud + item (solo para usuarios autenticados)
    try:
        #fechas opcionales
        from datetime import date
        def parse_date(s):
            try:
                return date.fromisoformat(s) if s else None
            except Exception:
                return None
        fi = parse_date(fecha_inicio) or timezone.now().date()
        ff = parse_date(fecha_fin) or fi

        #total estimado suma de ubicaciones seleccionadas
        total_estimado = sum([u.precio_mensual for u in ubics])
        
        #usuario autenticado
        solicitud = SolicitudPublicidadWeb.objects.create(
            usuario=auth_user,
            nombre_contacto=nombre or auth_user.get_full_name() or auth_user.username,
            email_contacto=email or auth_user.email,
            telefono_contacto=telefono or '',
            preferencia_contacto=preferencia,
            estado='pendiente',
            fecha_inicio_solicitada=fi,
            fecha_fin_solicitada=ff,
            mensaje_usuario=mensaje,
            costo_total_estimado=total_estimado,
        )
        
        created_items = []
        for ubic in ubics:
            item = ItemSolicitudWeb.objects.create(
                solicitud=solicitud,
                ubicacion=ubic,
                url_destino=url_destino,
                formato=ubic.dimensiones,
                precio_acordado=ubic.precio_mensual,
                notas=f"Tipo: {ubic.tipo.nombre}"
            )
            created_items.append({'id': item.id, 'ubicacion_id': ubic.id})
            
        return JsonResponse({
            'success': True,
            'message': 'Solicitud creada. Te contactaremos pronto.',
            'solicitud_id': solicitud.id,
            'items_web': created_items
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'message': f'Error al crear solicitud: {str(e)}'
        }, status=500)


def api_ver_solicitud(request, solicitud_id):
    """devuelve los detalles completos de una solicitud de publicidad web, incluyendo sus ítems e imágenes asociadas"""
    from apps.publicidad.models import SolicitudPublicidadWeb, ItemSolicitudWeb, ImagenPublicidadWeb, UbicacionPublicidadWeb
    from django.core.serializers.json import DjangoJSONEncoder
    from django.http import JsonResponse
    import json
    
    try:
        #obtener la solicitud con relaciones optimizadas
        solicitud = (SolicitudPublicidadWeb.objects
            .select_related('usuario')
            .prefetch_related(
                'items_web__ubicacion',
                'items_web__imagenes_web'
            )
            .get(id=solicitud_id)
        )
        
        #construir la respuesta
        data = {
            'id': solicitud.id,
            'nombre_contacto': solicitud.nombre_contacto or '',
            'email_contacto': solicitud.email_contacto or (solicitud.usuario.email if solicitud.usuario else ''),
            'usuario_username': solicitud.usuario.username if solicitud.usuario else 'Usuario no autenticado',
            'telefono_contacto': solicitud.telefono_contacto or '',
            'preferencia_contacto': solicitud.preferencia_contacto or 'email',
            'estado': solicitud.estado or 'pendiente',
            'estado_display': 'Contactado en breve' if solicitud.estado == 'en_revision' else solicitud.get_estado_display(),
            'fecha_solicitud': solicitud.fecha_solicitud.isoformat(),
            'fecha_inicio_solicitada': solicitud.fecha_inicio_solicitada.isoformat() if hasattr(solicitud, 'fecha_inicio_solicitada') and solicitud.fecha_inicio_solicitada else None,
            'fecha_fin_solicitada': solicitud.fecha_fin_solicitada.isoformat() if hasattr(solicitud, 'fecha_fin_solicitada') and solicitud.fecha_fin_solicitada else None,
            'costo_total_estimado': float(solicitud.costo_total_estimado) if hasattr(solicitud, 'costo_total_estimado') and solicitud.costo_total_estimado is not None else 0.0,
            'mensaje_usuario': solicitud.mensaje_usuario or '',
            'notas_admin': solicitud.notas_admin or '',
            'motivo_rechazo': solicitud.motivo_rechazo or '',
            'items_web': []
        }
        
        #agregar los ítems de la solicitud
        for item in solicitud.items_web.all():
            ubicacion = item.ubicacion
            item_data = {
                'id': item.id,
                'ubicacion_id': ubicacion.id if ubicacion else 0,
                'ubicacion_nombre': str(ubicacion) if ubicacion else 'Ubicación no especificada',
                'formato': item.formato or '',
                'precio_acordado': float(item.precio_acordado) if item.precio_acordado is not None else 0.0,
                'url_destino': item.url_destino or '',
                'notas': item.notas or '',
                'imagenes': []
            }
            
            #agregar las imágenes del ítem si existen
            for img in item.imagenes_web.all():
                item_data['imagenes'].append({
                    'id': img.id,
                    'descripcion': img.descripcion or '',
                    'url': img.imagen.url if img.imagen else None,
                    'orden': img.orden,
                    'fecha_subida': img.fecha_subida.isoformat() if img.fecha_subida else None
                })
            
            data['items_web'].append(item_data)
        
        return JsonResponse(data, encoder=DjangoJSONEncoder, safe=False)
        
    except SolicitudPublicidadWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error en api_ver_solicitud: {str(e)}\n{error_details}")
        return JsonResponse({
            'success': False, 
            'message': f'Error al obtener la solicitud: {str(e)}',
            'error_details': error_details
        }, status=500, json_dumps_params={'ensure_ascii': False})

@require_http_methods(["GET"])
def api_item_imagenes(request, item_id: int):
    """lista imágenes de un itemsolicitudweb"""
    from apps.publicidad.models import ItemSolicitudWeb
    try:
        item = ItemSolicitudWeb.objects.get(id=item_id)
        imgs = [
            {
                'id': img.id,
                'descripcion': img.descripcion or '',
                'url': (img.imagen.url if img.imagen else None),
                'orden': img.orden,
                'fecha_subida': img.fecha_subida.isoformat() if img.fecha_subida else None,
            }
            for img in item.imagenes_web.all()
        ]
        return JsonResponse({'success': True, 'imagenes': imgs})
    except ItemSolicitudWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item no encontrado'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def api_item_subir_imagen(request, item_id: int):
    """sube una imagen para un itemsolicitudweb"""
    from apps.publicidad.models import ItemSolicitudWeb, ImagenPublicidadWeb
    try:
        item = ItemSolicitudWeb.objects.get(id=item_id)
    except ItemSolicitudWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item no encontrado'}, status=404)

    file = request.FILES.get('imagen')
    if not file:
        return JsonResponse({'success': False, 'message': 'Falta archivo de imagen (campo "imagen")'}, status=400)

    descripcion = request.POST.get('descripcion', '')
    try:
        orden = int(request.POST.get('orden', '0'))
    except Exception:
        orden = 0

    img = ImagenPublicidadWeb.objects.create(
        item=item,
        imagen=file,
        descripcion=descripcion,
        orden=orden,
    )
    data = {
        'id': img.id,
        'descripcion': img.descripcion or '',
        'url': (img.imagen.url if img.imagen else None),
        'orden': img.orden,
        'fecha_subida': img.fecha_subida.isoformat() if img.fecha_subida else None,
    }
    return JsonResponse({'success': True, 'imagen': data})

@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_item_eliminar_imagen(request, imagen_id: int):
    """elimina una imagen de un itemsolicitudweb"""
    from apps.publicidad.models import ImagenPublicidadWeb
    try:
        img = ImagenPublicidadWeb.objects.get(id=imagen_id)
    except ImagenPublicidadWeb.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Imagen no encontrada'}, status=404)

    img.delete()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["DELETE", "POST"])
def eliminar_campania_web(request, campania_id):
    """elimina una campaña de publicidad web y sus elementos asociados. acepta tanto delete como post para mayor compatibilidad"""
    try:
        campania = get_object_or_404(Publicidad, id=campania_id, tipo='WEB')
        
        #verificar permisos (solo staff puede eliminar)
        if not request.user.is_staff:
            return JsonResponse({'error': 'No tienes permiso para realizar esta acción'}, status=403)
            
        #eliminar la configuracion web si existe
        if hasattr(campania, 'web_config'):
            #eliminar el archivo de medios si existe (acepta url, ruta relativa o filefield)
            try:
                media_value = getattr(campania.web_config, 'archivo_media', None)
                if media_value:
                    #si es un filefield con .path
                    file_path = None
                    if hasattr(media_value, 'path'):
                        file_path = media_value.path
                    else:
                        #media_value puede ser str (url absoluta, "/media/..." o relativa)
                        from urllib.parse import urlparse
                        raw = str(media_value)
                        parsed = urlparse(raw)
                        candidate_path = parsed.path if parsed.scheme in ('http', 'https') else raw
                        #normalizar contra media_url
                        if getattr(settings, 'MEDIA_URL', '') and candidate_path.startswith(settings.MEDIA_URL):
                            rel = candidate_path[len(settings.MEDIA_URL):]
                            file_path = os.path.join(settings.MEDIA_ROOT, rel)
                        elif candidate_path.startswith('/'):
                            #si es ruta absoluta del sistema, usarla tal cual; si parece bajo /media, unir a media_root
                            if getattr(settings, 'MEDIA_URL', '') and candidate_path.startswith(settings.MEDIA_URL):
                                rel = candidate_path[len(settings.MEDIA_URL):]
                                file_path = os.path.join(settings.MEDIA_ROOT, rel)
                            else:
                                #podría ya ser una ruta absoluta válida
                                file_path = candidate_path
                        else:
                            #ruta relativa: asumir relativa a media_root
                            file_path = os.path.join(settings.MEDIA_ROOT, candidate_path)

                    if file_path and os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception:
                #no bloquear la eliminacion por fallo al borrar archivo
                pass

            campania.web_config.delete()
            
        #finalmente, eliminar la campaña
        campania.delete()
        
        return JsonResponse({'success': True, 'message': 'Campaña eliminada correctamente'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def eliminar_solicitud(request, solicitud_id):
    """elimina una solicitud de publicidad y sus elementos asociados"""
    try:
        solicitud = get_object_or_404(SolicitudPublicidadWeb, id=solicitud_id)
        
        #verificar permisos (solo staff puede eliminar)
        if not request.user.is_staff:
            return JsonResponse({'error': 'No tienes permiso para realizar esta acción'}, status=403)
            
        #eliminar los items y sus imágenes asociadas
        for item in solicitud.items_web.all():
            #eliminar las imágenes del storage
            for img in item.imagenes_web.all():
                if img.imagen:
                    if os.path.isfile(img.imagen.path):
                        os.remove(img.imagen.path)
                img.delete()
            item.delete()
            
        #finalmente, eliminar la solicitud
        solicitud.delete()
        
        return JsonResponse({'success': True, 'message': 'Solicitud eliminada correctamente'})
        
        #si no es ajax, redirigir con mensaje
        messages.success(request, f'Solicitud #{solicitud_id} eliminada correctamente.')
        return redirect('dashboard_publicidad')
        
    except Exception as e:
        error_msg = f'Error al eliminar la solicitud: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg}, status=500)
            
        messages.error(request, error_msg)
        return redirect('dashboard_publicidad')

#crud operations for users
@login_required
@user_passes_test(is_staff_user)
def create_user(request):
    """crear nuevo usuario"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        try:
            user = User.objects.create_user(
                email=correo,
                username=usuario,
                password=password,
                first_name=nombre,
                is_staff=is_staff
            )
            messages.success(request, f'Usuario {usuario} creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def edit_user(request, user_id):
    """editar usuario existente"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.nombre = request.POST.get('nombre')
        user.usuario = request.POST.get('usuario')
        user.correo = request.POST.get('correo')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'

        try:
            user.save()
            messages.success(request, f'Usuario {user.usuario} actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def delete_user(request, user_id):
    """eliminar usuario"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.usuario
        try:
            user.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
    
    return redirect('dashboard_users')

#crud operations for articulos
@login_required
@user_passes_test(is_staff_user)
def create_articulo(request):
    """crear nuevo artículo con soporte multimedia"""
    if request.method == 'POST':
        try:
            #obtener datos del formulario
            titulo = request.POST.get('titulo')
            contenido = request.POST.get('contenido')
            categoria_id = request.POST.get('categoria')
            resumen = request.POST.get('resumen', '')
            publicado = request.POST.get('publicado') == 'on'
            
            #obtener archivos
            imagen_portada = request.FILES.get('imagen_portada')
            imagen_thumbnail = request.FILES.get('imagen_thumbnail')
            archivo_adjunto = request.FILES.get('archivo_adjunto')
            
            #obtener urls
            imagen_url = request.POST.get('imagen_url', '')
            video_url = request.POST.get('video_url', '')
            
            #validaciones básicas
            if not titulo or not contenido or not categoria_id:
                messages.error(request, 'Por favor complete todos los campos requeridos')
                return redirect('dashboard_articulos')
                
            #crear el artículo y adjuntar archivos antes del primer save
            articulo = Articulo(
                titulo=titulo,
                contenido=contenido,
                categoria_id=categoria_id,
                resumen=resumen,
                publicado=publicado,
                autor=request.user,
                imagen_url=imagen_url if imagen_url else None,
                video_url=video_url if video_url else None
            )
            #asignar archivos antes del primer guardado
            if imagen_portada:
                articulo.imagen_portada = imagen_portada
            if imagen_thumbnail:
                articulo.imagen_thumbnail = imagen_thumbnail
            if archivo_adjunto:
                articulo.archivo_adjunto = archivo_adjunto

            #guardar con todo adjuntado
            articulo.save()
            
            #la notificacion se maneja mediante la señal post_save en el modelo notificacion
            messages.success(request, 'Artículo creado exitosamente')
            return redirect('dashboard_articulos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el artículo: {str(e)}')
            return redirect('dashboard_articulos')
    
    #si no es post, redirigir a la lista de articulos
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def edit_articulo(request, articulo_id):
    """editar artículo con soporte multimedia"""
    articulo = get_object_or_404(Articulo, id=articulo_id)
    
    if request.method == 'POST':
        articulo.titulo = request.POST.get('titulo')
        articulo.contenido = request.POST.get('contenido')
        articulo.resumen = request.POST.get('resumen')
        categoria_id = request.POST.get('categoria')
        articulo.publicado = request.POST.get('publicado') == 'on'
        articulo.imagen_url = request.POST.get('imagen_url')
        articulo.video_url = request.POST.get('video_url')
        
        #actualizar archivos si se proporcionan nuevos
        imagen_portada = request.FILES.get('imagen_portada')
        if imagen_portada:
            articulo.imagen_portada = imagen_portada
        
        imagen_thumbnail = request.FILES.get('imagen_thumbnail')
        if imagen_thumbnail:
            articulo.imagen_thumbnail = imagen_thumbnail
            
        archivo_adjunto = request.FILES.get('archivo_adjunto')
        if archivo_adjunto:
            articulo.archivo_adjunto = archivo_adjunto
        
        try:
            #actualizar categoría si se proporciona
            if categoria_id:
                articulo.categoria = Categoria.objects.get(id=categoria_id)
            articulo.save()
            messages.success(request, f'Artículo "{articulo.titulo}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar artículo: {str(e)}')
    
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def delete_articulo(request, articulo_id):
    """eliminar artículo"""
    articulo = get_object_or_404(Articulo, id=articulo_id)
    
    if request.method == 'POST':
        titulo = articulo.titulo
        try:
            articulo.delete()
            messages.success(request, f'Artículo "{titulo}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar artículo: {str(e)}')
    
    return redirect('dashboard_articulos')

#crud operations for radio programs
@login_required
@user_passes_test(is_staff_user)
def create_program(request):
    """crear nuevo programa de radio"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fin_str = request.POST.get('hora_fin')
        dias = request.POST.getlist('dias[]')
        activo = request.POST.get('activo') == 'on'
        conductor_ids = request.POST.getlist('conductores[]')
        
        try:
            #--- convertir strings de hora a objetos time ---
            hora_inicio_obj = dt_datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin_obj = dt_datetime.strptime(hora_fin_str, '%H:%M').time()
            #----------------------------------------------------
        except (ValueError, TypeError):
            messages.error(request, 'Formato de hora inválido. Use HH:MM.')
            return redirect('dashboard_radio')
        
        try:
            program = Programa.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                activo=activo
            )
            
            if dias and hora_inicio_str and hora_fin_str:
                for dia in dias:
                    HorarioPrograma.objects.create(
                        programa=program,
                        dia_semana=int(dia),
                        hora_inicio=hora_inicio_obj,
                        hora_fin=hora_fin_obj,
                        activo=True
                    )
            
            if conductor_ids:
                for conductor_id in conductor_ids:
                    try:
                        conductor = Conductor.objects.get(id=conductor_id)
                        ProgramaConductor.objects.create(programa=program, conductor=conductor)
                    except Conductor.DoesNotExist:
                        pass 
            
            messages.success(request, f'Programa "{nombre}" creado exitosamente.')
        except Exception as e:
            print("--- ERROR EN CREATE_PROGRAM ---")
            traceback.print_exc()
            messages.error(request, f'Error al crear programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def edit_program(request, program_id):
    """editar programa de radio"""
    program = get_object_or_404(Programa, id=program_id)
    
    if request.method == 'POST':
        program.nombre = request.POST.get('nombre')
        program.descripcion = request.POST.get('descripcion')
        program.activo = request.POST.get('activo') == 'on'
        
        hora_inicio_str = request.POST.get('hora_inicio')
        hora_fin_str = request.POST.get('hora_fin')
        dias = request.POST.getlist('dias[]')
        conductor_ids = request.POST.getlist('conductores[]')
        
        try:
            hora_inicio_obj = dt_datetime.strptime(hora_inicio_str, '%H:%M').time()
            hora_fin_obj = dt_datetime.strptime(hora_fin_str, '%H:%M').time()
            #----------------------------------------------------
        except (ValueError, TypeError):
            messages.error(request, 'Formato de hora inválido. Use HH:MM.')
            return redirect('dashboard_radio')
            
        try:
            program.save()
            
            if dias and hora_inicio_str and hora_fin_str:
                program.horarios.all().delete()
                for dia in dias:
                    HorarioPrograma.objects.create(
                        programa=program,
                        dia_semana=int(dia),
                        hora_inicio=hora_inicio_obj,
                        hora_fin=hora_fin_obj,
                        activo=True
                    )
            
            program.conductores.all().delete()
            if conductor_ids:
                for conductor_id in conductor_ids:
                    try:
                        conductor = Conductor.objects.get(id=conductor_id)
                        ProgramaConductor.objects.create(programa=program, conductor=conductor)
                    except Conductor.DoesNotExist:
                        pass
            
            messages.success(request, f'Programa "{program.nombre}" actualizado exitosamente')
        except Exception as e:
            print("--- ERROR EN EDIT_PROGRAM ---")
            traceback.print_exc()
            messages.error(request, f'Error al actualizar programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_program(request, program_id):
    """eliminar programa de radio"""
    program = get_object_or_404(Programa, id=program_id)
    
    if request.method == 'POST':
        nombre = program.nombre
        try:
            program.delete()
            messages.success(request, f'Programa "{nombre}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar programa: {str(e)}')
    
    return redirect('dashboard_radio')

#crud operations for news
@login_required
@user_passes_test(is_staff_user)
def create_news(request):
    """crear nueva noticia"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria = request.POST.get('categoria')
        imagen_url = request.POST.get('imagen_url')
        publicado = request.POST.get('publicado') == 'on'
        
        try:
            #obtener categoría de noticias
            categoria_noticias = Categoria.objects.get_or_create(nombre='Noticias')[0]
            
            #crear artículo de noticias
            news = Articulo.objects.create(
                titulo=titulo,
                contenido=contenido,
                categoria=categoria_noticias,
                imagen_url=imagen_url,
                publicado=publicado,
                autor=request.user
            )
            messages.success(request, f'Noticia "{titulo}" creada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear noticia: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_news(request, news_id):
    """eliminar noticia"""
    news = get_object_or_404(Articulo, id=news_id)
    
    if request.method == 'POST':
        titulo = news.titulo
        try:
            news.delete()
            messages.success(request, f'Noticia "{titulo}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar noticia: {str(e)}')
    
    return redirect('dashboard_radio')

#estado crud
@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_estado(request):
    """agregar un nuevo estado, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')
    tipo_entidad = request.POST.get('tipo_entidad')

    if not nombre or not tipo_entidad:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre y tipo de estado son obligatorios.'}, status=400)
        messages.error(request, 'El nombre y tipo de estado son obligatorios.')
        return redirect('dashboard_emergentes')

    try:
        if Estado.objects.filter(nombre__iexact=nombre, tipo_entidad=tipo_entidad).exists():
            message = f'El estado "{nombre}" ya existe para {tipo_entidad}.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            estado = Estado.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo_entidad=tipo_entidad
            )
            message = f'Estado "{estado.nombre}" creado exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'estado': {
                        'id': estado.id,
                        'nombre': estado.nombre,
                        'descripcion': estado.descripcion,
                        'tipo_entidad': estado.tipo_entidad
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear el estado: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)
    return redirect('dashboard_emergentes')

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_estado(request, estado_id):
    """eliminar un estado, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    next_url = request.META.get('HTTP_REFERER')

    try:
        estado = get_object_or_404(Estado, id=estado_id)
        nombre_estado = estado.nombre

        #verificar si hay elementos usando este estado
        if estado.tipo_entidad == 'contacto' and estado.contactos.exists():
            message = f'No se puede eliminar el estado "{nombre_estado}" porque está siendo usado por contactos.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect(next_url or 'dashboard_emergentes')

        if estado.tipo_entidad == 'banda' and BandaEmergente.objects.filter(estado=estado).exists():
            message = f'No se puede eliminar el estado "{nombre_estado}" porque está siendo usado por bandas.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect(next_url or 'dashboard_emergentes')

        estado.delete()
        message = f'Estado "{nombre_estado}" eliminado correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar el estado: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect(next_url or 'dashboard_emergentes')

#chat moderation
@login_required
@user_passes_test(is_staff_user)
def delete_message(request, message_id):
    """eliminar mensaje del chat"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(ChatMessage, id=message_id)
            message.delete()
            messages.success(request, 'Mensaje eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar el mensaje: {str(e)}')
    
    return redirect('dashboard_chat')

@login_required
@user_passes_test(is_staff_user)
def update_station(request):
    """actualizar configuracion de la estación"""
    station = EstacionRadio.objects.first()
    
    if request.method == 'POST':
        station.nombre = request.POST.get('nombre', station.nombre)
        station.descripcion = request.POST.get('descripcion', station.descripcion)
        station.stream_url = request.POST.get('stream_url', station.stream_url)
        station.live_stream_url = request.POST.get('live_stream_url', station.live_stream_url)
        station.activo = request.POST.get('activo') == 'on'
        #actualizar otros campos si existen en el formulario
        station.telefono = request.POST.get('telefono', station.telefono)
        station.email = request.POST.get('email', station.email)
        station.direccion = request.POST.get('direccion', station.direccion)
        
        station.save()
        messages.success(request, 'Configuración de estación actualizada exitosamente')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def toggle_station_status(request):
    """alternar el estado de la estación (activo/inactivo)"""
    if request.method == 'POST':
        try:
            station = EstacionRadio.objects.first()
            if station:
                station.activo = not station.activo
                station.save()
                status = 'activa' if station.activo else 'en pausa'
                messages.success(request, f'La transmisión está ahora {status}')
            else:
                messages.error(request, 'No se encontró la estación de radio')
        except Exception as e:
            messages.error(request, f'Error al cambiar el estado: {str(e)}')
    
    return redirect('dashboard_radio')

#===============================
#bandas emergentes (crud + estado)
#===============================
@login_required
@user_passes_test(is_staff_user)
def get_comunas_ajax(request):
    """vista para obtener las comunas de una región mediante ajax"""
    region_id = request.GET.get('region_id')
    if region_id:
        comunas = Comuna.objects.filter(region_id=region_id).order_by('nombre')
        data = {
            'comunas': [{'id': c.id, 'nombre': c.nombre} for c in comunas]
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'No se proporcionó el ID de la región'}, status=400)

@login_required
@user_passes_test(is_staff_user)
def crear_banda_emergente(request):
    """vista para crear una nueva banda emergente"""
    if request.method == 'POST':
        form = BandaEmergenteForm(request.POST, request.FILES)
        if form.is_valid():
            banda = form.save(commit=False)
            banda.usuario = request.user
            banda.save()
            messages.success(request, 'Banda creada exitosamente')
            return redirect('dashboard_emergentes')
    else:
        form = BandaEmergenteForm()
    
    return render(request, 'dashboard/emergentes/form_banda.html', {
        'form': form,
        'titulo': 'Nueva Banda Emergente'
    })

@login_required
@user_passes_test(is_staff_user)
def editar_banda_emergente(request, banda_id):
    """vista para editar una banda emergente existente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    
    if request.method == 'POST':
        form = BandaEmergenteForm(request.POST, request.FILES, instance=banda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banda actualizada exitosamente')
            return redirect('dashboard_emergentes')
    else:
        form = BandaEmergenteForm(instance=banda)
    
    return render(request, 'dashboard/emergentes/form_banda.html', {
        'form': form,
        'titulo': f'Editar {banda.nombre_banda}'
    })

@login_required
@user_passes_test(is_staff_user)
def dashboard_emergentes(request):
    """gestion de bandas emergentes"""
    #obtener todas las bandas con sus relaciones
    bandas = BandaEmergente.objects.select_related(
        'genero', 'usuario', 'estado', 'comuna', 'comuna__ciudad', 'comuna__ciudad__pais'
    ).prefetch_related('integrantes__integrante', 'links').order_by('-fecha_envio')
    
    #filtros
    estado = request.GET.get('estado')
    genero = request.GET.get('genero')
    busqueda = request.GET.get('q')
    
    if estado:
        bandas = bandas.filter(estado__nombre=estado)
    
    if genero:
        bandas = bandas.filter(genero_id=genero)
    
    if busqueda:
        bandas = bandas.filter(
            Q(nombre_banda__icontains=busqueda) |
            Q(email_contacto__icontains=busqueda) |
            Q(comuna__nombre__icontains=busqueda) |
            Q(comuna__ciudad__nombre__icontains=busqueda)
        )
    
    #obtener estadisticas de estados para el filtro
    stats_estados = BandaEmergente.objects.values('estado__nombre').annotate(
        total=Count('id')
    ).order_by('estado__nombre')

    #convertir a diccionario para el template
    stats_estados = {item['estado__nombre']: item['total'] for item in stats_estados}

    #obtener top géneros musicales (top 5)
    top_generos = BandaEmergente.objects.values('genero__nombre').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    #paginacion
    paginator = Paginator(bandas, 10)  # 10 bandas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #obtener todos los géneros para el filtro y la gestion
    generos = GeneroMusical.objects.all().order_by('nombre')

    context = {
        'bandas': page_obj,
        'total_bandas': paginator.count,
        'estados': Estado.objects.all().order_by('tipo_entidad', 'nombre'),
        'generos': generos,
        'estado_actual': estado,
        'genero_actual': int(genero) if genero and genero.isdigit() else None,
        'busqueda': busqueda or '',
        'stats_estados': stats_estados,
        'top_generos': top_generos,
    }
    
    return render(request, 'dashboard/emergente.html', context)

@login_required
@user_passes_test(is_staff_user)
def cambiar_estado_banda(request, banda_id, nuevo_estado):
    """cambiar el estado de una banda y registrar quién lo revisó"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    
    try:
        #mapeo de estados (de la url a los nombres en la bd)
        estados_mapping = {
            'pendiente': 'Pendiente',
            'aprobado': 'Aprobado', 
            'rechazado': 'Rechazado',
            'revision': 'Revisado'
        }
        
        #buscar el estado en la tabla estado
        nombre_estado = estados_mapping.get(nuevo_estado.lower(), nuevo_estado)
        estado_obj = Estado.objects.get(
            nombre=nombre_estado,
            tipo_entidad='banda'
        )
        
        #actualizar estado y registrar quién lo revisó
        banda.estado = estado_obj
        banda.revisado_por = request.user
        banda.fecha_revision = timezone.now()
        banda.save()
        
        messages.success(request, f"Estado de '{banda.nombre_banda}' actualizado a {estado_obj.nombre}.")
    except Estado.DoesNotExist:
        messages.error(request, f"Estado '{nuevo_estado}' no encontrado.")
    except Exception as e:
        messages.error(request, f"Error al actualizar estado: {str(e)}")
    
    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
def view_banda(request, banda_id):
    """ver detalle completo de una banda emergente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    return render(request, 'dashboard/emergente_detail.html', {'banda': banda})


@login_required
@user_passes_test(is_staff_user)
def eliminar_banda_emergente(request, banda_id):
    """eliminar banda emergente"""
    if request.method != 'POST':
        return redirect('dashboard_emergentes')

    try:
        banda = BandaEmergente.objects.get(id=banda_id)
        nombre_banda = banda.nombre_banda
        banda.delete()
        messages.success(request, f'Banda "{nombre_banda}" eliminada correctamente.')
    except BandaEmergente.DoesNotExist:
        messages.error(request, 'La banda no existe.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')

    return redirect('dashboard_emergentes')


#las vistas para crear y editar bandas emergentes se manejarán en el frontend
@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_genero(request):
    """agregar un nuevo género musical, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')

    if not nombre:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre del género es obligatorio.'}, status=400)
        messages.error(request, 'El nombre del género es obligatorio.')
        return redirect('dashboard_emergentes')

    try:
        if GeneroMusical.objects.filter(nombre__iexact=nombre).exists():
            message = f'El género "{nombre}" ya existe.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            genero = GeneroMusical.objects.create(nombre=nombre, descripcion=descripcion)
            message = f'Género "{genero.nombre}" creado exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'genero': {
                        'id': genero.id,
                        'nombre': genero.nombre,
                        'descripcion': genero.descripcion
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear el género: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_genero(request, genero_id):
    """eliminar un género musical, con soporte para ajax y fallback"""
    is_ajax = request.headers.get('X-Requested-with') == 'XMLHttpRequest'

    try:
        genero = get_object_or_404(GeneroMusical, id=genero_id)
        nombre_genero = genero.nombre
        genero.delete()
        message = f'Género "{nombre_genero}" eliminado correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar el género: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)
    
    return redirect('dashboard_emergentes')


#===============================
#contactos (crud + estado)
#===============================
@login_required
@user_passes_test(is_staff_user)
def dashboard_contactos(request):
    """gestion de contactos"""
    #obtener parametros de filtro
    estado_filter = request.GET.get('estado')
    tipo_filter = request.GET.get('tipo')
    search_query = request.GET.get('q')

    #query base
    contactos = Contacto.objects.select_related(
        'tipo_asunto', 'estado', 'usuario', 'respondido_por'
    ).order_by('-fecha_envio')

    #aplicar filtros
    if estado_filter:
        contactos = contactos.filter(estado_id=estado_filter)
    if tipo_filter:
        contactos = contactos.filter(tipo_asunto_id=tipo_filter)
    if search_query:
        contactos = contactos.filter(
            Q(nombre__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mensaje__icontains=search_query)
        )

    #estadisticas
    total_contactos = Contacto.objects.count()

    #contactos pendientes (estado recibida o pendiente)
    contactos_pendientes = Contacto.objects.filter(
        Q(estado__nombre__iexact='Recibida') | Q(estado__nombre__iexact='Pendiente')
    ).count()

    #contactos respondidos
    contactos_respondidos = Contacto.objects.filter(
        estado__nombre__iexact='Respondida'
    ).count()

    #contactos de esta semana
    last_week = timezone.now() - timedelta(days=7)
    contactos_semana = Contacto.objects.filter(fecha_envio__gte=last_week).count()

    #paginacion
    paginator = Paginator(contactos, 10)  # 10 contactos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #obtener estados y tipos de asunto disponibles
    estados_disponibles = Estado.objects.all().order_by('nombre')
    tipos_asunto = TipoAsunto.objects.all().order_by('nombre')

    # estados para la sección "Gestión de estados" (contactos y bandas)
    estados = Estado.objects.all().order_by('tipo_entidad', 'nombre')

    context = {
        'contactos': page_obj,
        'page_obj': page_obj,
        'total_contactos': total_contactos,
        'contactos_pendientes': contactos_pendientes,
        'contactos_respondidos': contactos_respondidos,
        'contactos_semana': contactos_semana,
        'estados_disponibles': estados_disponibles,
        'tipos_asunto': tipos_asunto,
        'estados': estados,
  #añadido para la gestion de estados
    }

    return render(request, 'dashboard/contactos.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_contacto(request, contacto_id):
    """actualizar estado de un contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)

    if request.method == 'POST':
        nuevo_estado_id = request.POST.get('estado')

        try:
            nuevo_estado = Estado.objects.get(id=nuevo_estado_id)
            contacto.estado = nuevo_estado

            #si el estado es "respondida", marcar fecha y usuario
            if nuevo_estado.nombre.lower() == 'respondida':
                contacto.fecha_respuesta = timezone.now()
                contacto.respondido_por = request.user

            contacto.save()
            messages.success(request, f"Estado del contacto actualizado a '{nuevo_estado.nombre}'.")
        except Estado.DoesNotExist:
            messages.error(request, "Estado no encontrado.")
        except Exception as e:
            messages.error(request, f"Error al actualizar contacto: {str(e)}")

    return redirect('dashboard_contactos')


@login_required
@user_passes_test(is_staff_user)
def agregar_tipo_asunto(request):
    """agregar un nuevo tipo de asunto, con soporte para ajax y fallback"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El nombre del tipo de asunto es requerido'}, status=400)
            messages.error(request, 'El nombre del tipo de asunto es requerido.')
            return redirect('dashboard_contactos')
        
        try:
            #verificar si ya existe un tipo con el mismo nombre
            if TipoAsunto.objects.filter(nombre__iexact=nombre).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Ya existe un tipo de asunto con este nombre'}, status=400)
                messages.error(request, 'Ya existe un tipo de asunto con este nombre.')
                return redirect('dashboard_contactos')
            
            #crear el nuevo tipo de asunto
            tipo = TipoAsunto.objects.create(
                nombre=nombre,
                descripcion=descripcion if descripcion else None
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'tipo': {
                        'id': tipo.id,
                        'nombre': tipo.nombre,
                        'descripcion': tipo.descripcion or ''
                    }
                })
            
            messages.success(request, f'Tipo de asunto "{tipo.nombre}" agregado correctamente.')
            return redirect('dashboard_contactos')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Error al agregar el tipo de asunto: {str(e)}')
            return redirect('dashboard_contactos')
    
    #si no es una petición post, redirigir al dashboard
    return redirect('dashboard_contactos')


@login_required
@user_passes_test(is_staff_user)
def eliminar_tipo_asunto(request, tipo_id):
    """eliminar un tipo de asunto, con soporte para ajax y fallback. si hay contactos usando este tipo, se les asignará un tipo por defecto"""
    if request.method != 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
        messages.error(request, 'Método no permitido.')
        return redirect('dashboard_contactos')
    
    try:
        #obtener el tipo de asunto
        tipo = TipoAsunto.objects.get(id=tipo_id)
        nombre_tipo = tipo.nombre
        
        #obtener el primer tipo de asunto que no sea el actual
        tipo_por_defecto = TipoAsunto.objects.exclude(id=tipo_id).first()
        
        #si hay contactos usando este tipo, actualizarlos al tipo por defecto
        if Contacto.objects.filter(tipo_asunto=tipo).exists():
            if not tipo_por_defecto:
                error_msg = 'No se puede eliminar el tipo de asunto porque es el único existente.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('dashboard_contactos')
            
            #actualizar los contactos al tipo por defecto
            Contacto.objects.filter(tipo_asunto=tipo).update(tipo_asunto=tipo_por_defecto)
        
        #eliminar el tipo de asunto
        tipo.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, f'Tipo de asunto "{nombre_tipo}" eliminado correctamente.')
        return redirect('dashboard_contactos')
        
    except TipoAsunto.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El tipo de asunto no existe'}, status=404)
        messages.error(request, 'El tipo de asunto no existe.')
        return redirect('dashboard_contactos')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        messages.error(request, f'Error al eliminar el tipo de asunto: {str(e)}')
        return redirect('dashboard_contactos')


@login_required
@user_passes_test(is_staff_user)
def delete_contacto(request, contacto_id):
    """eliminar un contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)

    if request.method == 'POST':
        nombre = contacto.nombre
        try:
            contacto.delete()
            messages.success(request, f"Contacto de '{nombre}' eliminado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar contacto: {str(e)}")

    return redirect('dashboard_contactos')

#============================================
#notificaciones
#============================================

@login_required
@user_passes_test(is_staff_user)
def dashboard_notificaciones(request):
    """vista principal de notificaciones"""
    from apps.notifications.models import Notification
    
    #obtener filtros
    filtro_tipo = request.GET.get('tipo', '')
    filtro_leidas = request.GET.get('leidas', '')
    
    #query base - solo notificaciones del usuario actual
    notificaciones = Notification.objects.filter(usuario=request.user).order_by("-fecha_creacion")
    
    #aplicar filtros
    if filtro_tipo:
        notificaciones = notificaciones.filter(tipo=filtro_tipo)
    
    if filtro_leidas == 'si':
        notificaciones = notificaciones.filter(leido=True)
    elif filtro_leidas == 'no':
        notificaciones = notificaciones.filter(leido=False)
    
    #paginacion
    paginator = Paginator(notificaciones, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    #estadisticas
    total_notificaciones = notificaciones.count()
    no_leidas = notificaciones.filter(leido=False).count()
    leidas = notificaciones.filter(leido=True).count()

    context = {
        'page_obj': page_obj,
        'filtro_tipo': filtro_tipo,
        'filtro_leidas': filtro_leidas,
        'total_notificaciones': total_notificaciones,
        'no_leidas': no_leidas,
        'leidas': leidas,
    }
    
    return render(request, 'dashboard/notificaciones.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def marcar_notificacion_leida(request, notificacion_id):
    """marcar una notificacion como leída"""
    from apps.notifications.models import Notification
    
    notificacion = get_object_or_404(Notification, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('dashboard_notificaciones')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def eliminar_notificacion(request, notificacion_id):
    """eliminar una notificacion"""
    from apps.notifications.models import Notification
    
    notificacion = get_object_or_404(Notification, id=notificacion_id, usuario=request.user)
    notificacion.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notificación eliminada exitosamente.')
    return redirect('dashboard_notificaciones')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def marcar_todas_leidas(request):
    """marcar todas las notificaciones como leídas"""
    from apps.notifications.models import Notification
    
    count = Notification.objects.filter(usuario=request.user, leido=False).update(leido=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count})
    
    messages.success(request, f'{count} notificaciones marcadas como leídas.')
    return redirect('dashboard_notificaciones')

@login_required
def api_get_calendar_events(request):
    
    #1. id del calendario
    CALENDAR_ID = '7505ae36af692d9dc952769cb67cb09e5624f1c041e7e99c0c7efb2928b345b0@group.calendar.google.com' 

    #2. ruta a credenciales
    CREDENTIALS_FILE = settings.BASE_DIR / 'google-credentials.json'

    #3. permisos
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    print(f"[DEBUG] Intentando cargar calendario: {CALENDAR_ID}")
    print(f"[DEBUG] Buscando credenciales en: {CREDENTIALS_FILE}")

    try:
        #carga las credenciales del archivo json
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        print("[DEBUG] Credenciales cargadas exitosamente.")

        #construye el servicio de la api
        service = build('calendar', 'v3', credentials=creds)
        print("[DEBUG] Servicio de API de Google construido.")

        #llama a la api
        now = datetime.now(dt_timezone.utc).isoformat()  # 'Z' indica UTC
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        print("[DEBUG] Llamada a la API de Google exitosa.")
        events = events_result.get('items', [])
        print(f"[DEBUG] Encontrados {len(events)} eventos.")

        #formatea los eventos para fullcalendar
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'title': event.get('summary', 'Evento sin título'),
                'start': start,
                'end': end,
                'id': event['id'],
            })

        return JsonResponse(formatted_events, safe=False)

    except Exception as e:
        #--- esta es la parte importante ---
        #¡imprime el error completo en tu terminal de django
        print("="*50)
        print("¡ERROR! Falló la API de Google Calendar:")
 #esto imprimira el error rojo
        print("="*50)
        #-----------------------------------
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_track_impression(request, campania_id):
    """registra una impresión para una campaña de publicidad web"""
    from apps.publicidad.models import PublicidadWeb
    
    try:
        with transaction.atomic():
            #bloquea el registro para actualización
            campania = PublicidadWeb.objects.select_for_update().get(
                publicidad_id=campania_id,
                publicidad__tipo='WEB',
                publicidad__activo=True
            )
            campania.impresiones = F('impresiones') + 1
            campania.save(update_fields=['impresiones'])
            #obtener el valor actualizado desde la bd
            campania.refresh_from_db(fields=['impresiones'])
            
            #registrar la impresión en el log
            print(f"[PUBLICIDAD] Impresión registrada para campaña {campania_id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Impresión registrada correctamente',
                'nuevo_total': int(campania.impresiones)
            })
            
    except PublicidadWeb.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Campaña no encontrada o inactiva'}, 
            status=404
        )
    except Exception as e:
        print(f"[ERROR] Error al registrar impresión: {str(e)}")
        return JsonResponse(
            {'success': False, 'message': 'Error al registrar la impresión'}, 
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def api_track_click(request, campania_id):
    """registra un clic para una campaña de publicidad web"""
    from apps.publicidad.models import PublicidadWeb
    
    try:
        with transaction.atomic():
            #bloquea el registro para actualización
            campania = PublicidadWeb.objects.select_for_update().get(
                publicidad_id=campania_id,
                publicidad__tipo='WEB',
                publicidad__activo=True
            )
            campania.clics = F('clics') + 1
            campania.save(update_fields=['clics'])
            #obtener el valor actualizado desde la bd
            campania.refresh_from_db(fields=['clics'])
            
            #registrar el clic en el log
            print(f"[PUBLICIDAD] Clic registrado para campaña {campania_id}")
            
            #devolver la url de destino para redirección en el frontend
            return JsonResponse({
                'success': True,
                'redirect_url': campania.url_destino,
                'nuevo_total': int(campania.clics)
            })
            
    except PublicidadWeb.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Campaña no encontrada o inactiva'}, 
            status=404
        )
    except Exception as e:
        print(f"[ERROR] Error al registrar clic: {str(e)}")
        return JsonResponse(
            {'success': False, 'message': 'Error al registrar el clic'}, 
            status=500
        )


#========================
#suscripciones
#========================

@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_suscripciones(request):
    """gestion de suscripciones al newsletter"""
    #parametros de filtro
    estado_filter = request.GET.get('estado')  # 'activa' o 'inactiva'
    search_query = request.GET.get('q')

    #query base
    suscripciones = Suscripcion.objects.select_related('usuario').order_by('-fecha_suscripcion')

    #aplicar filtros
    if estado_filter == 'activa':
        suscripciones = suscripciones.filter(activa=True)
    elif estado_filter == 'inactiva':
        suscripciones = suscripciones.filter(activa=False)

    if search_query:
        suscripciones = suscripciones.filter(
            Q(nombre__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    #paginacion
    paginator = Paginator(suscripciones, 10)  # 10 suscripciones por página
    page_number = request.GET.get('page', 1)
    suscripciones_page = paginator.get_page(page_number)

    #estadisticas
    total_suscripciones = Suscripcion.objects.count()
    suscripciones_activas = Suscripcion.objects.filter(activa=True).count()
    suscripciones_inactivas = Suscripcion.objects.filter(activa=False).count()

    #suscripciones de esta semana
    last_week = timezone.now() - timedelta(days=7)
    suscripciones_semana = Suscripcion.objects.filter(fecha_suscripcion__gte=last_week).count()

    #bajas de esta semana
    bajas_semana = Suscripcion.objects.filter(
        activa=False,
        fecha_baja__isnull=False,
        fecha_baja__gte=last_week
    ).count()

    context = {
        'suscripciones': suscripciones_page,
        'total_suscripciones': total_suscripciones,
        'suscripciones_activas': suscripciones_activas,
        'suscripciones_inactivas': suscripciones_inactivas,
        'suscripciones_semana': suscripciones_semana,
        'bajas_semana': bajas_semana,
        'estado_filter': estado_filter,
        'search_query': search_query,
    }

    return render(request, 'dashboard/suscripciones.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["POST"])
def toggle_suscripcion(request, suscripcion_id):
    """activar/desactivar una suscripcion"""
    suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id)

    if suscripcion.activa:
        suscripcion.activa = False
        suscripcion.fecha_baja = timezone.now()
        messages.success(request, f'Suscripción de {suscripcion.email} desactivada')
    else:
        suscripcion.activa = True
        suscripcion.fecha_baja = None
        messages.success(request, f'Suscripción de {suscripcion.email} reactivada')

    suscripcion.save()
    return redirect('dashboard_suscripciones')

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["POST"])
def delete_suscripcion(request, suscripcion_id):
    """eliminar una suscripcion permanentemente"""
    suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id)
    email = suscripcion.email
    suscripcion.delete()
    messages.success(request, f'Suscripción de {email} eliminada permanentemente')
    return redirect('dashboard_suscripciones')

@login_required
@user_passes_test(is_staff_user)
def crear_conductor(request):
    """muestra el formulario para crear un nuevo conductor"""
    if request.method == 'POST':
        form = ConductorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conductor creado exitosamente.')
            return redirect('dashboard_radio')
        else:
            messages.error(request, 'Error al crear el conductor. Revisa el formulario.')
    else:
        form = ConductorForm()

    context = {
        'form': form,
        'page_title': 'Nuevo Conductor'
    }
    return render(request, 'dashboard/conductor_form.html', context)


@login_required
@user_passes_test(is_staff_user)
def editar_conductor(request, conductor_id):
    """edita un conductor existente"""
    conductor = get_object_or_404(Conductor, id=conductor_id)

    if request.method == 'POST':
        #si el formulario se envió
        form = ConductorForm(request.POST, request.FILES, instance=conductor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conductor actualizado exitosamente.')
 #vuelve a la pagina de radio
        else:
            messages.error(request, 'Error al actualizar. Revisa el formulario.')
    else:
        form = ConductorForm(instance=conductor) 

    context = {
        'form': form,
        'page_title': f'Editar Conductor: {conductor.nombre}'
    }
    return render(request, 'dashboard/conductor_form.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_POST
def toggle_activo_conductor(request, conductor_id):
    """activa o desactiva un conductor"""
    conductor = get_object_or_404(Conductor, id=conductor_id)

    conductor.activo = not conductor.activo
    conductor.save()

    if conductor.activo:
        messages.success(request, f'Conductor "{conductor.nombre}" activado.')
    else:
        messages.warning(request, f'Conductor "{conductor.nombre}" desactivado.')

    return redirect('dashboard_radio')


@login_required
@user_passes_test(is_staff_user)
@require_POST
def eliminar_conductor(request, conductor_id):
    """elimina un conductor"""
    conductor = get_object_or_404(Conductor, id=conductor_id)
    nombre_conductor = conductor.nombre

    conductor.delete()

    messages.error(request, f'Conductor "{nombre_conductor}" eliminado permanentemente.')
    return redirect('dashboard_radio')


def dashboard_password_reset(request):
    """vista para solicitar recuperación de contraseña desde el dashboard"""
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            #generar token de reseteo
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode
            from django.core.mail import send_mail

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            #construir url de reseteo para el frontend
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{frontend_url}/resetear-contrasena/{uid}/{token}"

            #enviar correo electrónico
            subject = 'Recuperación de Contraseña - Radio Oriente FM Dashboard'
            message = f"""hola {user.first_name or user.username}, recibimos una solicitud para restablecer tu contraseña del dashboard de radio oriente fm. para crear una nueva contraseña, haz clic en el siguiente enlace: {reset_url} este enlace expirará en 24 horas. si no solicitaste este cambio, puedes ignorar este correo electrónico y tu contraseña permanecerá sin cambios. saludos, el equipo de radio oriente fm"""

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return render(request, 'dashboard/password_reset.html', {
                    'success': True,
                    'message': 'Se ha enviado un correo electrónico con instrucciones para restablecer tu contraseña.'
                })
            except Exception as e:
                return render(request, 'dashboard/password_reset.html', {
                    'error': f'Error al enviar el correo: {str(e)}'
                })

        except User.DoesNotExist:
            #por seguridad, mostrar el mismo mensaje aunque el email no exista
            return render(request, 'dashboard/password_reset.html', {
                'success': True,
                'message': 'Si el correo existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña.'
            })

    return render(request, 'dashboard/password_reset.html')

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def api_subir_imagen_campania(request):
    """api para subir imágenes de campañas de publicidad"""
    import os
    import uuid
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    from django.conf import settings
    
    try:
        if 'imagen' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No se envió ningún archivo'}, status=400)
        
        imagen = request.FILES['imagen']
        
        #validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if imagen.content_type not in allowed_types:
            return JsonResponse({
                'success': False, 
                'message': 'Tipo de archivo no permitido. Solo se permiten imágenes (JPEG, PNG, GIF, WebP)'
            }, status=400)
        
        #validar tamaño (máximo 5mb)
        if imagen.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False, 
                'message': 'El archivo es demasiado grande. Máximo 5MB'
            }, status=400)
        
        #generar nombre unico para el archivo
        ext = os.path.splitext(imagen.name)[1].lower()
        filename = f"campania_{uuid.uuid4().hex}{ext}"
        
        #crear directorio si no existe
        upload_path = os.path.join('publicidad', 'campanias')
        full_path = os.path.join(upload_path, filename)
        
        #guardar archivo
        saved_path = default_storage.save(full_path, ContentFile(imagen.read()))
        
        #construir url completa
        file_url = default_storage.url(saved_path)
        
        return JsonResponse({
            'success': True,
            'url': file_url,
            'filename': filename,
            'message': 'Imagen subida correctamente'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al subir la imagen: {str(e)}'
        }, status=500)