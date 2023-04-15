from django.urls import include, path
from .views import ListSocmedAggs, SumSocmedAggs

urlpatterns = [
    path('list/', ListSocmedAggs.as_view()),
    path('sum/', SumSocmedAggs.as_view()),
]