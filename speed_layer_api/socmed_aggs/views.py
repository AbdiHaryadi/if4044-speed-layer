from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
from .models import SocmedAggs
from .serializers import SocmedAggsSerializer

class ListSocmedAggs(APIView):
    def get(self, request, format=None):
        queryset = SocmedAggs.objects.all()
        if "start" in request.GET.keys():
            try:
                queryset = queryset.filter(timestamp__gte=datetime.strptime(request.GET["start"], '%Y-%m-%d %H:%M'))
            except:
                return Response(
                    {'message': 'Please use date format yyyy-mm-dd hh:mm for start parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        if "end" in request.GET.keys():
            try:
                queryset = queryset.filter(timestamp__lte=datetime.strptime(request.GET["end"], '%Y-%m-%d %H:%M'))
            except:
                return Response(
                    {'message': 'Please use date format yyyy-mm-dd hh:mm for end parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        if "social_media" in request.GET.keys():
            queryset = queryset.filter(social_media=request.GET["social_media"])
        serializer = SocmedAggsSerializer(queryset, many=True)
        return Response(serializer.data)

class SumSocmedAggs(APIView):
    def get(self, request, format=None):
        queryset = SocmedAggs.objects.all()
        if "start" in request.GET.keys():
            try:
                queryset = queryset.filter(timestamp__gte=datetime.strptime(request.GET["start"], '%Y-%m-%d %H:%M'))
            except:
                return Response(
                    {'message': 'Please use date format yyyy-mm-dd hh:mm for start parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        if "end" in request.GET.keys():
            try:
                queryset = queryset.filter(timestamp__lte=datetime.strptime(request.GET["end"], '%Y-%m-%d %H:%M'))
            except:
                return Response(
                    {'message': 'Please use date format yyyy-mm-dd hh:mm for end parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        if "social_media" in request.GET.keys():
            queryset = queryset.filter(social_media=request.GET["social_media"])
        
        result = queryset.aggregate(Sum('count'), Sum('unique_count'))

        return Response(queryset.aggregate(Sum('count'), Sum('unique_count')))
