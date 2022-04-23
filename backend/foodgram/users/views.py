from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User, Subscribe
from users.serializers import SubscribeSerializer, UserSerializer


SELF_SUBSCRIBE_FORBIDDEN = 'Подписка на самого себя запрещена'
ALREADY_SUBSCRIBED = 'Вы уже подписаны на {user} автора'
ERROR = 'error'


class SubscribeViewSet(ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, subscribing):
        get_object_or_404(
            Subscribe,
            user=request.user.id, subscribing__id=subscribing
        ).delete()
        return Response(status=204)

    def create(self, request, subscribing):
        if subscribing == request.user.id:
            return Response({ERROR: SELF_SUBSCRIBE_FORBIDDEN}, status=400)
        subscribing_user = get_object_or_404(User, id=subscribing)
        item, created = Subscribe.objects.get_or_create(
            subscribing=subscribing_user,
            user=request.user
        )
        if not created:
            return Response(
                {ERROR: ALREADY_SUBSCRIBED.format(
                    user=subscribing_user.username
                )},
                status=400
            )
        return Response(SubscribeSerializer(
            item,
            many=False,
            context={'request': request}).data, status=201)

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)
