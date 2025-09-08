from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('correo', 'usuario', 'nombre', 'is_staff', 'is_active', 'fecha_creacion')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'fecha_creacion')
    search_fields = ('correo', 'usuario', 'nombre')
    ordering = ('correo',)
    
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'usuario', 'first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'fecha_creacion')}),
        ('Rol', {'fields': ('rol_id',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'usuario', 'nombre', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('fecha_creacion',)
