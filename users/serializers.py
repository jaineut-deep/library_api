from rest_framework import serializers

from .models import CustomUser, LendingBook


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]
        read_only_fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]

    def validate_email(self, value):
        value = value.lower().strip()

        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LendingBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = LendingBook
        fields = ["publication", "member"]
        read_only_fields = ["created_at", "updated_at", "count_renewal"]

    def validate(self, data):
        count_renewal = data.get("count_renewal")

        if count_renewal > 2:
            raise serializers.ValidationError({"count_renewal": "У выдачи не может быть больше двух продлений"})

        return data
