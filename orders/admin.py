from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'customer_email',
        'order_date',
        'delivery_date',
        'status',
        'total_amount',
    )

    list_filter = (
        'status',
        'order_date',
    )

    search_fields = (
        'customer_name',
        'customer_email',
    )

    ordering = ('-order_date',)

    inlines = [OrderItemInline]

def save_formset(self, request, form, formset, change):

    with transaction.atomic():

        instances = formset.save(commit=False)

        for instance in instances:

            product = instance.product

            # NEW ORDER
            if instance.pk is None:

                if product.stock < instance.quantity:
                    raise ValidationError(
                        f"Not enough stock for {product.name}. "
                        f"Available: {product.stock}, "
                        f"Requested: {instance.quantity}"
                    )

                instance.price = product.price

                product.stock -= instance.quantity
                product.save()

                instance.save()

            # EXISTING ORDER ITEM
            else:

                old_item = OrderItem.objects.get(pk=instance.pk)

                old_product = old_item.product
                old_quantity = old_item.quantity

                # Restore old stock
                old_product.stock += old_quantity
                old_product.save()

                # Check stock for new quantity
                if product.stock < instance.quantity:
                    raise ValidationError(
                        f"Not enough stock for {product.name}. "
                        f"Available: {product.stock}, "
                        f"Requested: {instance.quantity}"
                    )

                instance.price = product.price

                product.stock -= instance.quantity
                product.save()

                instance.save()

        # Deleted items
        for deleted in formset.deleted_objects:

            product = deleted.product

            product.stock += deleted.quantity
            product.save()

            deleted.delete()

        formset.save_m2m()

        # Calculate order total
        order = form.instance

        total = 0

        for item in order.items.all():
            total += item.quantity * item.price

        order.total_amount = total
        order.save()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )

    search_fields = (
        'product__name',
        'order__customer_name',
    )