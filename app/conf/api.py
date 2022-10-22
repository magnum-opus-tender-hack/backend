from django.urls import path

from search.api.views import (
    SearchApi,
    HintApi,
    AutoCompleteApi,
    IncreaseProductScoreApi,
)

urlpatterns = [
    path("search", SearchApi.as_view(), name="search_api"),
    path("hint", HintApi.as_view(), name="hint_api"),
    path("autocomplete_schema", AutoCompleteApi.as_view(), name="autocomplete_api"),
    path("score/<int:pk>", IncreaseProductScoreApi.as_view(), name="score_api"),
]
