from django.urls import path

from .views import UploadDealsListCustomerAPIView


urlpatterns = [
    path('deals/', UploadDealsListCustomerAPIView.as_view()),
]
