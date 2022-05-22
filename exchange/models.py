from django.db import models
from user.models import CustomUser


class CardHolder(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=150, blank=True, verbose_name="卡包码")
    to = models.CharField(max_length=150, blank=True, verbose_name="称呼")
    content = models.TextField(max_length=300, verbose_name="内容")
    signature = models.CharField(max_length=150, verbose_name="署名")
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name="CardHolder_user", verbose_name="用户")

    class Meta:
        verbose_name = '卡包'
        verbose_name_plural = '卡包'

    def __str__(self):
        return self.signature


class ExchangeCard(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, verbose_name='卡名称')
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name="ExchangeCard_user", verbose_name="用户")
    used_times = models.IntegerField(default=0, verbose_name="已使用次数")
    times = models.IntegerField(verbose_name="可使用次数")
    term = models.TextField(max_length=300, blank=True, verbose_name="使用条款")
    code = models.CharField(max_length=150, blank=True, verbose_name="兑换码")
    card_holder = models.ForeignKey(CardHolder, on_delete=models.CASCADE, related_name="ExchangeCard_card_holder", verbose_name="卡包")

    class Meta:
        verbose_name = '礼物卡'
        verbose_name_plural = '礼物卡'

    def __str__(self):
        return self.name


