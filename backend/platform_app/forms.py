from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django import forms
from . import models as m


class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = m.Course
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['department'].required = True
        university = self.data.get(self.add_prefix('university')) if self.is_bound else self.instance.university_id or self.initial.get('university')
        try:
            self.fields['department'].queryset = m.Department.objects.filter(university_id=int(university))
        except (ValueError,TypeError):
            self.fields['department'].queryset = m.Department.objects.none()


class AdmissionCallForm(forms.ModelForm):
    # A local clock value must be interpreted in the call's zone, not the admin user's zone.
    application_deadline = forms.CharField(required=False,widget=forms.TextInput(attrs={'type':'datetime-local','step':'1'}),
        help_text='Local date and time in this call’s time zone; seconds are supported.')

    class Meta:
        model = m.AdmissionCall
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.application_deadline and not self.is_bound:
            self.initial['application_deadline'] = self.instance.application_deadline.astimezone(ZoneInfo(self.instance.timezone)).strftime('%Y-%m-%dT%H:%M:%S')

    def clean_application_deadline(self):
        raw = self.cleaned_data.get('application_deadline')
        if not raw: return None
        try:
            local = datetime.fromisoformat(raw)
            zone = ZoneInfo(self.data.get(self.add_prefix('timezone'),'Europe/Rome'))
        except (ValueError,ZoneInfoNotFoundError):
            raise forms.ValidationError('Enter a valid deadline and IANA time zone.')
        if local.tzinfo:
            raise forms.ValidationError('Enter a local time without an offset; use the time zone field.')
        aware = local.replace(tzinfo=zone)
        if aware.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != local:
            raise forms.ValidationError('This time does not exist because the clocks change. Choose another time.')
        if aware.utcoffset() != aware.replace(fold=1).utcoffset():
            raise forms.ValidationError('This time occurs twice when the clocks change. Use UTC and the exact UTC deadline instead.')
        return aware
