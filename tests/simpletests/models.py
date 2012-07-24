from django.db import models


class Food(models.Model):
    is_meat = models.BooleanField()
