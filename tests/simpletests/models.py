from django.db import models


class Food(models.Model):
    is_meat = models.BooleanField()

    def __unicode__(self):
        return u'Food #%d' % self.id
