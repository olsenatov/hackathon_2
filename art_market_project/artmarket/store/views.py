from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

# Create your views here.

def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items    
    else:
        items = []
        order = {'get_cart_items': 0, 
                 'get_cart_total': 0,
                 'shipping' : False}
        cartItems = order['get_cart_items']
     
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request): 
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items    
        
    else:
        items = []
        order = {'get_cart_items': 0, 
                 'get_cart_total': 0,
                 'shipping' : False
                 }
        cartItems = order['get_cart_items']
        
    products = Product.objects.all() 
    context = {'items': items,
               'order': order, 'cartItems': cartItems }
    return render(request, 'store/cart.html', context)

def checkout(request): 
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items 
    else:
        items = []
        order = {'get_cart_items': 0, 
                 'get_cart_total': 0,
                 'shipping' : False
                 }
        cartItems = order['get_cart_items']
        
    products = Product.objects.all()    
    context = {'items': items,
               'order': order, 'cartItems': cartItems }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

@csrf_exempt       
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = float(data['form']['total'])
		order.transaction_id = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['country'],
			zipcode=data['shipping']['zipcode'],
            phone=data['shipping']['phone'],
			)
	else:
		print('User is not logged in')

	return JsonResponse('Payment submitted..', safe=False)


class OrderListView(APIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.all()

    def get(self, request):
        orders = self.get_queryset()
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)
    
    def put(self, request, order_id):
        order = self.get_object(order_id)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, order_id):
        order = self.get_object(id=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CustomerListView(APIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.all()

    def get(self, request):
        customers = self.get_queryset()
        serializer = self.serializer_class(customers, many=True)
        return Response(serializer.data)
    
    def put(self, request, customer_id):
        customer = self.get_object(customer_id)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, customer_id):
        customer = self.get_object(id=customer_id)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class ProductListView(APIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()

    def get(self, request):
        products = self.get_queryset()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)
    
    def put(self, request, product_id):
        product = self.get_object(product_id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, product_id):
        product = self.get_object(id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 

# class OrderMarkAsShippedView(APIView):    
#     def mark_as_shipped(self, request, order_id):
#         order = get_object_or_404(Order, id=order_id)
#         order.shipped = True
#         order.save()
#         return Response({'message': 'Order marked as shipped'})

# 
# class ProductMarkAsSoldView(APIView):
#     def mark_as_sold(self, request, product_id):
#         product = get_object_or_404(Order, id=product_id)
#         product.sold = True
#         product.save()
#         return Response({'message': 'Product is sold out'})
    