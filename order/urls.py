from django.urls import path
from .views import OrderView, OrderDetailsView

urlpatterns = [
    path('order/', OrderView.as_view()),
    path('order/<int:pk>/', OrderDetailsView.as_view()),
]
