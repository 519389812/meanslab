from django.db import models
from user.models import CustomUser
from nanoid import generate


class ExchangeCard(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, verbose_name='卡名称')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ExchangeCard_user", verbose_name="用户")
    times = models.IntegerField(verbose_name="可使用次数")
    code = models.CharField(max_length=150, blank=True, verbose_name="兑换码")

    def save(self, *args, **kwargs):
        self.code = generate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', 14)
        super(ExchangeCard, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Gi'
        verbose_name_plural = 'Gi'

    def __str__(self):
        return self.name


class CardHolder(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=300, verbose_name="内容")
    signature = models.CharField(max_length=150, verbose_name="署名")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="CardHolder_user", verbose_name="用户")
    exchange_card = models.ManyToManyField(ExchangeCard, on_delete=models.CASCADE, related_name="CardHolder_exchange_card", verbose_name="卡片")

    class Meta:
        verbose_name = 'Gi'
        verbose_name_plural = 'Gi'

    def __str__(self):
        return self.signature
