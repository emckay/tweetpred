from rest_framework import serializers
from .models import Account, DataFile, Estimate, Prediction


class AccountSerializer(serializers.ModelSerializer):
  class Meta:
    model = Account
    fields = ('pk', 'screen_name', 'dow', 'bins', 'market_url')

class DataFileSerializer(serializers.ModelSerializer):
  class Meta:
    model = DataFile
    fields = ('pk', 's3_key', 's3_bucket', 'account_id', 'data_fetched_at')

class EstimateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Estimate
    fields = ('pk', 'data_file_id', 'initial_params', 'hyper_params', 'start_time', 'end_time', 'params')

class PredictionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Prediction
    fields = ('pk', 'estimate_id', 'data_file_id', 'start_time', 'end_time', 'value')
