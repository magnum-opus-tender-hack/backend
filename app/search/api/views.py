from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from search.api.serializers import HintRequestSerializer

from search.api.serializers import SearchSerializer, ResponseSerializer, HintResponseSerializer, AutoCompleteRequestSerializer, AutoCompleteResponseSerializer
from search.services.search import process_string
from search.services.autocomplete_schema import autocomplete_schema

user_response = openapi.Response("search results", ResponseSerializer)
hint_response = openapi.Response("hints", HintResponseSerializer)
autocomplete_response = openapi.Response("autocomplete schema", AutoCompleteResponseSerializer)


class SearchApi(APIView):
    @swagger_auto_schema(request_body=SearchSerializer, responses={200: user_response})
    def post(self, request, format=None):
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            process_string(serializer.data["body"]), status=status.HTTP_200_OK
        )


class HintApi(APIView):
    @swagger_auto_schema(request_body=HintRequestSerializer, responses={200: hint_response})
    def post(self, request, format=None):
        serializer = HintRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'type': 'category',
                'value': serializer.data['content']
            },
            status=status.HTTP_200_OK   
        )

class AutoCompleteApi(APIView):
    @swagger_auto_schema(request_body=AutoCompleteRequestSerializer, responses={200: autocomplete_response})
    def post(self, request, format=None):
        serializer = AutoCompleteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'nodes': autocomplete_schema(serializer.data['content'])
            }, status=status.HTTP_200_OK
        )
