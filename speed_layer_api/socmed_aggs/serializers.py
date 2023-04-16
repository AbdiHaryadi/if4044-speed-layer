from rest_framework import serializers
from .models import SocmedAggs

class SocmedAggsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocmedAggs
        fields = ['social_media', 'timestamp', 'count', 'unique_count', 'created_at', 'updated_at']