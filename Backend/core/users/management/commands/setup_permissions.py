# core/users/management/commands/setup_permissions.py

"""
Comando para configurar permisos completos del sistema CRM+Ecommerce
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.users.models import User
from core.ecommerce.models import Categoria, Producto, Stock, Carrito, CarritoProducto
from core.common.models import Bitacora


class Command(BaseCommand):
    help = 'Configura permisos completos para todos los roles del sistema'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Configurando permisos del sistema CRM+Ecommerce...')
        
        # 1. Crear/obtener grupos
        administrador, _ = Group.objects.get_or_create(name='administrador')
        empleadonivel1, _ = Group.objects.get_or_create(name='empleadonivel1')
        empleadonivel2, _ = Group.objects.get_or_create(name='empleadonivel2')
        cliente, _ = Group.objects.get_or_create(name='cliente')
        
        # 2. Limpiar permisos existentes
        for group in [administrador, empleadonivel1, empleadonivel2, cliente]:
            group.permissions.clear()
        
        # 3. Obtener todos los permisos del sistema
        all_permissions = Permission.objects.all()
        
        # 4. ADMINISTRADOR - TODOS LOS PERMISOS
        administrador.permissions.set(all_permissions)
        self.stdout.write(f'✅ Administrador: {all_permissions.count()} permisos asignados')
        
        # 5. EMPLEADO NIVEL 1 (Supervisor) - Permisos de gestión
        supervisor_perms = Permission.objects.filter(
            content_type__in=ContentType.objects.filter(
                app_label__in=['users', 'ecommerce', 'common']
            )
        ).exclude(
            codename__in=['delete_user', 'add_user']  # No puede crear/eliminar usuarios
        )
        empleadonivel1.permissions.set(supervisor_perms)
        self.stdout.write(f'✅ Supervisor: {supervisor_perms.count()} permisos asignados')
        
        # 6. EMPLEADO NIVEL 2 (Vendedor) - Permisos de venta
        vendedor_perms = Permission.objects.filter(
            content_type__in=ContentType.objects.filter(
                model__in=['producto', 'categoria', 'carrito', 'carritoproducto', 'stock']
            ),
            codename__in=[
                'view_producto', 'change_producto',
                'view_categoria', 
                'view_carrito', 'add_carrito', 'change_carrito',
                'view_carritoproducto', 'add_carritoproducto', 'change_carritoproducto',
                'view_stock', 'change_stock'
            ]
        )
        empleadonivel2.permissions.set(vendedor_perms)
        self.stdout.write(f'✅ Vendedor: {vendedor_perms.count()} permisos asignados')
        
        # 7. CLIENTE - Solo permisos básicos
        cliente_perms = Permission.objects.filter(
            content_type__in=ContentType.objects.filter(
                model__in=['producto', 'categoria', 'carrito', 'carritoproducto']
            ),
            codename__in=[
                'view_producto', 'view_categoria',
                'view_carrito', 'add_carrito', 'change_carrito',
                'view_carritoproducto', 'add_carritoproducto', 'change_carritoproducto'
            ]
        )
        cliente.permissions.set(cliente_perms)
        self.stdout.write(f'✅ Cliente: {cliente_perms.count()} permisos asignados')
        
        # 8. Mostrar resumen de permisos por modelo
        self.stdout.write('\n📊 RESUMEN DE PERMISOS POR MODELO:')
        
        models_info = [
            ('User', User),
            ('Categoria', Categoria),
            ('Producto', Producto),
            ('Stock', Stock),
            ('Carrito', Carrito),
            ('CarritoProducto', CarritoProducto),
            ('Bitacora', Bitacora),
        ]
        
        for model_name, model_class in models_info:
            content_type = ContentType.objects.get_for_model(model_class)
            perms = Permission.objects.filter(content_type=content_type)
            self.stdout.write(f'  📝 {model_name}: {perms.count()} permisos')
            for perm in perms:
                self.stdout.write(f'    - {perm.codename}: {perm.name}')
        
        # 9. Configurar superusuario si existe
        superusers = User.objects.filter(is_superuser=True)
        for superuser in superusers:
            superuser.groups.add(administrador)
            self.stdout.write(f'✅ Superusuario {superuser.username} agregado al grupo administrador')
        
        self.stdout.write('\n🎉 ¡Configuración de permisos completada!')
        self.stdout.write('\n📋 JERARQUÍA DE ROLES:')
        self.stdout.write('  🔴 ADMINISTRADOR: Acceso total al sistema')
        self.stdout.write('  🟡 SUPERVISOR: Gestión de productos, usuarios, reportes')
        self.stdout.write('  🟢 VENDEDOR: Gestión de ventas y productos')
        self.stdout.write('  🔵 CLIENTE: Compras y gestión de carrito')
