from rest_framework import serializers

from clicks.models import Click


class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = ['campaign', 'timestamp']
