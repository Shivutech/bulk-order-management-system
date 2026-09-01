from django.shortcuts import render
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from ai_prediction.ml_model import predict_demand
from products.models import Product
from orders.models import Order


def dashboard(request):

    # Basic statistics

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    pending_orders = Order.objects.filter(
        status='Pending'
    ).count()

    processing_orders = Order.objects.filter(
        status='Processing'
    ).count()

    completed_orders = Order.objects.filter(
        status='Completed'
    ).count()

    cancelled_orders = Order.objects.filter(
        status='Cancelled'
    ).count()


    # Total revenue from completed orders

    total_revenue = Order.objects.filter(
        status='Completed'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0


    # Low stock products

    low_stock_products = Product.objects.filter(
        stock__lte=models.F('minimum_stock')
    )


    # Monthly revenue

    monthly_revenue = (
        Order.objects
        .filter(status='Completed')
        .annotate(
            month=TruncMonth('order_date')
        )
        .values('month')
        .annotate(
            revenue=Sum('total_amount')
        )
        .order_by('month')
    )


    # AI Predictions

    ai_predictions = []

    for product in Product.objects.all():

        predicted_demand = predict_demand(product.id)

        if predicted_demand is not None:

            recommended_purchase = max(
                0,
                predicted_demand - product.stock
            )

            if product.stock >= predicted_demand:

                risk = 'LOW'

            elif product.stock >= predicted_demand * 0.5:

                risk = 'MEDIUM'

            else:

                risk = 'HIGH'


            ai_predictions.append({
                'product': product,
                'predicted_demand': predicted_demand,
                'recommended_purchase': recommended_purchase,
                'risk': risk,
            })


    # Context

    context = {

        'total_products': total_products,

        'total_orders': total_orders,

        'pending_orders': pending_orders,

        'processing_orders': processing_orders,

        'completed_orders': completed_orders,

        'cancelled_orders': cancelled_orders,

        'total_revenue': total_revenue,

        'low_stock_products': low_stock_products,

        'monthly_revenue': monthly_revenue,

        'ai_predictions': ai_predictions,

    }


    return render(
        request,
        'dashboard/dashboard.html',
        context
    )