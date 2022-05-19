from django.db import models
from user.models import CustomUser
import random


class ExchangeCard(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, verbose_name='卡名称')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ExchangeCard_user", verbose_name="用户")
    times = models.IntegerField(verbose_name="可使用次数")
    code = models.CharField(max_length=150, blank=True, verbose_name="兑换码")

    def save(self, *args, **kwargs):
        random_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        code_len = 6
        code = ""
        for i in range(code_len):
            code += random.choice(random_string)
        self.code = code
        super(ExchangeCard, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '礼物卡'
        verbose_name_plural = '礼物卡'

    def __str__(self):
        return self.name
