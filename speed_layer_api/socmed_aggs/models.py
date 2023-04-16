from django.db import models

class SocmedAggs(models.Model):
    social_media = models.CharField("Social Media", max_length=32)
    timestamp = models.DateTimeField()
    count = models.IntegerField()
    unique_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.social_media + "[" + str(self.timestamp) + "]"
