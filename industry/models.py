from django.db import models


class Industry(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    name = models.CharField(max_length=20, verbose_name='名称')

    class Meta:
        verbose_name = '行业'
        verbose_name_plural = '行业'

    def __str__(self):
        return self.name
