from django import forms
from .models import Donor, Patient

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'NOM',
            'PRENOM', 
            'NUM_TEL',
            'DATE_N',
            'RESIDENC',
            'SEX',
            'GROUPAGE',
            'DATE_DERNIER_DON',
            'description'
        ]
        widgets = {
            'DATE_N': forms.DateTimeInput(attrs={'type': 'date'}),
            'DATE_DERNIER_DON': forms.DateInput(attrs={'type': 'date'}),
            'RESIDENC': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'أي معلومات إضافية قد تساعدنا في خدمتك بشكل أفضل'
            }),
        }
        labels = {
            'NOM': 'الاسم العائلي',
            'PRENOM': 'الاسم الشخصي',
            'NUM_TEL': 'رقم الهاتف',
            'DATE_N': 'تاريخ الميلاد',
            'RESIDENC': 'العنوان',
            'SEX': 'الجنس',
            'GROUPAGE': 'فئة الدم',
            'DATE_DERNIER_DON': 'تاريخ آخر تبرع',
            'description': 'ملاحظات إضافية',
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'First_name',
            'Family_name', 
            'phone',
            'date_of_birth',
            'blood_type',
            'hospital_name',
            'adress',
            'gender',
            'description'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'أي معلومات إضافية قد تساعدنا في خدمتك بشكل أفضل'
            }),
        }
        labels = {
            'First_name': 'الاسم الأول',
            'Family_name': 'الاسم العائلي',
            'phone': 'رقم الهاتف',
            'date_of_birth': 'تاريخ الميلاد',
            'blood_type': 'فصيلة الدم المطلوبة',
            'hospital_name': 'المستشفى أو المركز الطبي',
            'adress': 'العنوان',
            'gender': 'الجنس',
            'description': 'ملاحظات إضافية',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['First_name'].required = True
        self.fields['Family_name'].required = True
        self.fields['blood_type'].required = True
        self.fields['gender'].required = True