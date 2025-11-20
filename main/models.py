from django.db import models
from datetime import date, timedelta

class Donor(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    
    # Remove explicit ID field so Django adds id as AutoField automatically
    NOM = models.CharField(max_length=255, blank=True, null=True)
    PRENOM = models.CharField(max_length=255, blank=True, null=True)
    NUM_TEL = models.CharField(max_length=14,blank=True, null=True)
    DATE_N = models.DateTimeField(blank=True, null=True)
    RESIDENC = models.CharField(max_length=255, blank=True, null=True)
    SEX = models.CharField(max_length=255, blank=True, null=True, choices=GENDER_CHOICES)
    GROUPAGE = models.CharField(max_length=255, blank=True, null=True, choices=BLOOD_TYPES)
    DATE_DERNIER_DON = models.DateField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'main_donor'

    def __str__(self):
        return f"{self.PRENOM} {self.NOM}"

    def can_donate(self):
        if not self.DATE_DERNIER_DON:
            return True
        three_months_ago = date.today() - timedelta(days=90)
        return self.DATE_DERNIER_DON <= three_months_ago

class Patient(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    
    First_name = models.CharField(max_length=100)
    Family_name = models.CharField(max_length=100)
    phone =  models.CharField(max_length=14,blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    adress = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.First_name} {self.Family_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class DonationHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="المريض")
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, verbose_name="المتبرع")
    donation_date = models.DateField(auto_now_add=True, verbose_name="تاريخ التبرع")
    class Meta:
        db_table = 'donation_history'    
    def __str__(self):
        return f"{self.donor.PRENOM} تبرع لـ {self.patient.First_name} في {self.donation_date}"