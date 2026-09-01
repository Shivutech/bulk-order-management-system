from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date
from decimal import Decimal

from products.models import Product
from orders.models import Order, OrderItem


class Command(BaseCommand):

    help = 'Create demo historical order data for AI prediction'


    def handle(self, *args, **kwargs):

        product = Product.objects.first()

        if not product:

            self.stdout.write(
                self.style.ERROR(
                    'No product found. Create a product first.'
                )
            )

            return


        historical_data = [

            (date(2026, 1, 10), 20),

            (date(2026, 2, 10), 30),

            (date(2026, 3, 10), 40),

            (date(2026, 4, 10), 50),

            (date(2026, 5, 10), 60),

            (date(2026, 6, 10), 70),

        ]


        with transaction.atomic():

            for order_date, quantity in historical_data:

                order = Order.objects.create(

                    customer_name='Demo Customer',

                    customer_email='demo@example.com',

                    delivery_date=order_date,

                    status='Completed',

                    total_amount=Decimal(
                        quantity
                    ) * product.price

                )


                item = OrderItem.objects.create(

                    order=order,

                    product=product,

                    quantity=quantity,

                    price=product.price

                )


                # Override auto_now_add order date
                Order.objects.filter(
                    id=order.id
                ).update(
                    order_date=order_date
                )


                self.stdout.write(

                    self.style.SUCCESS(

                        f'Created order: '
                        f'{order_date} - '
                        f'{quantity} units'

                    )

                )


        self.stdout.write(

            self.style.SUCCESS(

                'Historical demo data created successfully!'

            )

        )