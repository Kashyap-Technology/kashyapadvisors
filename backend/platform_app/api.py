import logging
from datetime import date
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import serializers
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from . import models as m
from django.db.models import Q, Prefetch
from zoneinfo import ZoneInfo

class SubmissionThrottle(AnonRateThrottle): scope='submissions'

def serialize(obj):
    data={}
    for field in obj._meta.fields:
        if field.name=='geometry': continue
        value=getattr(obj,field.attname)
        if field.is_relation: data[field.name]=value
        elif field.get_internal_type() in ['ImageField','FileField']: data[field.name]=value.url if value else ''
        else: data[field.name]=value
    if isinstance(obj,m.Article): data['category_name']=obj.category.title
    if isinstance(obj,m.SiteSettings):
        data['social_links']=[{'label':link.label,'url':link.url} for link in obj.social_link_items.filter(active=True)]
    if isinstance(obj,m.Course):
        data['details']=[{'id':v.pk,'key':v.key,'label':v.label,'presentation':v.presentation,
            'value':v.value,'source_url':v.source_url,'link_label':v.link_label} for v in obj.public_values]
        data['admission_calls']=[serialize(call) for call in obj.public_calls]
    if isinstance(obj,m.AdmissionCall) and obj.application_deadline:
        local = obj.application_deadline.astimezone(ZoneInfo(obj.timezone))
        data['application_deadline']=local.isoformat()
        data['timezone_abbreviation']=local.tzname()
    return data

@api_view(['GET'])
def content(request):
    courses=m.Course.objects.filter(published=True,university__published=True).filter(
        Q(department__isnull=True)|Q(department__published=True)).prefetch_related(
            Prefetch('field_values',queryset=m.CourseFieldValue.objects.filter(active=True),to_attr='public_values'),
            Prefetch('admission_calls',queryset=m.AdmissionCall.objects.filter(published=True),to_attr='public_calls'))
    updates=m.OfficialUpdate.objects.filter(published=True).filter(Q(expires_at__isnull=True)|Q(expires_at__gte=timezone.now()))
    return Response({'settings':serialize(m.SiteSettings.objects.first()) if m.SiteSettings.objects.exists() else {}, **{key:[serialize(x) for x in model.objects.filter(published=True)] for key,model in [('countries',m.Country),('regions',m.Region),('universities',m.University),('scholarships',m.Scholarship),('pages',m.Page),('articles',m.Article),('careers',m.Career)]},
        'updates':[serialize(x) for x in updates],
        'departments':[serialize(x) for x in m.Department.objects.filter(published=True,university__published=True)],
        'courses':[serialize(x) for x in courses],
        'testimonials':[serialize(x) for x in m.Testimonial.objects.filter(published=True,consent_confirmed=True)],'faqs':[serialize(x) for x in m.FAQ.objects.filter(published=True)],'categories':[serialize(x) for x in m.Category.objects.all()],'test_dates':[serialize(x) for x in m.TestDate.objects.filter(test__published=True)]})

@api_view(['GET'])
def geometry(request):
    return Response({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'id':r.id,'name':r.title,'slug':r.slug},'geometry':r.geometry} for r in m.Region.objects.filter(published=True) if r.geometry]})

class ConsentMixin:
    def validate_consent(self,value):
        if not value: raise serializers.ValidationError('Please consent to processing your submission.')
        return value
class InquirySerializer(ConsentMixin,serializers.ModelSerializer):
    consent=serializers.BooleanField(required=True)
    class Meta:
        model=m.Inquiry
        exclude=['status','notes','created_at']
        read_only_fields=['id']
    def validate(self,data):
        r,u=data.get('preferred_region'),data.get('preferred_university')
        if r and not r.published: raise serializers.ValidationError('Region unavailable.')
        if u and (not u.published or (r and u.region_id!=r.pk)): raise serializers.ValidationError('Select a university in your chosen region.')
        year=data.get('graduation_year')
        if year and not 1950<=year<=date.today().year+10: raise serializers.ValidationError('Enter a valid graduation year.')
        return data
class ApplicationSerializer(ConsentMixin,serializers.ModelSerializer):
    consent=serializers.BooleanField(required=True)
    class Meta:
        model=m.CareerApplication
        exclude=['status','notes','created_at']
        read_only_fields=['id']
    def validate_career(self,value):
        if not value.published or (value.deadline and value.deadline<date.today()): raise serializers.ValidationError('This vacancy is closed.')
        return value
    def validate_resume(self,file):
        if file.size>5*1024*1024: raise serializers.ValidationError('Maximum file size is 5 MB.')
        head=file.read(5); file.seek(0)
        if head!=b'%PDF-': raise serializers.ValidationError('Upload a valid PDF resume.')
        return file

def notify(obj):
    name=obj._meta.model_name
    note=m.Notification.objects.create(title=f'New {obj._meta.verbose_name}: {obj.full_name}',admin_path=f'/admin/platform_app/{name}/{obj.pk}/change/')
    if settings.NOTIFICATION_EMAIL:
        try:
            send_mail(note.title,'A new submission is available in the secure admin panel. Sign in to review it.',settings.DEFAULT_FROM_EMAIL,[settings.NOTIFICATION_EMAIL])
            note.emailed=True; note.save(update_fields=['emailed'])
        except Exception: logging.getLogger(__name__).exception('Submission saved; notification email failed')

@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def inquiry(request):
    s=InquirySerializer(data=request.data); s.is_valid(raise_exception=True)
    with transaction.atomic():
        obj=s.save(); transaction.on_commit(lambda:notify(obj))
    return Response({'id':obj.pk,'message':'Your inquiry has been received. Our team will contact you.'},status=201)

@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def application(request):
    s=ApplicationSerializer(data=request.data); s.is_valid(raise_exception=True)
    with transaction.atomic():
        obj=s.save(); transaction.on_commit(lambda:notify(obj))
    return Response({'id':obj.pk,'message':'Your application has been received.'},status=201)

@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def subscribe(request):
    class SubscriberSerializer(ConsentMixin,serializers.Serializer):
        email=serializers.EmailField()
        consent=serializers.BooleanField(required=True)
    s=SubscriberSerializer(data=request.data); s.is_valid(raise_exception=True)
    m.Subscriber.objects.get_or_create(email=s.validated_data['email'].lower(),defaults={'consent':True})
    return Response({'message':'Thank you. Your newsletter subscription is saved.'},status=201)

@staff_member_required
def private_media(request,path):
    from django.core.files.storage import default_storage
    if not default_storage.exists(path): raise Http404
    return FileResponse(default_storage.open(path,'rb'),as_attachment=True)
