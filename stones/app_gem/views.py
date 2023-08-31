import csv
import codecs

from django.db.models import Sum
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import status, views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from datetime import datetime
from django.db import transaction

from .models import Customer, Deal, Gem
from .serializers import CustomerSerializer, CSVFileSerializer  # , DealSerializer

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class UploadDealsListCustomerAPIView(views.APIView):
    parser_classes = [MultiPartParser]
    queryset = Customer.objects.all().prefetch_related('deals', 'deals__item')
    serializer_class = CSVFileSerializer

    def get_queryset(self):
        return self.queryset.annotate(
            spent_money=Sum('deals__total')
        ).order_by('-spent_money')[:5]

    @extend_schema(request=CSVFileSerializer)
    def post(self, request, *args, **kwargs):
        serializer = CSVFileSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data['deals']
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        try:
            reader = csv.DictReader(codecs.iterdecode(csv_file, "utf-8"), delimiter=",")
            deals = []

            with transaction.atomic():
                # удаление старых данных
                Customer.objects.all().delete()
                Gem.objects.all().delete()
                Deal.objects.all().delete()

                for row in reader:
                    customer = Customer.objects.get_or_create(username=row['customer'])[0]
                    item = Gem.objects.get_or_create(name=row['item'])[0]
                    quantity = int(row['quantity'])
                    total = float(row['total'])
                    date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S.%f')

                    deals.append(Deal(customer=customer, item=item, quantity=quantity, total=total, date=date))

                Deal.objects.bulk_create(deals)

                # удаление из кэша данных
                cache.delete('customers_cache')
            return Response({'Status': 'OK'}, status.HTTP_200_OK)

        except:
            return Response({'Status': 'Error: file contain wrong data, make sure file is correct'},
                            status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={
        200: CustomerSerializer,
    }, )
    def get(self, request, *args, **kwargs):
        customers_cache = cache.get('customers_cache')
        if not customers_cache:
            serializer = CustomerSerializer(self.get_queryset(), many=True)
            data = {
                'response': serializer.data
            }
            cache.set('customers_cache', data, CACHE_TTL)
            return Response(data, status.HTTP_200_OK)
        return Response(customers_cache, status.HTTP_200_OK)
