from rest_framework import serializers

from config.settings import COUNT_RENEWAL

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

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()

        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def create(self, validated_data: dict) -> CustomUser:
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LendingBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = LendingBook
        fields = ["publication", "member"]
        read_only_fields = ["created_at", "updated_at", "count_renewal", "status"]


class LendingBookMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = LendingBook
        fields = ["count_renewal"]
        read_only_fields = ["created_at", "updated_at", "member", "publication"]

    def validate(self, data: dict) -> dict:
        count_renewal_choice = data.get("count_renewal")
        count_renewal_int = COUNT_RENEWAL.get(count_renewal_choice)

        if self.instance is not None:
            if (
                count_renewal_int - self.instance.get_count_renewal
            ) > 1 or count_renewal_int <= self.instance.get_count_renewal:
                raise serializers.ValidationError(
                    {"count_renewal": "Каждое следующее продление должно быть больше на 1"}
                )
            elif not self.instance.status:
                raise serializers.ValidationError({"status": "Текущая выдача не одобрена, попробуйте позже"})
            elif self.instance.status is None:
                raise serializers.ValidationError({"updated_at": "Запрос на выдачу уже отправлен, обратитесь позже"})
            elif self.instance.get_count_renewal == 2:
                raise serializers.ValidationError({"count_renewal": "Достигнут предел количества продлений"})

        return data


class LendingBookStaffSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(allow_null=True, required=False)

    class Meta:
        model = LendingBook
        fields = ["status"]
        read_only_fields = ["created_at", "updated_at", "count_renewal", "member", "publication"]
