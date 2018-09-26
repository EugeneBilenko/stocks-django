from django.db import models

# Create your models here.

# Algo name, the daily PnL and the positions


class AlgoProp(models.Model):
    name = models.CharField(max_length=255)
    daily_pnl = models.TextField()
    position = models.TextField()
