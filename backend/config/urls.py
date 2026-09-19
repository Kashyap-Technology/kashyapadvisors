from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from platform_app import api, seo
urlpatterns=[path('admin/',admin.site.urls),path('robots.txt',seo.robots),path('sitemap.xml',seo.sitemap),path('api/content/',api.content),path('api/regions/geometry/',api.geometry),path('api/inquiries/',api.inquiry),path('api/career-applications/',api.application),path('api/subscribe/',api.subscribe),path('media/private/<path:path>',lambda request,path:api.private_media(request,'private/'+path))]
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [re_path(r'^media/(?P<path>(?!private/).*)$',serve,{'document_root':settings.MEDIA_ROOT})]
