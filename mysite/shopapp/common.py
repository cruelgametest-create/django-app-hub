from csv import DictReader
from io import TextIOWrapper

from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    orders = []
    for row in reader:
        order = Order(
            user_id = row['user'],
            delivery_address = row['delivery_address'],
            promocode = row['promocode'],
        )
        order.save()
        p = Product.objects.filter(id__in=list(map(int, row['products'].split(', '))))
        order.products.set(p)
        orders.append(order)

    return orders
