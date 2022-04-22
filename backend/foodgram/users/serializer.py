from rest_framework import serializers, validators
from django.core.exceptions import ObjectDoesNotExist

from users.models import Subscribe, User

SELF_FOLLOW_FORBIDDEN = 'Подписка на самогосебя запрещена.'


class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.SerializerMethodField(
    #
    # )
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        ]

    def get_is_subscribed(self, item):
        import pdb
        pdb.set_trace()
        # return True if Subscribe.objects.filter(user=item, subscribing=)

class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    subscribing = serializers.PrimaryKeyRelatedField(
        default='',
        queryset=User.objects.all()
    )

    # def create(self, validated_data):
    #     import pdb
    #     pdb.set_trace()
    #     try:
    #         following = User.objects.get(id=self.context['following'])
    #     except ObjectDoesNotExist as error:
    #         raise serializers.ValidationError(error)
    #     user = self.context['request'].user
    #     if following == user:
    #         raise serializers.ValidationError(SELF_FOLLOW_FORBIDDEN)
    #     return Follow.objects.create(user=user, following=following)

    class Meta:
        model = Subscribe
        fields = '__all__'
        # validators = [
        #     validators.UniqueTogetherValidator(
        #         queryset=Subscribe.objects.all(),
        #         fields=['user', 'subscribing']
        #     )
        # ]