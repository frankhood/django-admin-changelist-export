from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers


class CustomExtraFieldSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("name",)

    def get_name(self, obj):
        return obj in self.context.get("user").groups.all()


class UserExportSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("last_name", "username", "first_name", "groups")

    def get_groups(self, obj):
        return CustomExtraFieldSerializer(
            Group.objects.all(), many=True, context={"user": obj}
        ).data

    @staticmethod
    def get_headers_labels():
        base_fields = {
            "last_name": "Cognome Utente",
            "username": "Username Utente",
            "first_name": "Nome Utente",
            **{
                f"groups.{index}.name": group.name
                for index, group in enumerate(Group.objects.all())
            },
        }
        return base_fields

    @staticmethod
    def get_custom_labels():
        labels = [
            "Cognome Utente",
            "Username Utente",
            "Nome Utente",
        ]

        labels.extend([group.name for group in Group.objects.all()])
        return labels
