from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from apps.ecommerce.productos.models import Producto, Categoria, Almacen, ArticuloAlmacen
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seed database with initial product data for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, help='The schema name of the tenant to seed', required=True)

    def handle(self, *args, **options):
        schema_name = options['schema']
        self.stdout.write(f"Seeding data for schema: {schema_name}...")

        try:
            with schema_context(schema_name):
                self.seed_data()
                self.stdout.write(self.style.SUCCESS(f"Successfully seeded data for {schema_name}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {str(e)}"))

    def seed_data(self):
        # 1. Create Categories
        categories_data = [
            {'nombre': 'Electrónica', 'descripcion': 'Dispositivos y gadgets electrónicos'},
            {'nombre': 'Ropa', 'descripcion': 'Moda para hombres y mujeres'},
            {'nombre': 'Hogar', 'descripcion': 'Artículos para el hogar y decoración'},
            {'nombre': 'Deportes', 'descripcion': 'Equipamiento deportivo'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
            categories[cat.nombre] = cat
            if created:
                self.stdout.write(f"Created category: {cat.nombre}")

        # 2. Create Warehouse
        almacen, created = Almacen.objects.get_or_create(
            codigo='MAIN-001',
            defaults={
                'nombre': 'Almacén Principal',
                'direccion': 'Calle Principal 123',
                'telefono': '555-0123'
            }
        )
        if created:
            self.stdout.write(f"Created warehouse: {almacen.nombre}")

        # 3. Create Products
        products_data = [
            {
                'codigo': 'LAP-001',
                'nombre': 'Laptop Pro X1',
                'descripcion': 'Potente laptop para profesionales. Procesador i7, 16GB RAM, 512GB SSD.',
                'precio': Decimal('1200.00'),
                'costo': Decimal('900.00'),
                'categoria': 'Electrónica',
                'peso': Decimal('1.5'),
            },
            {
                'codigo': 'PHN-002',
                'nombre': 'Smartphone Galaxy S25',
                'descripcion': 'Último modelo con cámara de alta resolución y batería de larga duración.',
                'precio': Decimal('999.99'),
                'costo': Decimal('750.00'),
                'categoria': 'Electrónica',
                'peso': Decimal('0.2'),
            },
            {
                'codigo': 'TSH-003',
                'nombre': 'Camiseta Algodón Premium',
                'descripcion': 'Camiseta 100% algodón, suave y duradera. Varios colores.',
                'precio': Decimal('25.00'),
                'costo': Decimal('8.00'),
                'categoria': 'Ropa',
                'peso': Decimal('0.15'),
            },
            {
                'codigo': 'CFM-004',
                'nombre': 'Cafetera Automática',
                'descripcion': 'Prepara el mejor café en casa con solo pulsar un botón.',
                'precio': Decimal('85.50'),
                'costo': Decimal('45.00'),
                'categoria': 'Hogar',
                'peso': Decimal('2.0'),
            },
            {
                'codigo': 'YGM-005',
                'nombre': 'Mat de Yoga',
                'descripcion': 'Mat antideslizante para yoga y pilates.',
                'precio': Decimal('30.00'),
                'costo': Decimal('12.00'),
                'categoria': 'Deportes',
                'peso': Decimal('0.8'),
            },
             {
                'codigo': 'HDP-006',
                'nombre': 'Auriculares Noise Cancelling',
                'descripcion': 'Auriculares inalámbricos con cancelación de ruido activa.',
                'precio': Decimal('250.00'),
                'costo': Decimal('150.00'),
                'categoria': 'Electrónica',
                'peso': Decimal('0.3'),
            },
        ]

        for prod_data in products_data:
            cat_name = prod_data.pop('categoria')
            producto, created = Producto.objects.get_or_create(
                codigo=prod_data['codigo'],
                defaults=prod_data
            )
            
            if created:
                producto.categorias.add(categories[cat_name])
                self.stdout.write(f"Created product: {producto.nombre}")
                
                # Add stock
                stock_qty = random.randint(10, 100)
                ArticuloAlmacen.objects.create(
                    producto=producto,
                    almacen=almacen,
                    cantidad=stock_qty
                )
                self.stdout.write(f"  Added {stock_qty} units to {almacen.nombre}")
            else:
                self.stdout.write(f"Product already exists: {producto.nombre}")
