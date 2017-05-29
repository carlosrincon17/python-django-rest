
from rest_framework import serializers
from apks.models import Apk

class ApkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apk
        fields = ('id', 'name', 'description', 'created_at', 'updated_at',
                  'cover', 'apk')
        read_only_fields = ('id', 'created_at', 'updated_at', 'cover', 'apk')
