import pandas as pd

from orders.models import OrderItem


def get_product_demand_data(product_id):

    order_items = OrderItem.objects.filter(
        product_id=product_id
    ).values(
        'order__order_date',
        'quantity'
    )

    data = list(order_items)

    if not data:
        return None

    df = pd.DataFrame(data)

    df['order__order_date'] = pd.to_datetime(
        df['order__order_date']
    )

    df['month'] = (
        df['order__order_date']
        .dt.to_period('M')
        .astype(str)
    )

    monthly_data = (
        df.groupby('month')['quantity']
        .sum()
        .reset_index()
    )

    return monthly_data
import pandas as pd

from sklearn.linear_model import LinearRegression

from orders.models import OrderItem


def get_product_demand_data(product_id):

    order_items = OrderItem.objects.filter(
        product_id=product_id
    ).values(
        'order__order_date',
        'quantity'
    )

    data = list(order_items)

    if not data:
        return None

    df = pd.DataFrame(data)

    df['order__order_date'] = pd.to_datetime(
        df['order__order_date']
    )

    df['month'] = (
        df['order__order_date']
        .dt.to_period('M')
        .astype(str)
    )

    monthly_data = (
        df.groupby('month')['quantity']
        .sum()
        .reset_index()
    )

    return monthly_data

def get_demand_history(product_id):

    df = get_product_demand_data(product_id)

    if df is None:
        return []

    history = []

    for _, row in df.iterrows():

        history.append({
            'month': row['month'],
            'quantity': int(row['quantity'])
        })

    return history
def predict_demand(product_id):

    df = get_product_demand_data(product_id)

    if df is None or len(df) < 2:
        return None

    df['month_number'] = range(1, len(df) + 1)

    X = df[['month_number']]

    y = df['quantity']

    model = LinearRegression()

    model.fit(X, y)

    next_month = [[len(df) + 1]]

    prediction = model.predict(next_month)

    predicted_demand = max(
        0,
        round(prediction[0])
    )

    return predicted_demand