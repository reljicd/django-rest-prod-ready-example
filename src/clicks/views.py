from knox.auth import TokenAuthentication
from rest_framework import permissions, viewsets
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.response import Response

from clicks.models import Click
from clicks.serializers import ClickSerializer


class ClickViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows clicks to be viewed or edited.
    """
    queryset = Click.objects.all().order_by('timestamp')
    serializer_class = ClickSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view()
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([TokenAuthentication])
def campaign_clicks(request, campaign: int):
    """
    Examples:
        GET /clicks/campaign/4510461/
        GET /clicks/campaign/4510461/?after_date=2021-11-07+03:10:00
            &before_date=2021-11-07+03:20:00
    """
    after_date = request.query_params.get('after_date')
    before_date = request.query_params.get('before_date')

    clicks = Click.count_campaign_clicks(campaign,
                                         after_date=after_date,
                                         before_date=before_date)

    response = {"campaign": campaign,
                "clicks": clicks}
    if after_date:
        response['after_date'] = after_date
    if before_date:
        response['before_date'] = before_date

    return Response(response)
