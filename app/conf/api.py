from django.urls import path

from search.api.views import SearchApi

urlpatterns = [
    path("search", SearchApi.as_view(), name="search_api")
]
