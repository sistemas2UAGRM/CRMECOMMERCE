from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from apps.ecommerce.productos.models import Producto, Categoria, Almacen, ArticuloAlmacen
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seed database with boutique product data for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str, help='The schema name of the tenant to seed', required=True)

    def handle(self, *args, **options):
        schema_name = options['schema']
        self.stdout.write(f"Seeding boutique data for schema: {schema_name}...")

        try:
            with schema_context(schema_name):
                self.seed_data()
                self.stdout.write(self.style.SUCCESS(f"Successfully seeded boutique data for {schema_name}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {str(e)}"))

    def seed_data(self):
        # 1. Create Categories
        categories_data = [
            {'nombre': 'Vestidos', 'descripcion': 'Vestidos para toda ocasión'},
            {'nombre': 'Blusas', 'descripcion': 'Blusas elegantes y casuales'},
            {'nombre': 'Pantalones', 'descripcion': 'Jeans, pantalones de vestir y más'},
            {'nombre': 'Zapatos', 'descripcion': 'Calzado para dama'},
            {'nombre': 'Accesorios', 'descripcion': 'Joyas, bolsos y complementos'},
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

        # 2. Create Warehouse (Ensure it exists)
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
                'codigo': 'DRS-001',
                'nombre': 'Vestido de Noche Elegante',
                'descripcion': 'Vestido largo de seda negra, perfecto para galas.',
                'precio': Decimal('150.00'),
                'costo': Decimal('80.00'),
                'categoria': 'Vestidos',
                'peso': Decimal('0.5'),
            },
            {
                'codigo': 'DRS-002',
                'nombre': 'Vestido Floral Verano',
                'descripcion': 'Vestido ligero con estampado floral, ideal para el día.',
                'precio': Decimal('45.00'),
                'costo': Decimal('20.00'),
                'categoria': 'Vestidos',
                'peso': Decimal('0.3'),
            },
            {
                'codigo': 'BLS-003',
                'nombre': 'Blusa de Seda Blanca',
                'descripcion': 'Blusa clásica de seda, corte elegante.',
                'precio': Decimal('60.00'),
                'costo': Decimal('30.00'),
                'categoria': 'Blusas',
                'peso': Decimal('0.2'),
            },
            {
                'codigo': 'PNT-004',
                'nombre': 'Jeans Skinny High-Waist',
                'descripcion': 'Jeans ajustados de tiro alto, color azul oscuro.',
                'precio': Decimal('55.00'),
                'costo': Decimal('25.00'),
                'categoria': 'Pantalones',
                'peso': Decimal('0.6'),
            },
            {
                'codigo': 'SHS-005',
                'nombre': 'Tacones Stiletto Rojos',
                'descripcion': 'Tacones de aguja color rojo vibrante.',
                'precio': Decimal('85.00'),
                'costo': Decimal('40.00'),
                'categoria': 'Zapatos',
                'peso': Decimal('0.8'),
            },
             {
                'codigo': 'ACC-006',
                'nombre': 'Collar de Perlas Cultivadas',
                'descripcion': 'Elegante collar de perlas con broche de plata.',
                'precio': Decimal('120.00'),
                'costo': Decimal('60.00'),
                'categoria': 'Accesorios',
                'peso': Decimal('0.1'),
            },
            {
                'codigo': 'ACC-007',
                'nombre': 'Bolso de Mano Cuero',
                'descripcion': 'Bolso de mano en cuero genuino, color camel.',
                'precio': Decimal('180.00'),
                'costo': Decimal('90.00'),
                'categoria': 'Accesorios',
                'peso': Decimal('0.7'),
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
                stock_qty = random.randint(5, 50)
                ArticuloAlmacen.objects.create(
                    producto=producto,
                    almacen=almacen,
                    cantidad=stock_qty
                )
                self.stdout.write(f"  Added {stock_qty} units to {almacen.nombre}")
            else:
                self.stdout.write(f"Product already exists: {producto.nombre}")
