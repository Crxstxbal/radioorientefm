from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from apps.users.models import User, Role
from apps.blog.models import BlogPost, BlogComment
from apps.radio.models import Program, News, RadioStation
from apps.chat.models import ChatMessage
from apps.contact.models import ContactMessage, Subscription

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """Dashboard principal con métricas generales"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_posts = BlogPost.objects.count()
    total_programs = Program.objects.count()
    total_subscriptions = Subscription.objects.count()
    
    # Estadísticas de la última semana
    last_week = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(fecha_creacion__gte=last_week).count()
    new_posts_week = BlogPost.objects.filter(fecha_creacion__gte=last_week).count()
    new_messages_week = ChatMessage.objects.filter(fecha_envio__gte=last_week).count()
    
    # Artículos más populares (por fecha de publicación reciente)
    popular_posts = BlogPost.objects.filter(publicado=True).order_by('-fecha_publicacion')[:5]
    
    # Mensajes de contacto recientes
    recent_contacts = ContactMessage.objects.order_by('-fecha_envio')[:5]
    
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
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """Gestión de usuarios"""
    users = User.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/users.html', {'users': users})

@login_required
@user_passes_test(is_staff_user)
def dashboard_blog(request):
    """Gestión del blog"""
    posts = BlogPost.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/blog.html', {'posts': posts})

@login_required
@user_passes_test(is_staff_user)
def dashboard_radio(request):
    """Gestión de radio y programas"""
    programs = Program.objects.all().order_by('hora_inicio')
    news = News.objects.all().order_by('-fecha_creacion')[:10]
    try:
        station = RadioStation.objects.first()
    except RadioStation.DoesNotExist:
        station = None
    
    context = {
        'programs': programs,
        'news': news,
        'station': station,
    }
    return render(request, 'dashboard/radio.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_chat(request):
    """Moderación del chat"""
    messages = ChatMessage.objects.all().order_by('-fecha_envio')[:50]
    return render(request, 'dashboard/chat.html', {'messages': messages})

@login_required
@user_passes_test(is_staff_user)
def dashboard_analytics(request):
    """Analytics y estadísticas detalladas"""
    # Datos para gráficos
    last_30_days = timezone.now() - timedelta(days=30)
    
    # Usuarios por día (últimos 30 días)
    users_by_day = []
    for i in range(30):
        date = timezone.now() - timedelta(days=i)
        count = User.objects.filter(fecha_creacion__date=date.date()).count()
        users_by_day.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    # Posts por mes (últimos 6 meses)
    posts_by_month = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        count = BlogPost.objects.filter(
            fecha_creacion__year=date.year,
            fecha_creacion__month=date.month
        ).count()
        posts_by_month.append({'month': date.strftime('%Y-%m'), 'count': count})
    
    context = {
        'users_by_day': users_by_day,
        'posts_by_month': posts_by_month,
    }
    
    return render(request, 'dashboard/analytics.html', context)

def dashboard_login(request):
    """Login específico para el dashboard"""
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
    """Logout del dashboard"""
    logout(request)
    return redirect('dashboard_login')

@login_required
@user_passes_test(is_staff_user)
def api_dashboard_stats(request):
    """API endpoint para estadísticas del dashboard"""
    stats = {
        'users': User.objects.count(),
        'posts': BlogPost.objects.count(),
        'programs': Program.objects.count(),
        'messages': ChatMessage.objects.count(),
        'subscriptions': Subscription.objects.count(),
    }
    return JsonResponse(stats)

# CRUD Operations for Users
@login_required
@user_passes_test(is_staff_user)
def create_user(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        try:
            user = User.objects.create_user(
                correo=correo,
                usuario=usuario,
                password=password,
                nombre=nombre,
                is_staff=is_staff
            )
            messages.success(request, f'Usuario {usuario} creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def edit_user(request, user_id):
    """Editar usuario existente"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.nombre = request.POST.get('nombre')
        user.usuario = request.POST.get('usuario')
        user.correo = request.POST.get('correo')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        try:
            user.save()
            messages.success(request, f'Usuario {user.usuario} actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def delete_user(request, user_id):
    """Eliminar usuario"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.usuario
        try:
            user.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
    
    return redirect('dashboard_users')

# CRUD Operations for Blog Posts
@login_required
@user_passes_test(is_staff_user)
def create_post(request):
    """Crear nuevo artículo del blog"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        resumen = request.POST.get('resumen')
        categoria = request.POST.get('categoria')
        tags = request.POST.get('tags')
        publicado = request.POST.get('publicado') == 'on'
        imagen_url = request.POST.get('imagen_url')
        
        try:
            post = BlogPost.objects.create(
                titulo=titulo,
                contenido=contenido,
                resumen=resumen,
                categoria=categoria,
                tags=tags,
                publicado=publicado,
                imagen_url=imagen_url,
                autor_id=request.user.id,
                autor_nombre=request.user.nombre
            )
            messages.success(request, f'Artículo "{titulo}" creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear artículo: {str(e)}')
    
    return redirect('dashboard_blog')

@login_required
@user_passes_test(is_staff_user)
def edit_post(request, post_id):
    """Editar artículo del blog"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post.titulo = request.POST.get('titulo')
        post.contenido = request.POST.get('contenido')
        post.resumen = request.POST.get('resumen')
        post.categoria = request.POST.get('categoria')
        post.tags = request.POST.get('tags')
        post.publicado = request.POST.get('publicado') == 'on'
        post.imagen_url = request.POST.get('imagen_url')
        
        try:
            post.save()
            messages.success(request, f'Artículo "{post.titulo}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar artículo: {str(e)}')
    
    return redirect('dashboard_blog')

@login_required
@user_passes_test(is_staff_user)
def delete_post(request, post_id):
    """Eliminar artículo del blog"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        titulo = post.titulo
        try:
            post.delete()
            messages.success(request, f'Artículo "{titulo}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar artículo: {str(e)}')
    
    return redirect('dashboard_blog')

# CRUD Operations for Radio Programs
@login_required
@user_passes_test(is_staff_user)
def create_program(request):
    """Crear nuevo programa de radio"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        conductor = request.POST.get('conductor')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        dias_semana = request.POST.get('dias_semana')
        activo = request.POST.get('activo') == 'on'
        
        try:
            program = Program.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                conductor=conductor,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                dias_semana=dias_semana,
                activo=activo
            )
            messages.success(request, f'Programa "{nombre}" creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def edit_program(request, program_id):
    """Editar programa de radio"""
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        program.nombre = request.POST.get('nombre')
        program.descripcion = request.POST.get('descripcion')
        program.conductor = request.POST.get('conductor')
        program.hora_inicio = request.POST.get('hora_inicio')
        program.hora_fin = request.POST.get('hora_fin')
        program.dias_semana = request.POST.get('dias_semana')
        program.activo = request.POST.get('activo') == 'on'
        
        try:
            program.save()
            messages.success(request, f'Programa "{program.nombre}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_program(request, program_id):
    """Eliminar programa de radio"""
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        nombre = program.nombre
        try:
            program.delete()
            messages.success(request, f'Programa "{nombre}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar programa: {str(e)}')
    
    return redirect('dashboard_radio')

# CRUD Operations for News
@login_required
@user_passes_test(is_staff_user)
def create_news(request):
    """Crear nueva noticia"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria = request.POST.get('categoria')
        imagen_url = request.POST.get('imagen_url')
        publicado = request.POST.get('publicado') == 'on'
        
        try:
            news = News.objects.create(
                titulo=titulo,
                contenido=contenido,
                categoria=categoria,
                imagen_url=imagen_url,
                publicado=publicado,
                autor_id=request.user.id,
                autor_nombre=request.user.nombre
            )
            messages.success(request, f'Noticia "{titulo}" creada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear noticia: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_news(request, news_id):
    """Eliminar noticia"""
    news = get_object_or_404(News, id=news_id)
    
    if request.method == 'POST':
        titulo = news.titulo
        try:
            news.delete()
            messages.success(request, f'Noticia "{titulo}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar noticia: {str(e)}')
    
    return redirect('dashboard_radio')

# Chat Moderation
@login_required
@user_passes_test(is_staff_user)
def delete_message(request, message_id):
    """Eliminar mensaje del chat"""
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if request.method == 'POST':
        try:
            message.delete()
            messages.success(request, 'Mensaje eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar mensaje: {str(e)}')
    
    return redirect('dashboard_chat')
