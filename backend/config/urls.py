from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from platform_app import api, seo
from portal import api as portal_api
urlpatterns=[path('admin/',admin.site.urls),path('robots.txt',seo.robots),path('sitemap.xml',seo.sitemap),path('api/content/',api.content),path('api/regions/geometry/',api.geometry),path('api/inquiries/',api.inquiry),path('api/career-applications/',api.application),path('api/subscribe/',api.subscribe),path('api/auth/register/',portal_api.student_register),path('api/auth/login/',portal_api.student_login),path('api/auth/logout/',portal_api.student_logout),path('api/auth/me/',portal_api.student_me),path('api/student/profile/',portal_api.student_profile),path('api/student/profile/submit/',portal_api.student_profile_submit),path('api/student/documents/',portal_api.student_documents),path('api/student/documents/presign/',portal_api.student_document_presign),path('api/student/documents/<int:document_id>/download/',portal_api.student_document_download),path('api/student/checklist/',portal_api.student_checklist),path('api/student/applications/',portal_api.student_applications),path('api/student/recommendations/',portal_api.student_recommendations),path('media/private/<path:path>',lambda request,path:portal_api.private_media(request,'private/'+path))]
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [re_path(r'^media/(?P<path>(?!private/).*)$',serve,{'document_root':settings.MEDIA_ROOT})]
