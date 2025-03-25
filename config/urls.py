from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),

    path('', include("core.urls")),
    path('auth/', include("account.urls")),
    path('expense/', include("expense.urls")),
    path('income/', include("income.urls")),
    path('wallet/', include("wallet.urls")),
    path('transaction/', include("transaction.urls")),
]

urlpatterns += [
    path(
        "api/schema/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/schema/download/", SpectacularAPIView.as_view(), name="schema"),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
