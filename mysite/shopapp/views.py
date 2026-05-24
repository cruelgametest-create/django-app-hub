"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""


import logging
from timeit import default_timer

from django.contrib.auth.models import Group
from django.contrib.syndication.views import Feed
from django.contrib.messages.api import success
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage, User
from .serializers import OrderSerializer

log = logging.getLogger(__name__)


class ShopIndexView(View):

    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('lApTop', 1999),
            ('deskTOp', 2999),
            ('smartPhone', 999),
        ]

        context = {
            "time_running": default_timer(),
            "products": products,
            "items" : 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")

        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class LatestProductsFeed(Feed):
    title = "Products show (latest)"
    description = "New products in the store"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.filter(archived=False)

    def item_title(self, item: Product):
        return f"{item.name} > {item.price}$, discount: {item.discount}%"

    def item_description(self, item: Product):
        return item.description[:200]


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        return self.request.user.is_superuser or self.request.user.has_perm("shopapp.add_product")

    model = Product
    fields = "name", "price", "description", "discount", "created_by", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm("shopapp.change_product") and get_object_or_404(Product, pk=self.kwargs["pk"]).created_by == self.request.user

    model = Product
    # fields = "name", "price", "description", "discount", "created_by", "preview"
    form_class = ProductForm
    template_name_suffix = "_update_form"
    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products", "promocode", "delivery_address"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "user", "products", "promocode", "delivery_address"
    template_name_suffix = "_update_form"
    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class UserOrdersListView(ListView):
    template_name = 'shopapp/user_orders_list.html'

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        self.owner = get_object_or_404(User, id=user_id)
        queryset = (
            Order.objects.select_related("user").prefetch_related("products").filter(user=self.owner)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_user"] = self.owner
        return context


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            elem = products_data[0]
            name = elem["name"]
            print("name:", name)
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class UserOrdersExportView(View):
    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        cache_key = f"user_orders_export_{user_id}"
        user = get_object_or_404(User, id=user_id)
        user_orders_data = cache.get(cache_key)
        if user_orders_data is None:
            orders = Order.objects.select_related("user").prefetch_related("products").filter(user=user)
            user_orders_data = OrderSerializer(orders, many=True).data
            # user_orders_data = [
            #     {
            #         "pk": order.pk,
            #         "user_id": order.user_id,
            #         "delivery_address": order.delivery_address,
            #         "promocode": order.promocode,
            #     }
            #     for order in orders
            # ]
            cache.set(cache_key, user_orders_data, 180)
        return JsonResponse({"orders": user_orders_data})
