from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls import patterns, url, include
from rasplaytv import settings

urlpatterns = [
    # Examples:
    url(r'^', include('playtv.urls', namespace='playtv')),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)