import datetime
import twitter
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from django.conf import settings
from ..models import DataFile, Account
from ..serializers import DataFileSerializer

class DataFileViewSet(viewsets.ModelViewSet):
  queryset = DataFile.objects.all()
  serializer_class = DataFileSerializer

  def create(self, request):
    account = Account.objects.get(pk=request.data['account_id'])
    api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                      consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                      access_token_key=settings.TWITTER_ACCESS_TOKEN_KEY,
                      access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                      application_only_auth=True)
    download_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    res = api.GetUserTimeline(screen_name=account.screen_name, count=200)
    new_tweets = res
    while len(res) > 1:
      max_id = res[-1].id_str
      print('downloading after', max_id)
      res = api.GetUserTimeline(
          screen_name=account.screen_name, max_id=max_id, count=200)
      new_tweets = new_tweets + res

    data_file = DataFile(account=account, data_fetched_at=download_time)
    data_file.write_df(new_tweets)
    data_file.save()
    return Response(self.serializer_class(data_file).data)
