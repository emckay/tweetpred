import datetime
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from ..predictive_models.hawkes import estimate, default_hyper_params, default_initial_params
from ..models import Estimate, DataFile
from ..serializers import EstimateSerializer


class EstimateViewSet(viewsets.ModelViewSet):
  queryset = Estimate.objects.all()
  serializer_class = EstimateSerializer

  def create(self, request):
    data_file_pk = request.data['data_file_id']
    data_file = DataFile.objects.get(pk=data_file_pk)
    model_class = 'hawkes'
    df = data_file.get_df()
    end_time = datetime.datetime.utcnow().timestamp()
    start_time = end_time - 60*60*24*7*4
    params = estimate(df, start_time, end_time)
    est = Estimate.objects.create(
        data_file=data_file,
        model_class=model_class,
        params=list(params),
        start_time=datetime.datetime.utcfromtimestamp(
            start_time).replace(tzinfo=pytz.utc),
        end_time=datetime.datetime.utcfromtimestamp(
            end_time).replace(tzinfo=pytz.utc),
        initial_params=default_initial_params,  # TODO: export this from hawkes model
        hyper_params=default_hyper_params  # TODO: export this from hawkes model
    )
    return Response(self.serializer_class(est, context={'request': request}).data)
