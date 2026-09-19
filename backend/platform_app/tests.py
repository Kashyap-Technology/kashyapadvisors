from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth import get_user_model
from . import models as m
from .forms import CourseAdminForm, AdmissionCallForm


@override_settings(STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class CourseCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.region=m.Region.objects.create(title='Veneto',slug='veneto',code=5,published=True)
        cls.university=m.University.objects.create(title='University of Padua',slug='padua',region=cls.region,city='Padua',website='https://www.unipd.it',published=True)
        cls.other=m.University.objects.create(title='Other university',slug='other',region=cls.region,city='Other',website='https://example.com',published=True)
        cls.department=m.Department.objects.create(title='Comparative Biomedicine and Food Science',university=cls.university,address='Agripolis, Legnaro',published=True)
        cls.other_department=m.Department.objects.create(title='Other department',university=cls.other,published=True)
        cls.course=m.Course.objects.create(title='Animal Care',slug='animal-care',university=cls.university,department=cls.department,degree='Bachelor’s degree',discipline='Animal science',published=True)
        cls.admin=get_user_model().objects.create_superuser(username='catalog-admin',email='catalog@example.com',password='test-only-password')

    def test_course_requires_matching_department(self):
        for department in [None,self.other_department]:
            with self.subTest(department=department), self.assertRaises(ValidationError):
                m.Course.objects.create(title='Invalid',slug='invalid',university=self.university,department=department,degree='Bachelor',discipline='Science')

    def test_department_cannot_move_or_be_deleted_with_courses(self):
        self.department.university=self.other
        with self.assertRaises(ValidationError): self.department.save()
        self.department.refresh_from_db()
        with self.assertRaises(ProtectedError): self.department.delete()

    def test_admin_filters_departments_and_requires_selection(self):
        form=CourseAdminForm(data={'university':self.university.pk})
        self.assertQuerySetEqual(form.fields['department'].queryset,[self.department])
        self.assertFalse(form.is_valid())
        self.assertIn('department',form.errors)
        self.client.force_login(self.admin)
        response=self.client.get(f'/admin/platform_app/course/departments/{self.university.pk}/')
        self.assertEqual(response.json()['departments'],[{'id':self.department.pk,'title':self.department.title}])

    def call_data(self,**changes):
        return dict(course=self.course.pk,title='Non-EU call',academic_year='2027/2028',applicant_category='Non-EU applicants outside Italy',application_start='2027-01-07',application_deadline='2027-03-07T23:59:59',timezone='Europe/Rome',studies_commence='2027-10-01',instructions='Only for NON-EU applicants residing outside Italy.\nApplicants in Italy must use the EU and equated call.',published=True,order=0,**changes)

    def test_exact_deadline_round_trip_uses_rome_not_kathmandu(self):
        form=AdmissionCallForm(data=self.call_data())
        self.assertTrue(form.is_valid(),form.errors)
        call=form.save()
        call.refresh_from_db()
        self.assertEqual(call.application_deadline,datetime(2027,3,7,22,59,59,tzinfo=timezone.utc))
        self.assertEqual(AdmissionCallForm(instance=call).initial['application_deadline'],'2027-03-07T23:59:59')
        result=self.client.get('/api/content/').json()['courses'][0]['admission_calls'][0]
        self.assertEqual(result['application_deadline'],'2027-03-07T23:59:59+01:00')
        self.assertEqual(result['timezone_abbreviation'],'CET')
        self.assertEqual(result['studies_commence'],'2027-10-01')

    def test_invalid_dates_and_clock_changes_rejected(self):
        for changes in [
            {'application_deadline':'2027-01-06T23:59:59'},
            {'timezone':'not/a-zone'},
            {'application_deadline':'2027-03-28T02:30:00'},
            {'application_deadline':'2027-10-31T02:30:00'},
        ]:
            data=self.call_data();data.update(changes)
            with self.subTest(changes=changes):
                form=AdmissionCallForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertTrue('application_deadline' in form.errors or 'timezone' in form.errors)
        data=self.call_data();data['application_deadline']='2027-07-07T23:59:59'
        form=AdmissionCallForm(data=data)
        self.assertTrue(form.is_valid(),form.errors)
        self.assertEqual(form.cleaned_data['application_deadline'].utcoffset().total_seconds(),7200)

    def test_custom_fields_order_links_and_publication(self):
        for config in [dict(label='Custom amount',order=10),dict(label='Internal note',active=False),dict(label='Custom requirement',presentation='section',order=2)]:
            m.CourseFieldValue.objects.create(course=self.course,value='Paragraph one\nParagraph two',source_url='https://example.com/requirements',link_label='Official requirements',**config)
        m.AdmissionCall.objects.create(course=self.course,title='Draft round',academic_year='2027/2028',applicant_category='EU',published=False)
        result=self.client.get('/api/content/').json()
        self.assertEqual([d['label'] for d in result['courses'][0]['details']],['Custom requirement','Custom amount'])
        self.assertEqual(result['courses'][0]['details'][0]['link_label'],'Official requirements')
        self.assertEqual(result['courses'][0]['admission_calls'],[])
        self.department.published=False;self.department.save()
        self.assertEqual(self.client.get('/api/content/').json()['courses'],[])
        self.department.published=True;self.department.save()
        self.university.published=False;self.university.save()
        result=self.client.get('/api/content/').json()
        self.assertEqual(result['courses'],[])
        self.assertNotIn(self.department.pk,[d['id'] for d in result['departments']])

    def test_duplicate_field_value_rejected(self):
        m.CourseFieldValue.objects.create(course=self.course,label='Duration',value='One')
        with self.assertRaises(IntegrityError),transaction.atomic():
            m.CourseFieldValue.objects.create(course=self.course,label='Duration',value='Two')

    def test_admin_pages_and_inline_save(self):
        self.client.force_login(self.admin)
        for path in ['course/add/',f'course/{self.course.pk}/change/',f'university/{self.university.pk}/change/','department/add/','coursefieldvalue/add/']:
            with self.subTest(path=path):
                response=self.client.get('/admin/platform_app/'+path)
                self.assertEqual(response.status_code,200)
        data={'title':'New programme','slug':'new-programme','university':self.university.pk,'department':self.department.pk,'degree':'Bachelor','discipline':'Science','order':0,'published':'on',
            'field_values-TOTAL_FORMS':'1','field_values-INITIAL_FORMS':'0','field_values-MIN_NUM_FORMS':'0','field_values-MAX_NUM_FORMS':'1000',
            'field_values-0-label':'Entry qualification','field_values-0-presentation':'section','field_values-0-order':'0','field_values-0-active':'on','field_values-0-value':'Secondary diploma\nEnglish / Italian documents',
            'admission_calls-TOTAL_FORMS':'1','admission_calls-INITIAL_FORMS':'0','admission_calls-MIN_NUM_FORMS':'0','admission_calls-MAX_NUM_FORMS':'1000'}
        for key,value in self.call_data().items():
            if key!='course': data['admission_calls-0-'+key]=value
        response=self.client.post('/admin/platform_app/course/add/',data)
        self.assertEqual(response.status_code,302, response.context and [(str(f.formset.errors)) for f in response.context['inline_admin_formsets']])
        course=m.Course.objects.get(slug='new-programme')
        self.assertEqual(course.field_values.get().value,'Secondary diploma\nEnglish / Italian documents')
        self.assertEqual(course.admission_calls.get().application_deadline.astimezone(ZoneInfo('Europe/Rome')).second,59)

    def test_fields_are_owned_and_edited_independently_by_each_course(self):
        other_course=m.Course.objects.create(title='Other course',slug='other-course',university=self.university,department=self.department,degree='Master',discipline='Science',published=True)
        first=m.CourseFieldValue.objects.create(course=self.course,label='Duration',value='3 years')
        second=m.CourseFieldValue.objects.create(course=other_course,label='Duration',value='2 years')
        self.client.force_login(self.admin)
        response=self.client.post(f'/admin/platform_app/coursefieldvalue/{first.pk}/change/',{'course':self.course.pk,'label':'Nominal duration','value':'4 years','presentation':'fact','order':20})
        self.assertEqual(response.status_code,302)
        first.refresh_from_db();second.refresh_from_db()
        self.assertEqual(first.label,'Nominal duration')
        self.assertFalse(first.active)
        self.assertEqual(second.label,'Duration')
        self.assertEqual(second.value,'2 years')
        self.assertTrue(second.active)
        courses={c['id']:c for c in self.client.get('/api/content/').json()['courses']}
        self.assertEqual(courses[self.course.pk]['details'],[])
        self.assertEqual(courses[other_course.pk]['details'][0]['value'],'2 years')
        self.assertEqual(self.client.get('/admin/platform_app/coursefield/').status_code,404)
