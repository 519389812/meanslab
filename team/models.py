from django.db import models


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name="名称")

    class Meta:
        verbose_name = "分组"
        verbose_name_plural = "分组"
        ordering = ["name"]

    def __str__(self):
        return self.name
