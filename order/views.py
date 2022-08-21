from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import Http404
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from .models import Order, OrderItem, Store, Product


# Create your views here.
class OrderView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):

    def get_queryset(self):
        return OrderItem.objects.all()

    def get(self, request, *args, **kwargs):
        if request.GET.get('user'):
            response = Order.objects.filter(user__id=int(request.GET.get('user'))).values()
            return Response(response, status=status.HTTP_200_OK)

        if request.GET.get('store'):
            response = Order.objects.filter(store__name__icontains=request.GET.get('store')).values()
            return Response(response, status=status.HTTP_200_OK)

        orders = Order.objects.all().values()
        response = {"message": "Data Retrieved", "data": orders}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        store = Store.objects.get(id=request.data['store'])
        order = Order.objects.create(user=User.objects.get(id=int(request.data['user'])), store=store)
        for i in request.data['items']:
            OrderItem.objects.create(order=order, product=Product.objects.get(id=i.get('product')),
                                     quantity=i.get('quantity'),
                                     amount=Product.objects.get(id=i.get('product')).price * int(i.get('quantity')))
        sum = OrderItem.objects.filter(order=order).aggregate(Sum('amount'))['amount__sum']
        order = Order.objects.get(id=order.id)
        order.total = sum
        order.save()
        response = {"message": "Order Placed Successfully", "order": order.id}
        return Response(response, status=status.HTTP_201_CREATED)


class OrderDetailsView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    queryset = OrderItem.objects.all()

    def get_object(self, pk):
        try:
            return Order.objects.filter(pk=pk)
        except Order.DoesNotExist as e:
            raise Http404 from e

    def get(self, request, pk, *args, **kwargs):
        snippet = self.get_object(pk)
        data = {
            "order": snippet.values(),
            "items": OrderItem.objects.filter(order__id=pk).values('product_id__name', 'quantity', 'amount')
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        store = Store.objects.get(id=request.data['store'])
        order = Order.objects.get(id=pk)
        order_item = OrderItem.objects.filter(order=order)
        order.store = store
        order_item.delete()
        for i in request.data['items']:
            OrderItem.objects.create(order=order, product=Product.objects.get(id=i.get('product')),
                                     quantity=i.get('quantity'),
                                     amount=Product.objects.get(id=i.get('product')).price * int(i.get('quantity')))

        sum = OrderItem.objects.filter(order=order).aggregate(Sum('amount'))['amount__sum']
        order.total = sum
        order.save()
        response = {"message": "Order Updated Successfully"}
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        order = self.get_object(pk)
        order.delete()
        response = {"message": "data deleted"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)
