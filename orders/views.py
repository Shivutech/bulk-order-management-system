from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from products.models import Product


def order_list(request):

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    orders = Order.objects.all().order_by('-order_date')

    if search:
        orders = orders.filter(
            customer_name__icontains=search
        )

    if status:
        orders = orders.filter(
            status=status
        )

    return render(
        request,
        'orders/order_list.html',
        {
            'orders': orders,
            'search': search,
            'status': status,
        }
    )


def create_order(request):

    products = Product.objects.all().order_by('name')

    if request.method == 'POST':

        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        delivery_date = request.POST.get('delivery_date')

        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')

        try:

            with transaction.atomic():

                # Create Order
                order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    delivery_date=delivery_date,
                    status='Pending',
                    total_amount=0
                )

                total = 0

                for product_id, quantity in zip(
                    product_ids,
                    quantities
                ):

                    if not product_id or not quantity:
                        continue

                    product = Product.objects.get(
                        id=product_id
                    )

                    quantity = int(quantity)

                    # Stock validation
                    if product.stock < quantity:

                        raise ValidationError(
                            f"Not enough stock for "
                            f"{product.name}. "
                            f"Available: {product.stock}, "
                            f"Requested: {quantity}"
                        )

                    price = product.price

                    # Create OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    # Deduct stock
                    product.stock -= quantity
                    product.save()

                    # Calculate total
                    total += quantity * price

                # Save total
                order.total_amount = total
                order.save()

            messages.success(
                request,
                f'Order #{order.id} created successfully!'
            )

            return redirect('order_list')

        except ValidationError as e:

            messages.error(
                request,
                e.message
            )

        except Exception as e:

            messages.error(
                request,
                f'Error: {e}'
            )

    return render(
        request,
        'orders/create_order.html',
        {
            'products': products
        }
    )
def order_detail(request, id):

    order = Order.objects.prefetch_related(
        'items__product'
    ).get(id=id)

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order
        }
    )


def update_order_status(request, id):

    order = Order.objects.get(id=id)

    if request.method == 'POST':

        status = request.POST.get('status')

        if status in [
            'Pending',
            'Processing',
            'Completed',
            'Cancelled'
        ]:

            order.status = status
            order.save()

    return redirect(
        'order_detail',
        id=order.id
    )