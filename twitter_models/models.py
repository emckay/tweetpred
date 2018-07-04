import io
import re
import datetime
import csv
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
import boto3


class Account(models.Model):
  screen_name = models.CharField(max_length=100)
  dow = models.IntegerField()
  bins = JSONField()
  market_url = models.TextField()
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
    file = io.StringIO(obj['Body'].read().decode())
    reader = list(csv.DictReader(file))
    data = dict(zip(reader[0], zip(*[d.values() for d in reader])))
    data['timestamp_s_utc'] = list(
        map(int, map(float, data['timestamp_s_utc'])))
    return data

  def write_df(self, statuses):
    data = list(map(DataFile.filter_keys, statuses))
    data.sort(key=lambda x: x['timestamp_s_utc'])
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
      writer.writerow(row)
    csv_buffer.seek(0)
    encoded_csv = csv_buffer.getvalue().encode()
    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    s3_key = '%s_%0.0f.csv' % (
        self.account.screen_name, self.data_fetched_at.timestamp())
    s3_bucket = settings.S3_DATA_FILE_BUCKET
    client.put_object(Body=encoded_csv, Bucket=s3_bucket, Key=s3_key)
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
