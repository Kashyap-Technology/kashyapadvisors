from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.utils.text import slugify

class Content(models.Model):
    title = models.CharField(max_length=240)
    slug = models.SlugField(unique=True,max_length=240)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='content/%Y/%m/',blank=True)
    image_url = models.URLField(blank=True)
    sections = models.JSONField(default=list,blank=True,help_text='List of {heading, body, kind, source_url}. kind: guidance, official, estimate.')
    published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    source_url = models.URLField(blank=True)
    reviewed_at = models.DateField(null=True,blank=True)
    class Meta:
        abstract = True
        ordering = ['order','title']
    def __str__(self): return self.title

class SiteSettings(models.Model):
    title = models.CharField(max_length=100,default='Kashyap Advisors')
    logo = models.ImageField(upload_to='brand/',blank=True)
    address = models.CharField(max_length=240,blank=True)
    phone = models.CharField(max_length=40,blank=True)
    support_phone = models.CharField(max_length=40,blank=True)
    whatsapp = models.CharField(max_length=40,blank=True)
    email = models.EmailField(blank=True)
    office_hours = models.CharField(max_length=160,blank=True)
    announcement = models.CharField(max_length=300,blank=True)
    hero_title = models.CharField(max_length=160,default='Your future. Made in Italy.')
    hero_description = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='brand/',blank=True)
    social_links = models.JSONField(default=list,blank=True)
    footer_text = models.TextField(blank=True)
    def save(self,*args,**kwargs): self.pk=1; super().save(*args,**kwargs)
    def __str__(self): return 'Website settings'


class SocialLink(models.Model):
    settings = models.ForeignKey(SiteSettings,on_delete=models.CASCADE,related_name='social_link_items')
    label = models.CharField(max_length=80,help_text='For example: Facebook, Instagram or TikTok.')
    url = models.URLField(help_text='Paste the complete https:// link.')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order','pk']
        verbose_name = 'Social link'
        verbose_name_plural = 'Social links'

    def __str__(self): return self.label


class OfficialUpdate(models.Model):
    KIND_CHOICES=[('deadline','Deadline / test'),('scholarship','Scholarship / accommodation'),('admission','Admission update'),('general','General update')]
    title = models.CharField(max_length=240)
    slug = models.SlugField(unique=True,max_length=240)
    summary = models.TextField(help_text='Short text shown in the alert and update list.')
    body = models.TextField(help_text='Detailed explanation. Use a blank line between paragraphs.')
    kind = models.CharField(max_length=30,choices=KIND_CHOICES,default='general')
    source_label = models.CharField(max_length=160,default='Official source')
    source_url = models.URLField()
    published_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True,blank=True,help_text='Optional. Hide this update from the live alert after this time.')
    published = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False,help_text='Show this update as the live notice on the homepage.')
    class Meta:
        ordering=['-pinned','-published_at','-pk']
        verbose_name='Official update'
        verbose_name_plural='Official updates'
    def __str__(self): return self.title

class Scholarship(Content):
    authority = models.CharField(max_length=200)
    deadline = models.DateField(null=True,blank=True)
    eligibility = models.TextField(blank=True)

class Region(Content):
    code = models.PositiveSmallIntegerField(unique=True)
    cities = models.JSONField(default=list)
    scholarship = models.ForeignKey(Scholarship,on_delete=models.SET_NULL,null=True,blank=True,related_name='regions')
    living_cost = models.CharField(max_length=160,blank=True)
    geometry = models.JSONField(default=dict,blank=True,help_text='GeoJSON geometry; seeded from openpolis ISTAT boundaries')

class Country(models.Model):
    name = models.CharField(max_length=120,unique=True)
    slug = models.SlugField(unique=True)
    code = models.CharField(max_length=2,unique=True,help_text='Two-letter country code, for example IT.')
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self): return self.name

class University(Content):
    country = models.ForeignKey(Country,on_delete=models.PROTECT,related_name='universities')
    region = models.ForeignKey(Region,on_delete=models.PROTECT,related_name='universities')
    city = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='universities/logos/',blank=True)
    logo_url = models.URLField(blank=True,help_text='Official university logo or favicon URL used when no uploaded logo is available.')
    institution_type = models.CharField(max_length=10,choices=[('public','Public'),('private','Private')],default='public')
    english_taught = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    disciplines = models.JSONField(default=list)
    degrees = models.JSONField(default=list)
    latitude = models.FloatField(default=41.9)
    longitude = models.FloatField(default=12.5)
    tuition = models.CharField(max_length=200,blank=True)
    deadline = models.DateField(null=True,blank=True)
    website = models.URLField()

class Department(models.Model):
    university = models.ForeignKey(University,on_delete=models.CASCADE,related_name='departments')
    title = models.CharField(max_length=240)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order','title']
        constraints = [models.UniqueConstraint(fields=['university','title'],name='unique_university_department')]

    def __str__(self): return f'{self.title} — {self.university.title}'

    def clean(self):
        super().clean()
        if self.pk and self.courses.exclude(university_id=self.university_id).exists():
            raise ValidationError({'university':'A department with courses cannot be moved to another university.'})

    def save(self,*args,**kwargs):
        self.clean()
        return super().save(*args,**kwargs)

class Course(Content):
    university = models.ForeignKey(University,on_delete=models.CASCADE,related_name='courses')
    department = models.ForeignKey(Department,on_delete=models.PROTECT,related_name='courses',null=True,blank=True,
        help_text='Choose a department belonging to this university. Required for new courses.')
    degree = models.CharField(max_length=40)
    discipline = models.CharField(max_length=100)
    english_taught = models.BooleanField(default=False)
    deadline = models.DateField(null=True,blank=True)
    tuition = models.CharField(max_length=200,blank=True)
    degree_class_code = models.CharField(max_length=80,blank=True)
    study_location = models.CharField(max_length=240,blank=True)
    course_type = models.CharField(max_length=160,blank=True,help_text='For example: Bachelor’s degree, full-time.')
    nominal_duration = models.CharField(max_length=100,blank=True,help_text='For example: 3 years (180 ECTS).')
    study_language = models.CharField(max_length=120,blank=True)
    application_fee = models.CharField(max_length=200,blank=True)
    pre_enrollment_fee = models.CharField(max_length=200,blank=True)
    tuition_fee = models.CharField(max_length=200,blank=True)
    cent_requirements = models.TextField(blank=True)
    language_requirements = models.TextField(blank=True)
    other_requirements = models.TextField(blank=True)
    studies_commence = models.DateField(null=True,blank=True)
    more_information = models.URLField(blank=True)
    entry_qualification = models.TextField(blank=True)
    course_link = models.URLField(blank=True)
    additional_info = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if not self.department_id and self._state.adding:
            raise ValidationError({'department':'Choose a department for this course.'})
        if self.department_id and self.department.university_id != self.university_id:
            raise ValidationError({'department':'The department must belong to the selected university.'})

    def save(self,*args,**kwargs):
        self.clean()
        return super().save(*args,**kwargs)

class CourseField(models.Model):
    label = models.CharField(max_length=160)
    key = models.SlugField(unique=True,help_text='Stable identifier, such as study-location or entry-qualification.')
    presentation = models.CharField(max_length=10,choices=[('fact','Overview row'),('section','Detailed section')],default='fact')
    help_text = models.CharField(max_length=300,blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True,help_text='Uncheck to hide this field on every public course page without deleting its values.')

    class Meta:
        ordering = ['order','pk']
        verbose_name = 'Course field'

    def __str__(self): return self.label

class CourseFieldValue(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='field_values')
    field = models.ForeignKey(CourseField,on_delete=models.SET_NULL,related_name='values',null=True,blank=True,editable=False)
    label = models.CharField(max_length=160)
    key = models.SlugField(blank=True,editable=False)
    presentation = models.CharField(max_length=10,choices=[('fact','Overview row'),('section','Detailed section')],default='fact')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True,help_text='Show this field on this course’s public page.')
    value = models.TextField(help_text='Plain text. Paragraphs and line breaks are preserved.')
    source_url = models.URLField(blank=True,help_text='Optional official page, fee schedule or requirements link.')
    link_label = models.CharField(max_length=160,blank=True)

    class Meta:
        ordering = ['order','pk']
        verbose_name = 'Course field'
        verbose_name_plural = 'Course fields'
        constraints = [models.UniqueConstraint(fields=['course','label'],name='unique_course_field_label')]

    def __str__(self): return f'{self.course.title} — {self.label}'

    def save(self,*args,**kwargs):
        if not self.key: self.key = slugify(self.label)[:50]
        return super().save(*args,**kwargs)

class AdmissionCall(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='admission_calls')
    title = models.CharField(max_length=200,help_text='For example: Non-EU applicants residing outside Italy')
    academic_year = models.CharField(max_length=20,help_text='For example: 2027/2028')
    applicant_category = models.CharField(max_length=240)
    application_start = models.DateField(null=True,blank=True)
    application_deadline = models.DateTimeField(null=True,blank=True,help_text='Enter the date and local time in the time zone below.')
    timezone = models.CharField(max_length=64,default='Europe/Rome',help_text='IANA time zone, e.g. Europe/Rome. Handles CET and summer time automatically.')
    studies_commence = models.DateField(null=True,blank=True)
    instructions = models.TextField(blank=True)
    available_places = models.PositiveIntegerField(null=True,blank=True)
    source_url = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order','application_start','pk']

    def clean(self):
        super().clean()
        try:
            zone = ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError,ValueError):
            raise ValidationError({'timezone':'Enter a valid IANA time zone, such as Europe/Rome.'})
        if self.application_start and self.application_deadline:
            deadline = self.application_deadline
            local_date = deadline.astimezone(zone).date() if deadline.tzinfo else deadline.date()
            if local_date < self.application_start:
                raise ValidationError({'application_deadline':'The deadline cannot be before the application start.'})

    def __str__(self): return f'{self.title} ({self.academic_year})'

class Page(Content):
    kind = models.CharField(max_length=20,choices=[(x,x.title()) for x in ['page','service','test','legal','journey','benefit','advantage']])


class PageSection(models.Model):
    """Editable section content for pages, services, guides and legal pages."""
    page = models.ForeignKey(Page,on_delete=models.CASCADE,related_name='page_sections')
    heading = models.CharField(max_length=240,help_text='Section heading, for example: Our mission.')
    body = models.TextField(help_text='Write the section content normally. Use a blank line between paragraphs.')
    kind = models.CharField(max_length=20,choices=[
        ('guidance','Guidance / advice'),
        ('official','Official information'),
        ('estimate','Estimate / budget'),
    ],default='guidance')
    source_url = models.URLField(blank=True,help_text='Optional official source link for this section.')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order','pk']
        verbose_name = 'Page section'
        verbose_name_plural = 'Page sections'

    def __str__(self): return self.heading

class TestDate(models.Model):
    test = models.ForeignKey(Page,on_delete=models.CASCADE,limit_choices_to={'kind':'test'},related_name='dates')
    label = models.CharField(max_length=200)
    exam_date = models.DateField()
    registration_deadline = models.DateField(null=True,blank=True)
    source_url = models.URLField()
    def __str__(self): return self.label

class Category(models.Model):
    title = models.CharField(max_length=120,unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.title

class Article(Content):
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    author = models.CharField(max_length=120)
    date = models.DateField()
    reading_time = models.PositiveSmallIntegerField(default=5)


class ArticleSection(models.Model):
    """A friendly, repeatable content block for the blog editor.

    Content.sections is kept as the public/API representation for backwards
    compatibility, while these fields make editing possible without JSON.
    """
    KIND_CHOICES = [
        ('guidance', 'Guidance / advice'),
        ('official', 'Official information'),
        ('estimate', 'Estimate / budget'),
    ]
    article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name='article_sections')
    heading = models.CharField(max_length=240,help_text='A clear heading for this part of the article.')
    body = models.TextField(help_text='Write normally. Use a blank line between paragraphs.')
    kind = models.CharField(max_length=20,choices=KIND_CHOICES,default='guidance')
    source_url = models.URLField(blank=True,help_text='Optional link to the official source for this block.')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order','pk']
        verbose_name = 'Blog section'
        verbose_name_plural = 'Blog sections'

    def __str__(self): return self.heading

class FAQ(models.Model):
    category = models.CharField(max_length=100)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    university = models.ForeignKey(University,on_delete=models.CASCADE,null=True,blank=True)
    page = models.ForeignKey(Page,on_delete=models.CASCADE,null=True,blank=True)
    published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering=['order','pk']
    def __str__(self): return self.question

class Testimonial(Content):
    university = models.ForeignKey(University,on_delete=models.SET_NULL,null=True,blank=True)
    course = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    video_url = models.URLField(blank=True)
    consent_confirmed = models.BooleanField(default=False)

class Career(Content):
    location = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=60)
    deadline = models.DateField(null=True,blank=True)
    salary = models.CharField(max_length=160,blank=True,help_text='For example: €1,200–€1,500 per month or Competitive.')
    minimum_experience = models.CharField(max_length=120,blank=True,help_text='For example: 2 years or Entry level.')
    minimum_commitment_years = models.PositiveSmallIntegerField(null=True,blank=True,help_text='Minimum expected commitment in years.')
    job_description = models.TextField(blank=True,help_text='Explain the role, day-to-day work and who the person will work with.')
    requirements = models.TextField(blank=True,help_text='List qualifications, skills and experience. Use one requirement per line.')
    application_instructions = models.TextField(blank=True,help_text='Tell applicants what to submit and how to apply.')
    status = models.CharField(max_length=10,choices=[('open','Open'),('closed','Closed')],default='open',help_text='Open vacancies accept applications. Closed vacancies remain visible but cannot be applied for.')

class Inquiry(models.Model):
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    whatsapp = models.CharField(max_length=40,blank=True)
    qualification = models.CharField(max_length=160,blank=True)
    gpa = models.CharField(max_length=30,blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True,blank=True)
    intended_degree = models.CharField(max_length=50,blank=True)
    preferred_course = models.CharField(max_length=160,blank=True)
    preferred_region = models.ForeignKey(Region,on_delete=models.SET_NULL,null=True,blank=True)
    preferred_university = models.ForeignKey(University,on_delete=models.SET_NULL,null=True,blank=True)
    english_proficiency = models.CharField(max_length=120,blank=True)
    budget = models.CharField(max_length=120,blank=True)
    scholarship_requirement = models.CharField(max_length=100,blank=True)
    message = models.TextField(max_length=10000,blank=True)
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=30,choices=[(x,x.title()) for x in ['new','contacted','in-progress','closed']],default='new')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.full_name} — {self.status}'

class CareerApplication(models.Model):
    career = models.ForeignKey(Career,on_delete=models.PROTECT)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    cover_letter = models.TextField(max_length=10000)
    resume = models.FileField(upload_to='private/resumes/%Y/%m/',validators=[FileExtensionValidator(['pdf'])])
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=30,choices=[(x,x.title()) for x in ['new','reviewing','interview','accepted','declined']],default='new')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.full_name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.email

class Notification(models.Model):
    title = models.CharField(max_length=240)
    admin_path = models.CharField(max_length=300)
    read = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title


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

    def __str__(self): return f'{self.user.get_full_name() or self.user.email} — student profile'


class StudentChecklistRequirement(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    accepted_extensions = models.CharField(max_length=120,default='pdf,jpg,jpeg,png',help_text='Comma-separated file extensions.')
    order = models.PositiveIntegerField(default=0)

    class Meta: ordering=['order','pk']
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

    class Meta: ordering=['-uploaded_at']
    def __str__(self): return f'{self.student} — {self.original_name}'


class StudentApplication(models.Model):
    STATUS_CHOICES=[('draft','Draft'),('submitted','Submitted'),('under_review','Under review'),('more_information','More information needed'),('ready_to_apply','Ready to apply'),('submitted_to_university','Submitted to university'),('accepted','Accepted'),('rejected','Not accepted'),('withdrawn','Withdrawn')]
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE,related_name='applications')
    course = models.ForeignKey(Course,on_delete=models.PROTECT,related_name='student_applications',null=True,blank=True)
    reference_code = models.CharField(max_length=30,unique=True)
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default='draft')
    student_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering=['-updated_at']
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

    class Meta: ordering=['-created_at']


class StudentRecommendation(models.Model):
    request = models.ForeignKey(StudentRecommendationRequest,on_delete=models.CASCADE,related_name='recommendations')
    course = models.ForeignKey(Course,on_delete=models.PROTECT,null=True,blank=True)
    title = models.CharField(max_length=240,blank=True)
    rationale = models.TextField()
    fit_score = models.PositiveSmallIntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title or self.course.title if self.course else 'Student recommendation'
