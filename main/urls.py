from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donor/', views.donor_form, name='donor_form'),
    path('looking_for_donor',views.Patient_form,name='patient_form'),
    path('donor_success/', views.donor_success, name='donor_success'),
    path('donation_history/', views.donation_history, name='donation_history'),
   
    # urls.py - Add this URL
    # Admin + Dashboard
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #dashboard urls
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/blood', views.blood_dashboard, name='blood_dashboard'),
    path('dashboard/modifier,<int:donor_id>/', views.modify_donor, name='modifier_donor'),
    path('dashboard/patients', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/modifier/patient/<int:patient_id>/', views.modify_patient, name='modifier_patient'),
    path('delete_patient/<int:patient_id>/', views.reject_patient, name='delete_patient'),
    #path('dashboard/blood', views.admin_dashboard, name='admin_dashboard'),
    path('approve_donor/<int:donor_id>/', views.approve_donor, name='approve_donor'),
    path('reject_donor/<int:donor_id>/', views.reject_donor, name='reject_donor'),
    path('generate-certificate/<int:patient_id>/<int:donor_id>/', 
         views.generate_certificate, 
         name='generate_certificate'),
    path('donate/<int:patient_id>/<int:donor_id>/',views.donate_blood, name='donate_blood'),
]
