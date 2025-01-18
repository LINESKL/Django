from rest_framework import serializers
from crm.models import TelegramUser

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            'user_id', 'username', 'last_activity', 'used_functions', 'quiz_points', 'created_at',
            'full_name', 'gender', 'age', 'region', 'marital_status', 'children', 'benefits',
            'is_registered', 'is_web_user'
        ]