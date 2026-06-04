from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('news/', include('news_verification.urls', namespace='news')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
