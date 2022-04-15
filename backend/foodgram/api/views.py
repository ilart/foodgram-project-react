from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from api.serializer import TagSerializer
from recipes.models import Tag


