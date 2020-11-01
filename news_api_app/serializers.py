from rest_framework import serializers

from .models import News


class NewsSerializer(serializers.ModelSerializer):
    """ Serializer for news Model"""

    class Meta:
        model = News
        fields = (
            'id',
            'title',
            'details',
            'date',
            'news_from',
            'news_url',
        )
