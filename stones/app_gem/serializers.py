import os
from typing import List

from django.db.models import Sum, Q, Count
from rest_framework import serializers

from .models import Customer, Deal, Gem


class CSVFileSerializer(serializers.Serializer):
    """ CSV File serializer """
    deals = serializers.FileField()

    def validate_deals(self, value):
        ext = os.path.splitext(value.name)[1]  # Получение расширения файла
        if ext != '.csv':
            raise serializers.ValidationError('Загруженный файл должен быть в формате CSV.')
        return value


class GemSerializer(serializers.ModelSerializer):
    """ Gem serializer """

    class Meta:
        model = Gem
        fields = ('name',)


class CustomerSerializer(serializers.ModelSerializer):
    """ Customer serializer """

    spent_money = serializers.IntegerField()
    gems = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id', 'username', 'spent_money', 'gems')

    def get_gems(self, obj) -> List:
        top_customers = Customer.objects.all().prefetch_related('deals', 'deals__item').annotate(
            total_spent=Sum('deals__total')).order_by('-total_spent')[:5]
        gem_names = Gem.objects.filter(deals__customer__in=top_customers).annotate(
            num_customers=Count('deals__customer')).filter(num_customers__gte=2).values_list('name', flat=True).filter(
            deals__customer=obj)
        gems_list = [i for i in gem_names]
        return gems_list
