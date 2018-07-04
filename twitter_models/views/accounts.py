import datetime
import pytz
import numpy as np
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from ..models import Account, DataFile, Prediction
from ..serializers import AccountSerializer
from ..helpers import last_dow_noon


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Account.objects.all()
  serializer_class = AccountSerializer

  @action(methods=['GET'], detail=True)
  @method_decorator(cache_page(600))
  def latest_histogram(self, _, pk):
    account = Account.objects.get(pk=pk)
    data_file = DataFile.objects.filter(account_id=account.pk).annotate(
        pred_count=Count('prediction')).filter(pred_count__gte=100).latest('created_at')
    estimate = data_file.estimate_set.latest('created_at')
    predictions = Prediction.objects.filter(
        data_file_id=data_file.pk, estimate_id=estimate.id).all()
    if len(predictions) == 0:
      raise 'no predictions yet'
    period_start = last_dow_noon(
        account.dow, datetime.datetime.now(pytz.timezone('America/New_York')))
    period_end = period_start + datetime.timedelta(days=7)
    if predictions[0].end_time != period_end:
      raise 'prediction end time not same as period end'
    timestamps = data_file.get_df()['timestamp_s_utc']
    so_far = list(filter(lambda x: x > period_start.timestamp()
                         and x < period_end.timestamp(), timestamps))
    predicted_counts = np.array(list(map(lambda x: x.value, predictions)))
    predicted_counts += len(so_far)
    bins = []
    for i in range(len(account.bins) + 1):
      if i == 0:
        bin_start = 0
      else:
        bin_start = account.bins[i - 1]
      if i < len(account.bins):
        bin_end = account.bins[i]
      else:
        bin_end = 9999
      bins.append({
          'start': bin_start,
          'end': bin_end,
          'count': len(predicted_counts[(predicted_counts >= bin_start) & (predicted_counts < bin_end)]),
      })
    return Response({
        'params': estimate.params,
        'model_class': estimate.model_class,
        'n': len(predictions),
        'so_far': len(so_far),
        'bins': bins,
        'as_of': data_file.data_fetched_at,
        'account': AccountSerializer(account).data,
        'period_start': period_start,
        'period_end': period_end,
    })
