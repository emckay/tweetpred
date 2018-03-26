from ..models import Account
from ..serializers import AccountSerializer
from rest_framework import viewsets

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Account.objects.all()
  serializer_class = AccountSerializer
