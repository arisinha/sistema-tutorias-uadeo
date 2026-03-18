from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'unidad', 'programa_educativo']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Académica', {
            'fields': ('rol', 'unidad', 'programa_educativo', 'telefono')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Académica', {
            'fields': ('rol', 'unidad', 'programa_educativo', 'telefono')
        }),
    )
