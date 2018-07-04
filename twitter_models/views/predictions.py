import datetime
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from ..models import Prediction, Estimate, DataFile
from ..serializers import PredictionSerializer
from ..predictive_models.hawkes import predict
from ..helpers import last_dow_noon

class PredictionViewSet(viewsets.ModelViewSet):
  queryset = Prediction.objects.all()
  serializer_class = PredictionSerializer

  def create(self, request):
    estimate_pk = request.data['estimate_id']
    est = Estimate.objects.get(pk=estimate_pk)
    data_file_pk = request.data['data_file_id']
    n = request.data['n']
    data_file = DataFile.objects.get(pk=data_file_pk)
    account = data_file.account
    period_start = last_dow_noon(account.dow, datetime.datetime.now(pytz.timezone('America/New_York')))
    period_end = period_start + datetime.timedelta(days=7)
    df = data_file.get_df()
    pred_start_time = data_file.data_fetched_at.timestamp()
    pred_end_time = period_end.timestamp()
    for _ in range(n):
      value = predict(df, est.params, est.hyper_params,
                      est.start_time.timestamp(), pred_start_time, pred_end_time)
      pred = Prediction.objects.create(
          estimate=est,
          data_file=data_file,
          start_time=datetime.datetime.utcfromtimestamp(
              pred_start_time).replace(tzinfo=pytz.utc),
          end_time=datetime.datetime.utcfromtimestamp(
              pred_end_time).replace(tzinfo=pytz.utc),
          value=value
      )
    return Response(self.serializer_class(pred, context={'request': request}).data)
