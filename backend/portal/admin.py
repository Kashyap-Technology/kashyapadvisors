from django.contrib import admin

from . import models as m


class StudentChecklistInline(admin.TabularInline):
    model=m.StudentChecklistItem
    extra=0
    fields=('requirement','status','admin_note','visible_to_student')
    autocomplete_fields=('requirement',)


class StudentDocumentInline(admin.TabularInline):
    model=m.StudentDocument
    extra=0
    fields=('document_type','original_name','file','file_size','status','admin_note','uploaded_at')
    readonly_fields=('original_name','file_size','uploaded_at')


@admin.register(m.StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display=('student_name','email','phone','profile_status','updated_at')
    list_filter=('profile_status','nationality','province')
    search_fields=('user__email','user__first_name','user__last_name','phone','passport_number','citizenship_number')
    readonly_fields=('user','submitted_at','reviewed_at','created_at','updated_at')
    inlines=[StudentChecklistInline,StudentDocumentInline]
    fieldsets=(
        ('Account',{'fields':('user','phone','profile_status','submitted_at','reviewed_at','admin_note')}),
        ('Identification',{'fields':('date_of_birth','gender','nationality','passport_number','passport_expiry','citizenship_number')}),
        ('Address & emergency contact',{'fields':('address','municipality','district','province','emergency_contact_name','emergency_contact_phone')}),
        ('Academic profile',{'fields':('highest_qualification','previous_degree','previous_institution','field_of_study','grading_system','overall_percentage','overall_gpa','graduation_year','academic_history')}),
        ('Language & goals',{'fields':('english_test','english_score','english_test_date','other_language','other_language_score','target_degree','target_disciplines','preferred_cities')}),
        ('Timestamps',{'fields':('created_at','updated_at')}),
    )
    def student_name(self,obj): return obj.user.get_full_name() or obj.user.email
    def email(self,obj): return obj.user.email


@admin.register(m.StudentChecklistRequirement)
class StudentChecklistRequirementAdmin(admin.ModelAdmin):
    list_display=('title','key','required','active','order')
    list_filter=('required','active')
    search_fields=('title','key','description')
    prepopulated_fields={'key':('title',)}


@admin.register(m.StudentChecklistItem)
class StudentChecklistItemAdmin(admin.ModelAdmin):
    list_display=('student','requirement','status','visible_to_student','updated_at')
    list_filter=('status','visible_to_student','requirement')
    search_fields=('student__user__email','student__user__first_name','student__user__last_name','requirement__title')
    autocomplete_fields=('student','requirement')


class StudentApplicationStageInline(admin.TabularInline):
    model=m.StudentApplicationStage
    extra=0
    fields=('key','title','description','status','visible_to_student','order')


@admin.register(m.StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display=('reference_code','student','course','status','updated_at')
    list_filter=('status','course__university')
    search_fields=('reference_code','student__user__email','student__user__first_name','student__user__last_name','course__title')
    readonly_fields=('reference_code','created_at','updated_at')
    autocomplete_fields=('student','course')
    inlines=[StudentApplicationStageInline]


@admin.register(m.StudentApplicationStage)
class StudentApplicationStageAdmin(admin.ModelAdmin):
    list_display=('application','title','status','visible_to_student','updated_at')
    list_filter=('status','visible_to_student')
    search_fields=('application__reference_code','application__student__user__email','title')
    autocomplete_fields=('application',)


class StudentRecommendationInline(admin.TabularInline):
    model=m.StudentRecommendation
    extra=0
    fields=('course','title','rationale','fit_score')


@admin.register(m.StudentRecommendationRequest)
class StudentRecommendationRequestAdmin(admin.ModelAdmin):
    list_display=('student','kind','status','created_at','updated_at')
    list_filter=('kind','status')
    search_fields=('student__user__email','student__user__first_name','student__user__last_name','student_question')
    readonly_fields=('student','created_at','updated_at')
    autocomplete_fields=('student',)
    inlines=[StudentRecommendationInline]


@admin.register(m.StudentRecommendation)
class StudentRecommendationAdmin(admin.ModelAdmin):
    list_display=('title','request','course','fit_score','created_at')
    search_fields=('title','rationale','request__student__user__email')
    autocomplete_fields=('request','course')
