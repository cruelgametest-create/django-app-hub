"""
В этом модуле лежат представления для API. бу
"""


from csv import DictWriter

from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .common import save_csv_products
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("hello products list")  #принт для отладки
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


@extend_schema(description="Order views CRUD")
class OrderViewSet(ModelViewSet):
    """
    Набор представлений для действий над Order
    Полный CRUD для сущностей заказа
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["delivery_address", "promocode"]
    filterset_fields = [
        "delivery_address",
        "promocode",
    ]
    ordering_fields = [
        "delivery_address",
        "promocode",
    ]

    @extend_schema(
        summary="Get one order by ID",
        description="Retrieves **order**, returns 404 if not found",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Empty response, order by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)
