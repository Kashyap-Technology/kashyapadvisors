import logging
from datetime import date
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.core.mail import send_mail

from . import models as m


class SubmissionThrottle(AnonRateThrottle):
    scope='submissions'


def serialize(obj):
    data={}
    for field in obj._meta.fields:
        if field.name=='geometry': continue
        value=getattr(obj,field.attname)
        if field.is_relation: data[field.name]=value
        elif field.get_internal_type() in ['ImageField','FileField']: data[field.name]=value.url if value else ''
        else: data[field.name]=value
    if isinstance(obj,m.Article): data['category_name']=obj.category.title
    if isinstance(obj,m.SiteSettings): data['social_links']=[{'label':link.label,'url':link.url} for link in obj.social_link_items.filter(active=True)]
    if isinstance(obj,m.Course):
        data['details']=[{'id':v.pk,'key':v.key,'label':v.label,'presentation':v.presentation,'value':v.value,'source_url':v.source_url,'link_label':v.link_label} for v in obj.public_values]
        data['admission_calls']=[serialize(call) for call in obj.public_calls]
    if isinstance(obj,m.AdmissionCall) and obj.application_deadline:
        local=obj.application_deadline.astimezone(ZoneInfo(obj.timezone)); data['application_deadline']=local.isoformat(); data['timezone_abbreviation']=local.tzname()
    return data


@api_view(['GET'])
def content(request):
    courses=m.Course.objects.filter(published=True,university__published=True).filter(Q(department__isnull=True)|Q(department__published=True)).prefetch_related(Prefetch('field_values',queryset=m.CourseFieldValue.objects.filter(active=True),to_attr='public_values'),Prefetch('admission_calls',queryset=m.AdmissionCall.objects.filter(published=True),to_attr='public_calls'))
    updates=m.OfficialUpdate.objects.filter(published=True).filter(Q(expires_at__isnull=True)|Q(expires_at__gte=timezone.now()))
    return Response({'settings':serialize(m.SiteSettings.objects.first()) if m.SiteSettings.objects.exists() else {},**{key:[serialize(x) for x in model.objects.filter(published=True)] for key,model in [('countries',m.Country),('regions',m.Region),('universities',m.University),('scholarships',m.Scholarship),('pages',m.Page),('articles',m.Article),('careers',m.Career)]},'updates':[serialize(x) for x in updates],'departments':[serialize(x) for x in m.Department.objects.filter(published=True,university__published=True)],'courses':[serialize(x) for x in courses],'testimonials':[serialize(x) for x in m.Testimonial.objects.filter(published=True,consent_confirmed=True)],'faqs':[serialize(x) for x in m.FAQ.objects.filter(published=True)],'categories':[serialize(x) for x in m.Category.objects.all()],'test_dates':[serialize(x) for x in m.TestDate.objects.filter(test__published=True)]})


@api_view(['GET'])
def geometry(request):
    return Response({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'id':region.id,'name':region.title,'slug':region.slug},'geometry':region.geometry} for region in m.Region.objects.filter(published=True) if region.geometry]})


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
        region,university=data.get('preferred_region'),data.get('preferred_university')
        if region and not region.published: raise serializers.ValidationError('Region unavailable.')
        if university and (not university.published or (region and university.region_id!=region.pk)): raise serializers.ValidationError('Select a university in your chosen region.')
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
    label=obj.full_name
    note=m.Notification.objects.create(title=f'New {obj._meta.verbose_name}: {label}',admin_path=f'/admin/platform_app/{name}/{obj.pk}/change/')
    if settings.NOTIFICATION_EMAIL:
        try:
            send_mail(note.title,'A new submission is available in the secure admin panel. Sign in to review it.',settings.DEFAULT_FROM_EMAIL,[settings.NOTIFICATION_EMAIL])
            note.emailed=True; note.save(update_fields=['emailed'])
        except Exception: logging.getLogger(__name__).exception('Submission saved; notification email failed')


@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def inquiry(request):
    serializer=InquirySerializer(data=request.data); serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        obj=serializer.save(); transaction.on_commit(lambda:notify(obj))
    return Response({'id':obj.pk,'message':'Your inquiry has been received. Our team will contact you.'},status=201)


@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def application(request):
    serializer=ApplicationSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    with transaction.atomic():
        obj=serializer.save(); transaction.on_commit(lambda:notify(obj))
    return Response({'id':obj.pk,'message':'Your application has been received.'},status=201)


@api_view(['POST'])
@throttle_classes([SubmissionThrottle])
def subscribe(request):
    class SubscriberSerializer(ConsentMixin,serializers.Serializer):
        email=serializers.EmailField()
        consent=serializers.BooleanField(required=True)
    serializer=SubscriberSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    m.Subscriber.objects.get_or_create(email=serializer.validated_data['email'].lower(),defaults={'consent':True})
    return Response({'message':'Thank you. Your newsletter subscription is saved.'},status=201)
