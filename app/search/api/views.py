from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from search.api.serializers import HintRequestSerializer

from search.api.serializers import (
    SearchSerializer,
    ResponseSerializer,
    HintResponseSerializer,
    AutoCompleteRequestSerializer,
    AutoCompleteResponseSerializer,
)
from search.models import Product
from search.services.colors import group
from search.services.search import process_search
from search.services.autocomplete_schema import autocomplete_schema

from search.services.hints import get_hints

user_response = openapi.Response("search results", ResponseSerializer)
hint_response = openapi.Response("hints", HintResponseSerializer)
autocomplete_response = openapi.Response(
    "autocomplete schema", AutoCompleteResponseSerializer
)


class SearchApi(APIView):
    @swagger_auto_schema(request_body=SearchSerializer, responses={200: user_response})
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            group(
                process_search(
                    serializer.data["body"],
                    serializer.data["limit"],
                    serializer.data["offset"],
                ),
                serializer.data["body"],
            ),
            status=status.HTTP_200_OK,
        )


class HintApi(APIView):
    @swagger_auto_schema(
        request_body=HintRequestSerializer, responses={200: hint_response}
    )
    def post(self, request):
        serializer = HintRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "type": get_hints(serializer.data["content"]),
                "value": serializer.data["content"],
            },
            status=status.HTTP_200_OK,
        )


class AutoCompleteApi(APIView):
    @swagger_auto_schema(
        request_body=AutoCompleteRequestSerializer,
        responses={200: autocomplete_response},
    )
    def post(self, request):
        serializer = AutoCompleteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "nodes": autocomplete_schema(
                    serializer.data["content"], serializer.data["exclude"]
                )
            },
            status=status.HTTP_200_OK,
        )


class IncreaseProductScoreApi(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Product id",
                type=openapi.TYPE_INTEGER,
            )
        ]
    )
    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        product.score += 1
        product.save(update_fields=["score"])
        return Response({"score": product.score}, status=status.HTTP_200_OK)
