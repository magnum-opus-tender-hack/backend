from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="description",
        terms_of_service="https://akarpov.ru/about",
        contact=openapi.Contact(email="alexander.d.karpov@gmail.com"),
        license=openapi.License(name="License"),
    ),
    validators=["ssv"],
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/", include("conf.api")),
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
