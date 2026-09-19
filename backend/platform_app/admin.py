from django.contrib import admin
from . import models as m
from .forms import CourseAdminForm, AdmissionCallForm
from django.http import JsonResponse
from django.urls import path
admin.site.site_header = 'Kashyap Advisors · Content Studio'
admin.site.site_title = 'Kashyap Admin'
admin.site.index_title = 'Manage your Italy education platform'
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title','published','updated_at')
    list_filter = ('published',)
    search_fields = ('title','summary')
    prepopulated_fields = {'slug':('title',)}
class CourseInline(admin.TabularInline):
    model=m.Course
    extra=0
    fields=('title','slug','department','degree','discipline','english_taught','published')
    show_change_link=True
    def get_formset(self,request,obj=None,**kwargs):
        formset = super().get_formset(request,obj,**kwargs)
        formset.form.base_fields['department'].required = True
        formset.form.base_fields['department'].queryset = m.Department.objects.filter(university=obj) if obj else m.Department.objects.none()
        return formset
class DepartmentInline(admin.TabularInline):
    model=m.Department
    extra=0
    fields=('title','address','published','order')
    show_change_link=True
@admin.register(m.University)
class UniversityAdmin(ContentAdmin):
    list_filter=('published','country','region','institution_type','featured')
    fieldsets=(
        ('University identity',{'fields':('title','slug','country','region','city','institution_type','website')}),
        ('Study profile',{'fields':('summary','disciplines','degrees','english_taught','featured')}),
        ('Brand & location',{'fields':('logo','logo_url','latitude','longitude')}),
        ('Publishing & sources',{'fields':('published','order','source_url','reviewed_at','image','image_url')}),
    )
    inlines=[DepartmentInline,CourseInline]

@admin.register(m.Country)
class CountryAdmin(admin.ModelAdmin):
    list_display=('name','code','published')
    list_filter=('published',)
    search_fields=('name','code')
    prepopulated_fields={'slug':('name',)}

@admin.register(m.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display=('title','university','published')
    list_filter=('university','published')
    search_fields=('title','university__title','address')
    def get_readonly_fields(self,request,obj=None):
        return ('university',) if obj and obj.courses.exists() else ()

class AdmissionCallInline(admin.StackedInline):
    model=m.AdmissionCall
    form=AdmissionCallForm
    extra=0

class CourseFieldValueInline(admin.StackedInline):
    model=m.CourseFieldValue
    extra=0
    fields=('label','value','presentation','order','active','source_url','link_label')

@admin.register(m.Course)
class CourseAdmin(ContentAdmin):
    form=CourseAdminForm
    list_display=('title','university','department','degree','published')
    list_filter=('published','university','department','degree')
    search_fields=('title','summary','university__title','department__title')
    inlines=[CourseFieldValueInline,AdmissionCallInline]
    fieldsets=(
        ('Course identity',{'fields':('title','slug','university','department','summary','degree','discipline','degree_class_code')}),
        ('Programme details',{'fields':('study_location','course_type','nominal_duration','study_language','studies_commence')}),
        ('Fees',{'fields':('application_fee','pre_enrollment_fee','tuition_fee','tuition')}),
        ('Requirements',{'fields':('cent_requirements','language_requirements','other_requirements','entry_qualification')}),
        ('Links & extra information',{'fields':('more_information','course_link','additional_info')}),
        ('Publishing & sources',{'fields':('published','order','source_url','reviewed_at','image','image_url')}),
    )
    class Media:
        js=('platform_app/course-admin.js',)

    def get_urls(self):
        return [path('departments/<int:university_id>/',self.admin_site.admin_view(self.departments))]+super().get_urls()

    def departments(self,request,university_id):
        if not (self.has_add_permission(request) or self.has_change_permission(request)):
            return JsonResponse({'detail':'Permission denied'},status=403)
        return JsonResponse({'departments':list(m.Department.objects.filter(university_id=university_id).values('id','title'))})

class CourseFieldAdmin(admin.ModelAdmin):
    list_display=('label','course','presentation','order','active')
    list_filter=('course','active','presentation')
    search_fields=('label','value','course__title','course__university__title')
    autocomplete_fields=('course',)
    fields=('course','label','value','presentation','order','active','source_url','link_label')

    def has_module_permission(self,request): return False

admin.site.register(m.CourseFieldValue,CourseFieldAdmin)

class PageSectionInline(admin.StackedInline):
    model=m.PageSection
    extra=1
    fields=('heading','body','kind','source_url','order')
    ordering=('order','pk')
    verbose_name='Page section'
    verbose_name_plural='Page sections — add as many as you need'

@admin.register(m.Page)
class PageAdmin(ContentAdmin):
    list_display=('title','kind','published','updated_at')
    list_filter=('kind','published')
    search_fields=('title','summary','page_sections__heading','page_sections__body')
    inlines=[PageSectionInline]
    fieldsets=(
        ('Page details',{'fields':('title','slug','kind','summary')}),
        ('Publishing & sources',{'fields':('published','order','source_url','reviewed_at','image','image_url')}),
    )

    def save_related(self,request,form,formsets,change):
        super().save_related(request,form,formsets,change)
        page=form.instance
        page.sections=[{
            'heading':section.heading,
            'body':section.body,
            'kind':section.kind,
            'source_url':section.source_url,
        } for section in page.page_sections.all()]
        page.save(update_fields=['sections','updated_at'])
class ArticleSectionInline(admin.StackedInline):
    model=m.ArticleSection
    extra=1
    fields=('heading','body','kind','source_url','order')
    ordering=('order','pk')
    verbose_name='Content block'
    verbose_name_plural='Article content blocks — add as many as you need'

@admin.register(m.Article)
class ArticleAdmin(ContentAdmin):
    list_display=('title','category','author','date','published','updated_at')
    list_filter=('published','category','date')
    search_fields=('title','summary','author','article_sections__body')
    inlines=[ArticleSectionInline]
    fieldsets=(
        ('Start your article',{'fields':('title','slug','category','author','date','reading_time','summary')}),
        ('Cover image',{'fields':('image','image_url')}),
        ('Publishing',{'fields':('published','order','source_url','reviewed_at'),'description':'Save as a draft while you are writing. Turn on Published when it is ready.'}),
    )

    def save_related(self,request,form,formsets,change):
        super().save_related(request,form,formsets,change)
        article=form.instance
        article.sections=[{
            'heading':section.heading,
            'body':section.body,
            'kind':section.kind,
            'source_url':section.source_url,
        } for section in article.article_sections.all()]
        article.save(update_fields=['sections','updated_at'])

@admin.register(m.Career)
class CareerAdmin(ContentAdmin):
    list_display=('title','status','location','employment_type','deadline','published','updated_at')
    list_filter=('status','published','employment_type','location')
    search_fields=('title','summary','location','employment_type','job_description','requirements')
    fieldsets=(
        ('Role details',{'fields':('title','slug','location','employment_type','salary','minimum_experience','minimum_commitment_years','deadline','status','summary')}),
        ('The vacancy',{'fields':('job_description','requirements','application_instructions'),'description':'Use one requirement per line. Applicants will see these sections on the vacancy page.'}),
        ('Publishing',{'fields':('published','order','source_url','reviewed_at'),'description':'Save as a draft while preparing the vacancy. Turn on Published when applications should be visible.'}),
    )

    def save_model(self,request,obj,form,change):
        obj.sections=[
            {'heading':'Job description','body':obj.job_description,'kind':'guidance','source_url':''},
            {'heading':'Requirements','body':obj.requirements,'kind':'guidance','source_url':''},
            {'heading':'How to apply','body':obj.application_instructions,'kind':'guidance','source_url':''},
        ]
        obj.sections=[section for section in obj.sections if section['body'].strip()]
        super().save_model(request,obj,form,change)

for model in [m.Region,m.Scholarship]: admin.site.register(model,ContentAdmin)

@admin.register(m.Testimonial)
class TestimonialAdmin(ContentAdmin):
    list_display=('title','university','course','city','consent_confirmed','published','updated_at')
    list_filter=('published','consent_confirmed','university','city')
    search_fields=('title','summary','course','city','university__title')
    fieldsets=(
        ('Student story',{'fields':('title','slug','summary','university','course','city')}),
        ('Video',{'fields':('video_url','image','image_url'),'description':'Add the video link and an optional thumbnail image.'}),
        ('Consent & publishing',{'fields':('consent_confirmed','published','order','source_url','reviewed_at'),'description':'Only publish a testimonial after consent has been confirmed.'}),
    )
@admin.register(m.Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display=('full_name','email','intended_degree','status','created_at')
    list_filter=('status','created_at','intended_degree')
    search_fields=('full_name','email','phone')
    readonly_fields=('created_at',)
@admin.register(m.CareerApplication)
class ApplicationAdmin(admin.ModelAdmin):
    list_display=('full_name','career','status','created_at')
    list_filter=('status','career')
    search_fields=('full_name','email')
@admin.register(m.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display=('title','read','emailed','created_at')
    list_filter=('read','emailed')
    list_editable=('read',)
    readonly_fields=('title','admin_path','emailed','created_at')
@admin.register(m.SiteSettings)
class SettingsAdmin(admin.ModelAdmin):
    class SocialLinkInline(admin.StackedInline):
        model=m.SocialLink
        extra=1
        fields=('label','url','order','active')
        ordering=('order','pk')
        verbose_name='Social profile'
        verbose_name_plural='Social profiles — add as many as you need'

    inlines=[SocialLinkInline]
    fieldsets=(
        ('Contact details',{'fields':('title','logo','address','phone','support_phone','whatsapp','email','office_hours','announcement')}),
        ('Homepage',{'fields':('hero_title','hero_description','hero_image')}),
        ('Footer',{'fields':('footer_text',),'description':'Social links are managed below as separate items.'}),
    )

    def save_related(self,request,form,formsets,change):
        super().save_related(request,form,formsets,change)
        settings=form.instance
        settings.social_links=[{'label':link.label,'url':link.url} for link in settings.social_link_items.filter(active=True)]
        settings.save(update_fields=['social_links'])

    def has_add_permission(self,request): return not m.SiteSettings.objects.exists()
    def has_delete_permission(self,request,obj=None): return False

@admin.register(m.OfficialUpdate)
class OfficialUpdateAdmin(admin.ModelAdmin):
    list_display=('title','kind','published_at','expires_at','published','pinned')
    list_filter=('kind','published','pinned','published_at')
    search_fields=('title','summary','body','source_label')
    prepopulated_fields={'slug':('title',)}
    fieldsets=(
        ('What students see',{'fields':('title','slug','kind','summary','body')}),
        ('Official source',{'fields':('source_label','source_url','published_at','expires_at')}),
        ('Visibility',{'fields':('published','pinned'),'description':'Pin only the most important current notice. Expired notices disappear from the live alert automatically.'}),
    )
for model in [m.FAQ,m.Category,m.TestDate,m.Subscriber]: admin.site.register(model)
