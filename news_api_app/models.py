from django.db import models


class News(models.Model):
    """Model for the News entity"""
    title = models.CharField(max_length=50, blank=False)
    details = models.TextField(blank=False)
    date = models.DateField(blank=False)
    news_from = models.CharField(max_length=50, blank=False)
    news_url = models.CharField(max_length=250, blank=False)

    def __str__(self):
        return self.id
