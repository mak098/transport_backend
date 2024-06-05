
from django.contrib import admin
from django.urls import path, include
from django.conf import settings #add this
from django.conf.urls.static import static #add this
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/users/', include('authentication.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns.append(path('', admin.site.urls))

admin.site.site_header = 'VOYAGE'
admin.site.site_title = '243 voyage'
admin.site.index_title = 'voyage'
