from pyexpat.errors import messages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse 
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import DonorForm, PatientForm
from .models import DonationHistory, Patient, Donor
from datetime import date, timedelta
import os
from django.conf import settings
 
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("Warning: arabic-reshaper or python-bidi not installed.")

def reshape_arabic(text):
    """تحويل النص العربي للعرض الصحيح في PDF"""
    if not text:
        return ""
    if ARABIC_SUPPORT:
        try:
            reshaped_text = arabic_reshaper.reshape(str(text))
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return str(text)
    else:
        return str(text)


def generate_certificate(request, patient_id, donor_id):
    """توليد شهادة تبرع بالدم بتصميم احترافي أبيض وأسود"""
    
    patient = get_object_or_404(Patient, id=patient_id)
    donor = get_object_or_404(Donor, id=donor_id)
    
    response = HttpResponse(content_type='application/pdf')
    filename = f'certificate_{patient_id}_{donor_id}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # تسجيل الخط العربي
    arabic_font = 'Helvetica'
    try:
        possible_font_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf'),
            os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansArabic-Regular.ttf'),
            os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Arial.ttf'),
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
        ]
        
        for font_path in possible_font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                arabic_font = 'ArabicFont'
                break
    except Exception as e:
        print(f"Font error: {e}")
    
    # ==== إضافة الشعار ====
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
    # محاولة مسارات بديلة للشعار
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.jpg')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    
    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            # وضع الشعار في الأعلى في المنتصف
            logo_width = 3*cm
            logo_height = 3*cm
            p.drawImage(logo, width/2 - logo_width/2, height - 5.25*cm, 
                       width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            print(f"Logo error: {e}")
    else:
        print(f"Logo not found at: {logo_path}")
    
    # ==== الإطار الخارجي المزدوج ====
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(3)
    p.rect(1.5*cm, 1.5*cm, width-3*cm, height-3*cm, stroke=1, fill=0)
    
    p.setLineWidth(1)
    p.rect(2*cm, 2*cm, width-4*cm, height-4*cm, stroke=1, fill=0)
    
    # خطوط زخرفية في الزوايا
    corner_size = 1*cm
    # الزاوية العلوية اليمنى
    p.line(width-2*cm, height-2*cm, width-2*cm-corner_size, height-2*cm)
    p.line(width-2*cm, height-2*cm, width-2*cm, height-2*cm-corner_size)
    # الزاوية العلوية اليسرى
    p.line(2*cm, height-2*cm, 2*cm+corner_size, height-2*cm)
    p.line(2*cm, height-2*cm, 2*cm, height-2*cm-corner_size)
    # الزاوية السفلية اليمنى
    p.line(width-2*cm, 2*cm, width-2*cm-corner_size, 2*cm)
    p.line(width-2*cm, 2*cm, width-2*cm, 2*cm+corner_size)
    # الزاوية السفلية اليسرى
    p.line(2*cm, 2*cm, 2*cm+corner_size, 2*cm)
    p.line(2*cm, 2*cm, 2*cm, 2*cm+corner_size)
    
    # ==== العنوان الرئيسي ====
    p.setFont(arabic_font, 26)
    p.setFillColorRGB(0, 0, 0)
    title = reshape_arabic("جمعية الغد الأفضل")
    p.drawCentredString(width/2, height - 6*cm, title)
    
    # خط تزييني تحت العنوان
    p.setLineWidth(2)
    p.line(width/2 - 4*cm, height - 6.5*cm, width/2 + 4*cm, height - 6.5*cm)
    
    # العنوان الفرعي
    p.setFont(arabic_font, 18)
    p.setFillColorRGB(0.2, 0.2, 0.2)
    subtitle = reshape_arabic("استمارة التبرع بالدم")
    p.drawCentredString(width/2, height - 7.5*cm, subtitle)
    
    # ==== صندوق معلومات المتبرع ====
    y_position = height - 9.5*cm
    box_height = 7*cm  # زيادة الارتفاع لإضافة المعلومات الجديدة
    
    # خلفية رمادية فاتحة
    p.setFillColorRGB(0.95, 0.95, 0.95)
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(1)
    p.rect(3*cm, y_position - box_height, width - 6*cm, box_height, stroke=1, fill=1)
    
    # عنوان القسم مع خلفية سوداء
    header_height = 0.8*cm
    p.setFillColorRGB(0, 0, 0)
    p.rect(3*cm, y_position - header_height, width - 6*cm, header_height, stroke=0, fill=1)
    
    p.setFont(arabic_font, 14)
    p.setFillColorRGB(1, 1, 1)  # نص أبيض
    p.drawCentredString(width/2, y_position - 0.55*cm, reshape_arabic("معلومات المتبرع"))
    
    y_position -= 1.5*cm
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    
    # عرض البيانات في جدول منظم
    right_margin = width - 5*cm
    label_x = right_margin
    value_x = right_margin - 3*cm
    
    # الاسم
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("الاسم:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, reshape_arabic(donor.PRENOM or ''))
    
    y_position -= 0.7*cm
    # اللقب
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("اللقب:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, reshape_arabic(donor.NOM or ''))
    
    y_position -= 0.7*cm
    # تاريخ الميلاد
    birth_date = donor.DATE_N.strftime('%d-%m-%Y') if donor.DATE_N else 'غير محدد'
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("تاريخ الميلاد:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    if donor.DATE_N:
        p.drawRightString(value_x, y_position, birth_date)
    else:
        p.drawRightString(value_x, y_position, reshape_arabic('غير محدد'))
    
    y_position -= 0.7*cm
    # الزمرة الدموية
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("الزمرة الدموية:"))
    p.setFont(arabic_font, 13)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, donor.GROUPAGE or '')
    
    y_position -= 0.7*cm
    # تاريخ آخر تبرع
    last_donation = donor.DATE_DERNIER_DON.strftime('%d-%m-%Y') if donor.DATE_DERNIER_DON else 'أول تبرع'
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("تاريخ آخر تبرع:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    if donor.DATE_DERNIER_DON:
        p.drawRightString(value_x, y_position, last_donation)
    else:
        p.drawRightString(value_x, y_position, reshape_arabic('أول تبرع'))
    
    y_position -= 0.7*cm
    # معلومات إضافية
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("معلومات إضافية:"))
    p.setFont(arabic_font, 9)
    p.setFillColorRGB(0, 0, 0)
    
    # معالجة النص الطويل للمعلومات الإضافية
    description = donor.description or 'لا توجد معلومات إضافية'
    if len(description) > 30:
        # تقسيم النص إذا كان طويلاً
        words = description.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= 30:
                current_line += " " + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # عرض الأسطر
        for i, line in enumerate(lines[:2]):  # عرض سطرين كحد أقصى
            p.drawRightString(value_x, y_position - (i * 0.5*cm), reshape_arabic(line))
    else:
        p.drawRightString(value_x, y_position, reshape_arabic(description))
    
    # ==== صندوق معلومات المريض ====
    y_position -= 2.5*cm  # زيادة المسافة بسبب المعلومات الإضافية
    box_height = 5.8*cm
    
    p.setFillColorRGB(0.95, 0.95, 0.95)
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(1)
    p.rect(3*cm, y_position - box_height, width - 6*cm, box_height, stroke=1, fill=1)
    
    # عنوان القسم
    p.setFillColorRGB(0, 0, 0)
    p.rect(3*cm, y_position - header_height, width - 6*cm, header_height, stroke=0, fill=1)
    
    p.setFont(arabic_font, 14)
    p.setFillColorRGB(1, 1, 1)
    p.drawCentredString(width/2, y_position - 0.55*cm, reshape_arabic("معلومات المريض"))
    
    y_position -= 1.5*cm
    
    # الاسم
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("الاسم:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, reshape_arabic(patient.First_name or ''))
    
    y_position -= 0.7*cm
    # اللقب
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("اللقب:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, reshape_arabic(patient.Family_name or ''))
    
    y_position -= 0.7*cm
    # تاريخ الميلاد
    patient_birth = patient.date_of_birth.strftime('%d-%m-%Y') if patient.date_of_birth else 'غير محدد'
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("تاريخ الميلاد:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    if patient.date_of_birth:
        p.drawRightString(value_x , y_position, patient_birth)
    else:
        p.drawRightString(value_x, y_position, reshape_arabic('غير محدد'))
    
    y_position -= 0.7*cm
    # الزمرة الدموية
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("الزمرة الدموية:"))
    p.setFont(arabic_font, 13)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, patient.blood_type or '')
    
    y_position -= 0.7*cm
    # المستشفى
    p.setFont(arabic_font, 10)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawRightString(label_x, y_position, reshape_arabic("المستشفى:"))
    p.setFont(arabic_font, 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawRightString(value_x, y_position, reshape_arabic(patient.hospital_name or 'غير محدد'))
    
    # ==== خط فاصل زخرفي ====
    y_position -= 1.5*cm
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(1.5)
    p.line(4*cm, y_position, width - 4*cm, y_position)
    # ==== التوقيع ====
    y_position = 5.5*cm
    
    # إزالة المربع وإضافة التوقيع على اليسار
    p.setFont(arabic_font, 12)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(4.5*cm, y_position, reshape_arabic("رئيس الجمعية"))
    
    # خط التوقيع
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(0.8)
    p.line(4*cm, y_position - 0.3*cm, 7*cm, y_position - 0.3*cm)
    
    # ==== التذييل ====
    p.setFont(arabic_font, 8)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    footer = reshape_arabic("جمعية الغد الأفضل - نساهم في إنقاذ الأرواح")
    p.drawCentredString(width/2, 2.5*cm, footer)
    
    # خط في الأسفل
    p.setStrokeColorRGB(0, 0, 0)
    p.setLineWidth(0.5)
    p.line(3*cm, 3*cm, width - 3*cm, 3*cm)
    
    p.showPage()
    p.save()
    
    return response
#dashboard views    

def admin_dashboard(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    return render(request, 'admin_dashboard.html')


#blood

def blood_dashboard(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    pending_donors = Donor.objects.filter(is_approved=False)
    approved_donors = Donor.objects.filter(is_approved=True)
    return render(request, 'blood_dashboard.html', {
        'pending_donors': pending_donors,
        'approved_donors': approved_donors
    })
  
    
def modify_donor(request, donor_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    donor = get_object_or_404(Donor, id=donor_id)
    
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('blood_dashboard')
    else:
        form = DonorForm(instance=donor)
    
    return render(request, 'donor_modification.html', {'form': form, 'donor': donor})


def patient_dashboard(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    patients = Patient.objects.filter(is_active=True)
    data = []
    three_months_ago = date.today() - timedelta(days=90)
    
    for p in patients:
        compatible_donors = Donor.objects.filter(
            GROUPAGE=p.blood_type,
            is_approved=True,
            DATE_DERNIER_DON__lte=three_months_ago
        )
        data.append({"patient": p, "donors": compatible_donors})
    
    return render(request, 'patient_dashboard.html', {"data": data})


def modify_patient(request, patient_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
                form.save()
                # CORRECT: Use messages.success() function
                return redirect('patient_dashboard')
                # CORRECT: Use messages.error() function
        else:
            # CORRECT: Use messages.error() function
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patient_modification.html', {
        'form': form, 
        'patient': patient
    })   


def home(request):
    return render(request, 'home.html')


def donor_form(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donor_success') 
    else:
        form = DonorForm()
    return render(request, 'donor_form.html', {'form': form})


def donor_success(request):
    return render(request, 'donor_success.html')


def Patient_form(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'patient_success.html')
    else:
        form = PatientForm()
    return render(request, 'patient_form_simple.html', {'form': form})


# ADMIN AUTHENTICATION
def login_view(request):
    if request.session.get('is_admin_logged_in'):
        return redirect('blood_dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "mohammed" and password == "mohammed":
            request.session['is_admin_logged_in'] = True
            return redirect('admin_dashboard')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# DONOR ACTIONS
def approve_donor(request, donor_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    donor = get_object_or_404(Donor, id=donor_id)
    donor.is_approved = True
    donor.save()
    return redirect('blood_dashboard')


def reject_donor(request, donor_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    donor = get_object_or_404(Donor, id=donor_id)
    donor.delete()
    return redirect('blood_dashboard')

def reject_patient(request, patient_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    patient = get_object_or_404(Patient, id=patient_id)
    patient.delete()
    return redirect('patient_dashboard')


def delete_donor(request, donor_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    donor = get_object_or_404(Donor, id=donor_id)
    donor.delete()
    return redirect('blood_dashboard')


# BLOOD DONATION TRACKING

def donate_blood(request,donor_id,patient_id):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    donor = get_object_or_404(Donor, id=donor_id)
    patient = get_object_or_404(Patient, id=patient_id)
    donor.DATE_DERNIER_DON = date.today()
    donationHistory = DonationHistory(
        patient=patient,
        donor=donor,
        donation_date = date.today(),
    )
    donationHistory.save()
    donor.save()
    patient.save()
    return redirect('patient_dashboard');

def donation_history(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('login')
    
    donations = DonationHistory.objects.all().order_by('-donation_date')
    
    # Calculate unique donors count
    unique_donors = DonationHistory.objects.values('donor').distinct().count()
    
    context = {
        'donations': donations,
        'unique_donors': unique_donors,
    }
    return render(request, 'donation_history.html', context)