import json

from django.shortcuts import render

from products.models import Product

from .ml_model import (
    predict_demand,
    get_demand_history
)


def prediction(request):

    products = Product.objects.all().order_by('name')

    selected_product = None
    predicted_demand = None
    recommended_purchase = None
    risk = None

    history = []

    chart_labels = []
    chart_values = []

    product_id = request.GET.get('product')

    if product_id:

        try:

            selected_product = Product.objects.get(
                id=product_id
            )

            history = get_demand_history(
                selected_product.id
            )

            predicted_demand = predict_demand(
                selected_product.id
            )

            if predicted_demand is not None:

                recommended_purchase = max(
                    0,
                    predicted_demand - selected_product.stock
                )

                if selected_product.stock >= predicted_demand:

                    risk = 'LOW'

                elif selected_product.stock >= predicted_demand * 0.5:

                    risk = 'MEDIUM'

                else:

                    risk = 'HIGH'


            # Chart data

            for item in history:

                chart_labels.append(
                    item['month']
                )

                chart_values.append(
                    item['quantity']
                )


            if predicted_demand is not None:

                chart_labels.append(
                    'Next Month'
                )

                chart_values.append(
                    predicted_demand
                )


        except Product.DoesNotExist:

            pass


    context = {

        'products': products,

        'selected_product': selected_product,

        'predicted_demand': predicted_demand,

        'recommended_purchase': recommended_purchase,

        'risk': risk,

        'history': history,

        'chart_labels': json.dumps(chart_labels),

        'chart_values': json.dumps(chart_values),

    }


    return render(
        request,
        'ai_prediction/prediction.html',
        context
    )