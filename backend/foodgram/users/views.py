from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.serializer import FollowSerializer, UserSerializer
from users.models import User, Follow

#
# class UsersViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     def get_permissions(self):
#         if self.action == 'retrieve':
#             return (IsAuthenticated(),)
#         return (AllowAny(),)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_me(request):
#     """Вью получения данных о себе"""
#
#     serializer = UserSerializer(
#         instance=request.user,
#     )
#     return Response(
#         serializer.data,
#         status=status.HTTP_200_OK
#     )

class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ['following__username', ]
    permission_classes = (IsAuthenticated, )



    def destroy(self, request, *args, **kwargs):

        get_object_or_404(
            Follow,
            user=request.user.id, following__username=kwargs.get('username')
        ).delete()

    def get_queryset(self):

        return self.request.user.follower.all()

    def get_serializer_context(self):
        return {"following": self.kwargs['following']}
