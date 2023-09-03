from django.urls import path
from . import views

urlpatterns = [
path('', views.store, name='store'),
path('cart/', views.cart, name='cart'),
path('checkout/', views.checkout, name='checkout'),
path('update_item/', views.updateItem, name='update'),
path('process_order/', views.processOrder, name="process_order"),
path('orders/', views.OrderListView.as_view(), name='orders_list'),

path('customers/', views.CustomerListView.as_view(), name='customers_list'),
path('products/', views.ProductListView.as_view(), name='products_list'),
# path('products/<int:order_id>/mark_as_sold/', views.ProductView.as_view(), name='product_mark_sold'),
# path('orders/<int:order_id>/mark_as_shipped/', views.OrderMarkAsShippedView.as_view(), name='order_mark_shipped'),




]
