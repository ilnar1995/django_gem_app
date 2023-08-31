from django.db import models


class Gem(models.Model):
    """ Gem """
    name = models.CharField('Название', max_length=64, unique=True)

    class Meta:
        db_table = "stone"
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'

    def __str__(self):
        return self.name


class Customer(models.Model):
    """ Customer """
    username = models.CharField('Имя пользователя', max_length=64, unique=True)

    class Meta:
        db_table = "customer"
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Deal(models.Model):
    """ Deal """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 related_name='deals', verbose_name='Пользователь')
    item = models.ForeignKey(Gem, on_delete=models.CASCADE, related_name='deals', verbose_name='Камень')
    quantity = models.PositiveIntegerField('Количество')
    total = models.PositiveIntegerField('Сумма сделки')
    date = models.DateTimeField('Дата и время создания')

    class Meta:
        db_table = "deal"
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    def __str__(self):
        return self.customer.username
