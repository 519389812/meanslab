from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=300, blank=True, verbose_name='全名')

    def save(self, *args, **kwargs):
        self.full_name = '%s%s' % (self.last_name, self.first_name)
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
