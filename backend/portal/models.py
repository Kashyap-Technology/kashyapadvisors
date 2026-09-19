from django.db import models


class StudentProfile(models.Model):
    STATUS_CHOICES=[('incomplete','Profile incomplete'),('submitted','Profile submitted'),('under_review','Under review'),('complete','Profile complete')]
    user = models.OneToOneField('auth.User',on_delete=models.CASCADE,related_name='student_profile')
    phone = models.CharField(max_length=40)
    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=40,blank=True)
    nationality = models.CharField(max_length=80,default='Nepali')
    passport_number = models.CharField(max_length=80,blank=True)
    passport_expiry = models.DateField(null=True,blank=True)
    citizenship_number = models.CharField(max_length=80,blank=True)
    address = models.TextField(blank=True)
    municipality = models.CharField(max_length=120,blank=True)
    district = models.CharField(max_length=100,blank=True)
    province = models.CharField(max_length=100,blank=True)
    emergency_contact_name = models.CharField(max_length=160,blank=True)
    emergency_contact_phone = models.CharField(max_length=40,blank=True)
    highest_qualification = models.CharField(max_length=120,blank=True)
    previous_degree = models.CharField(max_length=200,blank=True)
    previous_institution = models.CharField(max_length=240,blank=True)
    field_of_study = models.CharField(max_length=160,blank=True)
    grading_system = models.CharField(max_length=80,blank=True,help_text='For example: percentage, 4.0 GPA or CGPA.')
    overall_percentage = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    overall_gpa = models.DecimalField(max_digits=4,decimal_places=2,null=True,blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True,blank=True)
    academic_history = models.JSONField(default=list,blank=True)
    english_test = models.CharField(max_length=80,blank=True,help_text='For example: IELTS, PTE, TOEFL or Medium of Instruction.')
    english_score = models.CharField(max_length=80,blank=True)
    english_test_date = models.DateField(null=True,blank=True)
    other_language = models.CharField(max_length=80,blank=True)
    other_language_score = models.CharField(max_length=80,blank=True)
    target_degree = models.CharField(max_length=80,blank=True)
    target_disciplines = models.JSONField(default=list,blank=True)
    preferred_cities = models.JSONField(default=list,blank=True)
    profile_status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='incomplete')
    submitted_at = models.DateTimeField(null=True,blank=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='platform_app_studentprofile'

    def __str__(self): return f'{self.user.get_full_name() or self.user.email} — student profile'


class StudentChecklistRequirement(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    accepted_extensions = models.CharField(max_length=120,default='pdf,jpg,jpeg,png',help_text='Comma-separated file extensions.')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table='platform_app_studentchecklistrequirement'
        ordering=['order','pk']
    def __str__(self): return self.title


class StudentChecklistItem(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('uploaded','Uploaded'),('verified','Verified'),('rejected','Needs replacement'),('not_applicable','Not applicable')]
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='checklist_items')
    requirement = models.ForeignKey(StudentChecklistRequirement,on_delete=models.PROTECT,related_name='student_items')
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    admin_note = models.TextField(blank=True)
    visible_to_student = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='platform_app_studentchecklistitem'
        ordering=['requirement__order','pk']
        constraints=[models.UniqueConstraint(fields=['student','requirement'],name='unique_student_checklist_requirement')]

    def __str__(self): return f'{self.student} — {self.requirement.title}'


class StudentDocument(models.Model):
    STATUS_CHOICES=[('pending','Pending review'),('verified','Verified'),('rejected','Needs replacement')]
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='documents')
    checklist_item = models.ForeignKey(StudentChecklistItem,on_delete=models.SET_NULL,null=True,blank=True,related_name='documents')
    document_type = models.CharField(max_length=80)
    file = models.FileField(upload_to='private/student-documents/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120,blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    admin_note = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        db_table='platform_app_studentdocument'
        ordering=['-uploaded_at']
    def __str__(self): return f'{self.student} — {self.original_name}'


class StudentApplication(models.Model):
    STATUS_CHOICES=[('draft','Draft'),('submitted','Submitted'),('under_review','Under review'),('more_information','More information needed'),('ready_to_apply','Ready to apply'),('submitted_to_university','Submitted to university'),('accepted','Accepted'),('rejected','Not accepted'),('withdrawn','Withdrawn')]
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='applications')
    course = models.ForeignKey('platform_app.Course',on_delete=models.PROTECT,related_name='student_applications',null=True,blank=True)
    reference_code = models.CharField(max_length=30,unique=True)
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default='draft')
    student_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='platform_app_studentapplication'
        ordering=['-updated_at']
    def __str__(self): return self.reference_code


class StudentApplicationStage(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('current','In progress'),('complete','Complete'),('blocked','Action needed')]
    application = models.ForeignKey(StudentApplication,on_delete=models.CASCADE,related_name='stages')
    key = models.SlugField()
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    visible_to_student = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='platform_app_studentapplicationstage'
        ordering=['order','pk']
        constraints=[models.UniqueConstraint(fields=['application','key'],name='unique_application_stage')]

    def __str__(self): return f'{self.application.reference_code} — {self.title}'


class StudentRecommendationRequest(models.Model):
    KIND_CHOICES=[('ai','AI course guidance'),('admission_head','Admission Head review')]
    STATUS_CHOICES=[('requested','Requested'),('in_progress','In progress'),('ready','Ready'),('needs_information','Needs more information')]
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='recommendation_requests')
    kind = models.CharField(max_length=30,choices=KIND_CHOICES)
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default='requested')
    student_question = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='platform_app_studentrecommendationrequest'
        ordering=['-created_at']


class StudentRecommendation(models.Model):
    request = models.ForeignKey(StudentRecommendationRequest,on_delete=models.CASCADE,related_name='recommendations')
    course = models.ForeignKey('platform_app.Course',on_delete=models.PROTECT,null=True,blank=True)
    title = models.CharField(max_length=240,blank=True)
    rationale = models.TextField()
    fit_score = models.PositiveSmallIntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='platform_app_studentrecommendation'

    def __str__(self): return self.title or self.course.title if self.course else 'Student recommendation'
