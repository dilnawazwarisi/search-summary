from django.urls import path, include
from .views import *


urlpatterns = [
    path('get-summary', SearchView.as_view(), name='search-view')
]