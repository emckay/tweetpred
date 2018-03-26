import io
import re
import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
import boto3
import pandas as pd


class Account(models.Model):
  screen_name = models.CharField(max_length=100)
  dow = models.IntegerField()
  created_at = models.DateTimeField(auto_now_add=True, null=False)
  updated_at = models.DateTimeField(auto_now=True, null=False)


class DataFile(models.Model):
  account = models.ForeignKey(Account, on_delete=models.PROTECT)
  s3_key = models.CharField(max_length=100)
  s3_bucket = models.CharField(max_length=100)
  data_fetched_at = models.DateTimeField()
  archived = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, null=False)
  updated_at = models.DateTimeField(auto_now=True, null=False)

  @staticmethod
  def filter_keys(twitter_status):
    keys = ['created_at', 'favorite_count', 'id_str', 'is_retweet',
            'retweet_count', 'source', 'text', 'timestamp_s_utc']
    d = twitter_status.AsDict()
    # for consistency with twitter archive data
    d['source'] = re.split(r'>|<', d['source'])[2]
    if 'retweeted_status' in d:
      d['is_retweet'] = True
      d['favorite_count'] = 0
    else:
      d['is_retweet'] = False
    d['timestamp_s_utc'] = datetime.datetime.strptime(
        twitter_status.created_at, '%a %b %d %H:%M:%S %z %Y').timestamp()
    return dict((k, d[k]) for k in keys if k in d)

  def get_df(self):
    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    obj = client.get_object(Bucket=self.s3_bucket, Key=self.s3_key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

  def write_df(self, statuses):
    df = pd.DataFrame(list(map(DataFile.filter_keys, statuses)))
    df.drop_duplicates(inplace=True)
    df.sort_values('timestamp_s_utc', inplace=True)
    csv_buffer = io.BytesIO()
    byt = df.to_csv(None).encode()
    csv_buffer.write(byt)
    csv_buffer.seek(0)
    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    s3_key = '%s_%0.0f.csv' % (self.account.screen_name, self.data_fetched_at.timestamp())
    s3_bucket = settings.S3_DATA_FILE_BUCKET
    client.upload_fileobj(csv_buffer, s3_bucket, s3_key)
    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    self.s3_key = s3_key
    self.s3_bucket = s3_bucket


class Estimate(models.Model):
  data_file = models.ForeignKey(DataFile, on_delete=models.PROTECT)
  model_class = models.CharField(max_length=100)
  initial_params = JSONField()
  hyper_params = JSONField()
  params = JSONField()
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
  created_at = models.DateTimeField(auto_now_add=True, null=False)
  updated_at = models.DateTimeField(auto_now=True, null=False)


class Prediction(models.Model):
  estimate = models.ForeignKey(Estimate, on_delete=models.PROTECT)
  data_file = models.ForeignKey(DataFile, on_delete=models.PROTECT)
  start_time = models.DateTimeField()
  end_time = models.DateTimeField()
  value = models.FloatField()
  created_at = models.DateTimeField(auto_now_add=True, null=False)
  updated_at = models.DateTimeField(auto_now=True, null=False)
