"""
URL configuration for KALAKSHETRA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Return health status
    status = {
        "status": "healthy",
        "database": db_status,
    }
    return JsonResponse(status)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.master_data.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.hospital.urls')),
    path('api/', include('apps.doctors.urls')),
    # re_path(r'^(?!api/).*$', include('apps.web_pages.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
