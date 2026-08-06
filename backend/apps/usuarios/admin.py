from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, AuditoriaAccion


@admin.register(AuditoriaAccion)
class AuditoriaAccionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'ip', 'fecha']
    list_filter = ['accion', 'fecha']
    search_fields = ['usuario__username', 'accion', 'detalle', 'ip']
    readonly_fields = ['usuario', 'accion', 'detalle', 'ip', 'fecha']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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
