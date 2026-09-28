import json
import logging
import re
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from platform_app.models import Course, Notification
from . import models as m


class StudentAuthThrottle(AnonRateThrottle):
    scope='student_auth'


STUDENT_MAX_FILE_SIZE=10*1024*1024
STUDENT_ALLOWED_EXTENSIONS={'pdf','jpg','jpeg','png','doc','docx'}
STUDENT_PROFILE_FIELDS={
    'phone','date_of_birth','gender','nationality','passport_number','passport_expiry','citizenship_number',
    'address','municipality','district','province','emergency_contact_name','emergency_contact_phone',
    'highest_qualification','previous_degree','previous_institution','field_of_study','grading_system',
    'overall_percentage','overall_gpa','graduation_year','academic_history','english_test','english_score',
    'english_test_date','other_language','other_language_score','target_degree','target_disciplines','preferred_cities',
}


def ensure_student_checklist(profile):
    for requirement in m.StudentChecklistRequirement.objects.filter(active=True):
        m.StudentChecklistItem.objects.get_or_create(student=profile,requirement=requirement)


def profile_completion(profile):
    required=['phone','date_of_birth','nationality','address','district','province','previous_degree','previous_institution','field_of_study','grading_system','graduation_year','english_test','english_score','target_degree']
    complete=sum(bool(getattr(profile,field,None)) for field in required)
    return round(complete/len(required)*100)


def student_profile_payload(profile):
    data={field.name:getattr(profile,field.name) for field in profile._meta.fields if field.name not in {'id','user','created_at','updated_at','admin_note'}}
    data.update({'id':profile.pk,'email':profile.user.email,'first_name':profile.user.first_name,'last_name':profile.user.last_name,'profile_completion':profile_completion(profile)})
    return data


def checklist_payload(item):
    return {'id':item.pk,'key':item.requirement.key,'title':item.requirement.title,'description':item.requirement.description,'required':item.requirement.required,'accepted_extensions':item.requirement.accepted_extensions,'status':item.status,'admin_note':item.admin_note,'visible_to_student':item.visible_to_student}


def document_payload(document):
    return {'id':document.pk,'document_type':document.document_type,'original_name':document.original_name,'file_size':document.file_size,'content_type':document.content_type,'status':document.status,'admin_note':document.admin_note,'uploaded_at':document.uploaded_at,'checklist_item':document.checklist_item_id}


def application_payload(application):
    course=application.course
    return {'id':application.pk,'reference_code':application.reference_code,'status':application.status,'status_label':application.get_status_display(),'student_note':application.student_note,'submitted_at':application.submitted_at,'created_at':application.created_at,'updated_at':application.updated_at,'course':{'id':course.pk,'title':course.title,'slug':course.slug,'degree':course.degree,'university':course.university.title} if course else None,'stages':[{'id':stage.pk,'key':stage.key,'title':stage.title,'description':stage.description,'status':stage.status,'status_label':stage.get_status_display(),'order':stage.order} for stage in application.stages.filter(visible_to_student=True)]}


def recommendation_payload(request):
    return {'id':request.pk,'kind':request.kind,'status':request.status,'student_question':request.student_question,'created_at':request.created_at,'updated_at':request.updated_at,'recommendations':[{'id':item.pk,'title':item.title,'course_id':item.course_id,'course_title':item.course.title if item.course else '','rationale':item.rationale,'fit_score':item.fit_score} for item in request.recommendations.select_related('course')]}


def ai_course_recommendations(profile,request):
    if not settings.OPENAI_API_KEY: return False
    courses=list(Course.objects.filter(published=True,university__published=True).select_related('university').order_by('pk')[:250])
    catalog=[{'id':course.pk,'title':course.title,'university':course.university.title,'degree':course.degree,'discipline':course.discipline,'language':course.study_language,'location':course.study_location,'tuition':course.tuition_fee or course.tuition,'summary':course.summary[:500]} for course in courses]
    student={'previous_degree':profile.previous_degree,'previous_institution':profile.previous_institution,'field_of_study':profile.field_of_study,'grading_system':profile.grading_system,'overall_percentage':str(profile.overall_percentage or ''),'overall_gpa':str(profile.overall_gpa or ''),'graduation_year':profile.graduation_year,'english_test':profile.english_test,'english_score':profile.english_score,'target_degree':profile.target_degree,'target_disciplines':profile.target_disciplines,'preferred_cities':profile.preferred_cities,'question':request.student_question}
    prompt='Recommend up to five courses only from the supplied catalog for this Nepalese student. Do not invent courses or eligibility. Treat this as educational guidance, not an admission or visa decision. Return only valid JSON: {"recommendations":[{"course_id":123,"rationale":"...","fit_score":85}]}.'+'\n\nSTUDENT:\n'+json.dumps(student,ensure_ascii=False)+'\n\nCATALOG:\n'+json.dumps(catalog,ensure_ascii=False)
    body=json.dumps({'model':settings.OPENAI_MODEL,'store':False,'instructions':'You are a careful international admissions guidance assistant. Use only the supplied catalog and student facts.','input':prompt,'temperature':0.2,'max_output_tokens':1800}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':f'Bearer {settings.OPENAI_API_KEY}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=30) as response: payload=json.loads(response.read().decode())
        text=payload.get('output_text','') or ''.join(part.get('text','') for item in payload.get('output',[]) for part in item.get('content',[]) if part.get('type')=='output_text')
        parsed=json.loads(text); allowed={course.pk:course for course in courses}; created=0
        for recommendation in parsed.get('recommendations',[])[:5]:
            course=allowed.get(int(recommendation.get('course_id',0)))
            if not course: continue
            rationale=str(recommendation.get('rationale','')).strip()[:5000]
            if not rationale: continue
            score=recommendation.get('fit_score'); score=int(score) if isinstance(score,(int,float)) else None
            m.StudentRecommendation.objects.create(request=request,course=course,title=course.title,rationale=rationale,fit_score=max(0,min(100,score)) if score is not None else None); created+=1
        request.status='ready' if created else 'needs_information'; request.save(update_fields=['status','updated_at']); return bool(created)
    except (urllib.error.URLError,TimeoutError,json.JSONDecodeError,ValueError,KeyError,TypeError) as error:
        logging.getLogger(__name__).warning('AI course recommendation deferred: %s',error)
        return False


def storj_client():
    if not settings.USE_STORJ or not settings.STORJ_ACCESS_KEY or not settings.STORJ_SECRET_KEY or not settings.STORJ_BUCKET:
        raise RuntimeError('Storj presigned uploads are not configured.')
    return boto3.client('s3',aws_access_key_id=settings.STORJ_ACCESS_KEY,aws_secret_access_key=settings.STORJ_SECRET_KEY,endpoint_url=settings.STORJ_ENDPOINT,region_name='us-east-1',config=Config(signature_version='s3v4'))


def student_object_key(user,filename):
    extension=Path(filename).suffix.lower().lstrip('.')
    stem=re.sub(r'[^a-z0-9]+','-',Path(filename).stem.lower()).strip('-')[:80] or 'document'
    return f'private/student-documents/{user.pk}/{uuid.uuid4().hex}-{stem}.{extension}'


def student_profile_for(user):
    profile,created=m.StudentProfile.objects.get_or_create(user=user,defaults={'phone':''})
    if created: ensure_student_checklist(profile)
    return profile


def notify(obj):
    name=obj._meta.model_name
    person=getattr(obj,'full_name',None) or getattr(getattr(obj,'student',None),'user',None)
    label=person.get_full_name() if person and hasattr(person,'get_full_name') else getattr(person,'email',str(person or 'student'))
    note=Notification.objects.create(title=f'New {obj._meta.verbose_name}: {label}',admin_path=f'/admin/portal/{name}/{obj.pk}/change/')
    if settings.NOTIFICATION_EMAIL:
        try:
            send_mail(note.title,'A new student portal submission is available in the secure admin panel. Sign in to review it.',settings.DEFAULT_FROM_EMAIL,[settings.NOTIFICATION_EMAIL])
            note.emailed=True; note.save(update_fields=['emailed'])
        except Exception: logging.getLogger(__name__).exception('Submission saved; notification email failed')


class StudentRegistrationSerializer(serializers.Serializer):
    email=serializers.EmailField()
    phone=serializers.CharField(max_length=40)
    password=serializers.CharField(min_length=8,write_only=True)
    password_confirm=serializers.CharField(min_length=8,write_only=True)
    first_name=serializers.CharField(max_length=150,required=False,allow_blank=True)
    last_name=serializers.CharField(max_length=150,required=False,allow_blank=True)

    def validate_email(self,value):
        value=value.strip().lower()
        if get_user_model().objects.filter(email__iexact=value).exists(): raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self,data):
        if data['password']!=data['password_confirm']: raise serializers.ValidationError({'password_confirm':'Passwords do not match.'})
        validate_password(data['password'])
        return data


class StudentLoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([StudentAuthThrottle])
def student_register(request):
    serializer=StudentRegistrationSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    data=serializer.validated_data; User=get_user_model()
    with transaction.atomic():
        user=User.objects.create_user(username=data['email'],email=data['email'],password=data['password'],first_name=data.get('first_name',''),last_name=data.get('last_name',''))
        profile=m.StudentProfile.objects.create(user=user,phone=data['phone']); ensure_student_checklist(profile)
        token=Token.objects.create(user=user)
    return Response({'token':token.key,'profile':student_profile_payload(profile),'message':'Your student account is ready. Complete your profile to continue.'},status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([StudentAuthThrottle])
def student_login(request):
    serializer=StudentLoginSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    user=authenticate(request,username=serializer.validated_data['email'].lower(),password=serializer.validated_data['password'])
    if not user or not user.is_active: raise serializers.ValidationError('Email or password is incorrect.')
    profile=student_profile_for(user); token,_=Token.objects.get_or_create(user=user)
    return Response({'token':token.key,'profile':student_profile_payload(profile)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_logout(request):
    Token.objects.filter(user=request.user).delete(); return Response({'message':'You have been signed out.'})


def portal_payload(profile):
    ensure_student_checklist(profile)
    return {'profile':student_profile_payload(profile),'checklist':[checklist_payload(item) for item in profile.checklist_items.select_related('requirement').filter(visible_to_student=True)],'documents':[document_payload(doc) for doc in profile.documents.all()],'applications':[application_payload(application) for application in profile.applications.select_related('course','course__university').prefetch_related('stages')],'recommendations':[recommendation_payload(item) for item in profile.recommendation_requests.prefetch_related('recommendations__course')]}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_me(request):
    return Response(portal_payload(student_profile_for(request.user)))


@api_view(['GET','PATCH'])
@permission_classes([IsAuthenticated])
def student_profile(request):
    profile=student_profile_for(request.user)
    if request.method=='PATCH':
        data=request.data.copy(); first_name=data.pop('first_name',None); last_name=data.pop('last_name',None)
        if first_name is not None: request.user.first_name=str(first_name).strip()
        if last_name is not None: request.user.last_name=str(last_name).strip()
        request.user.save(update_fields=['first_name','last_name'])
        invalid=set(data)-STUDENT_PROFILE_FIELDS
        if invalid: raise serializers.ValidationError({'detail':f'Unsupported profile fields: {", ".join(sorted(invalid))}.'})
        for field,value in data.items(): setattr(profile,field,value)
        profile.save()
    return Response(student_profile_payload(profile))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_profile_submit(request):
    profile=student_profile_for(request.user)
    required={'first_name':request.user.first_name,'last_name':request.user.last_name,'phone':profile.phone,'date_of_birth':profile.date_of_birth,'nationality':profile.nationality,'address':profile.address,'district':profile.district,'province':profile.province,'previous_degree':profile.previous_degree,'previous_institution':profile.previous_institution,'field_of_study':profile.field_of_study,'grading_system':profile.grading_system,'graduation_year':profile.graduation_year,'english_test':profile.english_test,'english_score':profile.english_score,'target_degree':profile.target_degree}
    missing=[label.replace('_',' ') for label,value in required.items() if not value]
    if not (profile.overall_percentage or profile.overall_gpa): missing.append('percentage or GPA')
    if not (profile.passport_number or profile.citizenship_number): missing.append('passport or citizenship number')
    if missing: return Response({'detail':'Complete these profile fields before submitting: '+', '.join(missing)+'.'},status=400)
    profile.profile_status='submitted'; profile.submitted_at=timezone.now(); profile.save(update_fields=['profile_status','submitted_at','updated_at'])
    return Response({'message':'Your profile has been submitted for review.','profile':student_profile_payload(profile)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_checklist(request):
    profile=student_profile_for(request.user); ensure_student_checklist(profile)
    return Response({'items':[checklist_payload(item) for item in profile.checklist_items.select_related('requirement').filter(visible_to_student=True)]})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_document_presign(request):
    profile=student_profile_for(request.user); filename=str(request.data.get('file_name','')).strip(); content_type=str(request.data.get('content_type','application/octet-stream')).strip()
    try: file_size=int(request.data.get('file_size',0))
    except (TypeError,ValueError): file_size=0
    extension=Path(filename).suffix.lower().lstrip('.')
    if not filename or extension not in STUDENT_ALLOWED_EXTENSIONS: return Response({'detail':'Upload a PDF, JPG, PNG, DOC or DOCX file.'},status=400)
    if file_size<=0 or file_size>STUDENT_MAX_FILE_SIZE: return Response({'detail':'Each document must be between 1 byte and 10 MB.'},status=400)
    checklist_id=request.data.get('checklist_item'); item=None
    if checklist_id:
        item=get_object_or_404(m.StudentChecklistItem,pk=checklist_id,student=profile); allowed={x.strip().lower().lstrip('.') for x in item.requirement.accepted_extensions.split(',') if x.strip()}
        if allowed and extension not in allowed: return Response({'detail':f'This checklist item accepts: {", ".join(sorted(allowed))}.'},status=400)
    try:
        client=storj_client(); key=student_object_key(request.user,filename); upload_url=client.generate_presigned_url('put_object',Params={'Bucket':settings.STORJ_BUCKET,'Key':key,'ContentType':content_type},ExpiresIn=900,HttpMethod='PUT')
    except RuntimeError as error: return Response({'detail':str(error)},status=503)
    return Response({'key':key,'upload_url':upload_url,'expires_in':900,'headers':{'Content-Type':content_type}})


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def student_documents(request):
    profile=student_profile_for(request.user)
    if request.method=='GET': return Response({'documents':[document_payload(doc) for doc in profile.documents.all()]})
    key=str(request.data.get('key','')); filename=str(request.data.get('file_name','')).strip(); content_type=str(request.data.get('content_type','')); prefix=f'private/student-documents/{request.user.pk}/'
    if not key.startswith(prefix) or '..' in key or not filename: return Response({'detail':'Invalid upload key.'},status=400)
    try: metadata=storj_client().head_object(Bucket=settings.STORJ_BUCKET,Key=key)
    except RuntimeError as error: return Response({'detail':str(error)},status=503)
    except ClientError: return Response({'detail':'The uploaded object could not be found. Please try again.'},status=400)
    size=int(metadata.get('ContentLength',0)); extension=Path(filename).suffix.lower().lstrip('.')
    if size<=0 or size>STUDENT_MAX_FILE_SIZE or extension not in STUDENT_ALLOWED_EXTENSIONS: return Response({'detail':'The uploaded document is invalid or exceeds 10 MB.'},status=400)
    item=None
    if request.data.get('checklist_item'): item=get_object_or_404(m.StudentChecklistItem,pk=request.data['checklist_item'],student=profile)
    document=m.StudentDocument(student=profile,checklist_item=item,document_type=str(request.data.get('document_type','other')),file=key,original_name=filename,file_size=size,content_type=content_type or metadata.get('ContentType','')); document.save()
    if item: item.status='uploaded'; item.save(update_fields=['status','updated_at'])
    return Response({'document':document_payload(document)},status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_document_download(request,document_id):
    profile=student_profile_for(request.user); document=get_object_or_404(m.StudentDocument,pk=document_id,student=profile)
    try: url=storj_client().generate_presigned_url('get_object',Params={'Bucket':settings.STORJ_BUCKET,'Key':document.file.name},ExpiresIn=600,HttpMethod='GET')
    except RuntimeError as error: return Response({'detail':str(error)},status=503)
    return Response({'download_url':url,'expires_in':600})


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def student_applications(request):
    profile=student_profile_for(request.user)
    if request.method=='GET': return Response({'applications':[application_payload(application) for application in profile.applications.select_related('course','course__university').prefetch_related('stages')]})
    if profile.profile_status not in {'submitted','under_review','complete'}: return Response({'detail':'Submit your completed profile before starting an application.'},status=400)
    course_id=request.data.get('course'); course=get_object_or_404(Course,pk=course_id,published=True) if course_id else None
    if course and profile.applications.filter(course=course).exclude(status__in={'rejected','withdrawn'}).exists(): return Response({'detail':'You already have an active application for this course.'},status=400)
    reference=f'KA-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}'; application=m.StudentApplication.objects.create(student=profile,course=course,reference_code=reference,status='submitted',submitted_at=timezone.now())
    for order,key,title in [(1,'profile','Profile review'),(2,'documents','Document verification'),(3,'application','Application preparation'),(4,'university','University decision')]: m.StudentApplicationStage.objects.create(application=application,key=key,title=title,order=order,status='current' if order==1 else 'pending')
    transaction.on_commit(lambda:notify(application))
    return Response({'application':application_payload(application)},status=201)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def student_recommendations(request):
    profile=student_profile_for(request.user)
    if request.method=='GET': return Response({'requests':[recommendation_payload(item) for item in profile.recommendation_requests.prefetch_related('recommendations__course')]})
    if profile.profile_status not in {'submitted','under_review','complete'}: return Response({'detail':'Submit your completed profile before requesting recommendations.'},status=400)
    kind=request.data.get('kind')
    if kind not in {'ai','admission_head'}: return Response({'detail':'Choose ai or admission_head.'},status=400)
    item=m.StudentRecommendationRequest.objects.create(student=profile,kind=kind,student_question=str(request.data.get('student_question',''))[:5000]); transaction.on_commit(lambda:notify(item))
    if kind=='ai': ai_course_recommendations(profile,item)
    return Response({'request':recommendation_payload(item),'message':'Your recommendation request has been added to the portal.'},status=201)


@staff_member_required
def private_media(request,path):
    from django.core.files.storage import default_storage
    if not default_storage.exists(path): raise Http404
    return FileResponse(default_storage.open(path,'rb'),as_attachment=True)
