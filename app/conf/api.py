from django.urls import path

from search.api.views import SearchApi, HintApi

urlpatterns = [
    path("search", SearchApi.as_view(), name="search_api"),
    path("hint", HintApi.as_view(), name="hint api")
]
