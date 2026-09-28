from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from . import models as m


@override_settings(STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}},USE_STORJ=True,STORJ_ACCESS_KEY='test-access',STORJ_SECRET_KEY='test-secret',STORJ_BUCKET='student-documents',STORJ_ENDPOINT='https://gateway.storjshare.io')
class StudentPortalTests(TestCase):
    def post_json(self,path,data,headers=None):
        return self.client.post(path,data=data,content_type='application/json',**(headers or {}))

    def patch_json(self,path,data,headers=None):
        return self.client.patch(path,data=data,content_type='application/json',**(headers or {}))

    def register(self):
        response=self.post_json('/api/auth/register/',{'email':'student@gmail.com','phone':'+9779800000000','password':'Strong-Student-Password-9','password_confirm':'Strong-Student-Password-9','first_name':'Sita','last_name':'Sharma'})
        self.assertEqual(response.status_code,201,response.content)
        return response.json()

    def auth(self,token): return {'HTTP_AUTHORIZATION':f'Token {token}'}

    def test_student_registration_profile_submission_and_checklist(self):
        result=self.register(); token=result['token']
        self.assertEqual(result['profile']['profile_status'],'incomplete')
        self.assertGreaterEqual(len(self.client.get('/api/student/checklist/',**self.auth(token)).json()['items']),7)
        response=self.patch_json('/api/student/profile/',{'phone':'+9779800000000','date_of_birth':'2000-01-01','gender':'Female','nationality':'Nepali','passport_number':'PA1234567','passport_expiry':'2030-01-01','address':'Kathmandu','municipality':'Kathmandu Metropolitan','district':'Kathmandu','province':'Bagmati','emergency_contact_name':'Parent','emergency_contact_phone':'+9779811111111','highest_qualification':'+2 / NEB','previous_degree':'+2 Science','previous_institution':'National College','field_of_study':'Science','grading_system':'Percentage','overall_percentage':82.5,'graduation_year':2022,'english_test':'IELTS','english_score':'7.0','target_degree':"Bachelor's",'target_disciplines':['Computer Science'],'preferred_cities':['Milan']},self.auth(token))
        self.assertEqual(response.status_code,200,response.content)
        response=self.client.post('/api/student/profile/submit/',**self.auth(token))
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(response.json()['profile']['profile_status'],'submitted')
        self.assertEqual(self.post_json('/api/auth/login/',{'email':'student@gmail.com','password':'Strong-Student-Password-9'}).status_code,200)

    def test_presigned_upload_is_finalized_without_sending_file_through_django(self):
        result=self.register(); token=result['token']; item=self.client.get('/api/student/checklist/',**self.auth(token)).json()['items'][0]
        fake=Mock(); fake.generate_presigned_url.side_effect=['https://storj.example/upload','https://storj.example/download']; fake.head_object.return_value={'ContentLength':1024,'ContentType':'application/pdf'}
        with patch('portal.api.storj_client',return_value=fake):
            response=self.post_json('/api/student/documents/presign/',{'file_name':'passport.pdf','content_type':'application/pdf','file_size':1024,'checklist_item':item['id']},self.auth(token))
            self.assertEqual(response.status_code,200,response.content)
            key=response.json()['key']; self.assertTrue(key.startswith('private/student-documents/'))
            response=self.post_json('/api/student/documents/',{'key':key,'file_name':'passport.pdf','content_type':'application/pdf','document_type':'passport','checklist_item':item['id']},self.auth(token))
            self.assertEqual(response.status_code,201,response.content)
            self.assertEqual(response.json()['document']['status'],'pending')
            response=self.client.get(f"/api/student/documents/{response.json()['document']['id']}/download/",**self.auth(token))
            self.assertEqual(response.status_code,200,response.content)
            self.assertEqual(response.json()['download_url'],'https://storj.example/download')
        self.assertEqual(m.StudentDocument.objects.count(),1)
