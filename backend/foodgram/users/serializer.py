from rest_framework import serializers, validators
from django.core.exceptions import ObjectDoesNotExist

from users.models import Follow, User

SELF_FOLLOW_FORBIDDEN = 'Подписка на самогосебя запрещена.'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        ]


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        default='',
        queryset=User.objects.all()
    )

    def create(self, validated_data):
        import pdb
        pdb.set_trace()
        try:
            following = User.objects.get(id=self.context['following'])
        except ObjectDoesNotExist as error:
            raise serializers.ValidationError(error)
        user = self.context['request'].user
        if following == user:
            raise serializers.ValidationError(SELF_FOLLOW_FORBIDDEN)
        return Follow.objects.create(user=user, following=following)

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]