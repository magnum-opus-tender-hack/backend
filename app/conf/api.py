from django.urls import path

from search.api.views import SearchApi, HintApi, AutoCompleteApi

urlpatterns = [
    path("search", SearchApi.as_view(), name="search_api"),
    path("hint", HintApi.as_view(), name="hint api"),
    path('autocomplete_schema', AutoCompleteApi.as_view(), name='autocomplete api')
]
