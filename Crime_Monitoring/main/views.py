from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.contrib.auth.models import User
from .models import Profile, PoliceProfile, CrimeReport,  ContactUsComplaint
from .forms import SignupForm, AddPoliceForm, ContactUsComplaintForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404


# Create your views here.
def is_police(user):
    return user.groups.filter(name='Police').exists()

def home(request):
    return render(request, 'index.html')

def contact_us(request):
    return render(request, 'contect_us.html')

def safety_tips(request):
    return render(request, 'safety_tips.html')

def about_us(request):
    return render(request, 'about_us.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            user_type = form.cleaned_data['user_type']

            # Ensure only public users can sign up
            if user_type != 'public':
                messages.error(request, 'Only Public signup is allowed.')
                return render(request, 'signup.html', {'form': form})

            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'signup.html', {'form': form})

            # Create User and Profile
            user = User.objects.create_user(username=username, email=email, password=password1)
            Profile.objects.create(user=user, user_type=user_type)

            messages.success(request, 'Signup successful. Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Form invalid. Please try again.')
    else:
        # Pass user_type as hidden field with 'public' value
        form = SignupForm(initial={'user_type': 'public'})
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        selected_user_type = request.POST.get('user_type')  # public / police / admin

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser and selected_user_type == 'admin':
                login(request, user)
                return redirect('admin_dashboard')

            # ✅ Public login (normal profile से)
            if selected_user_type == 'public' and hasattr(user, 'profile'):
                if user.profile.user_type == 'public':
                    login(request, user)
                    return redirect('public_dashboard')
                else:
                    messages.error(request, "User type mismatch for public.")
                    return redirect('login')

            # ✅ Police login (अब PoliceProfile से check करेंगे)
            elif selected_user_type == 'police':
                try:
                    police_profile = PoliceProfile.objects.get(user=user)
                    login(request, user)
                    return redirect('police_dashboard')
                except PoliceProfile.DoesNotExist:
                    messages.error(request, "No police profile found. Contact admin.")
                    return redirect('login')

            else:
                messages.error(request, "User type mismatch or profile missing.")
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def public_dashboard(request):
    # लॉगिन किए हुए यूज़र का पुलिस प्रोफाइल प्राप्त करना
    user_profile = request.user.profile
    police_profile = PoliceProfile.objects.get(user=request.user) if user_profile.user_type == 'police' else None

    # यूज़र के लिए रिपोर्ट्स की संख्या निकालना (Pending, In Progress, Solved, Waiting)
    pending_reports = CrimeReport.objects.filter(reporter=request.user, status='pending').count()
    in_progress_reports = CrimeReport.objects.filter(reporter=request.user, status='in_progress').count()
    solved_reports = CrimeReport.objects.filter(reporter=request.user, status='solved').count()
    waiting_reports = CrimeReport.objects.filter(reporter=request.user, status='waiting').count()

    # पुलिस के लिए रिपोर्ट्स की स्थिति के आधार पर आंकड़े
    if police_profile:
        reports_at_station = CrimeReport.objects.filter(pincode=police_profile.pincode).count()
    else:
        reports_at_station = 0

    context = {
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'solved_reports': solved_reports,
        'waiting_reports': waiting_reports,
        'reports_at_station': reports_at_station,
        'police_station': police_profile.station if police_profile else None,
    }

    return render(request, 'public_dashboard.html', context)

@login_required
def submit_crime_report(request):
    if request.method == 'POST':
        CrimeReport.objects.create(
            reporter=request.user,
            name=request.POST['name'],
            contact_no=request.POST['contact_no'],
            email=request.POST['email'],
            description=request.POST['description'],
            crime_location=request.POST['crime_location'],
            crime_date=request.POST['crime_date'],
            crime_time=request.POST['crime_time'],
            district=request.POST['district'],
            state=request.POST['state'],
            city=request.POST['city'],
            village=request.POST.get('village'),
            pincode=request.POST['pincode'],
            evidence_file=request.FILES.get('evidence_file')
        )
        messages.success(request, "Your crime report has been submitted successfully!")
        return redirect('submit_crime')

    return render(request, 'public/submit_crime.html')

@login_required
def my_reports_view(request):
    user = request.user
    reports = CrimeReport.objects.filter(reporter=user)

    pincode = request.GET.get('pincode')
    if pincode:
        reports = reports.filter(pincode=pincode)

    # हर report के साथ उसकी police info जोड़ दो (as custom attributes)
    for report in reports:
        try:
            police = PoliceProfile.objects.get(pincode=report.pincode)
            report.police_station = police.station
            report.officer_name = police.name
            report.officer_username = police.user.username
        except PoliceProfile.DoesNotExist:
            report.police_station = 'N/A'
            report.officer_name = 'N/A'
            report.officer_username = 'N/A'

    return render(request, 'public/my_reports.html', {
        'reports': reports,
        'pincode': pincode,
    })


@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactUsComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user  # Assigning the logged-in user to the complaint
            complaint.save()
            # Redirect or message
            return redirect('complaint_success')
    else:
        form = ContactUsComplaintForm()

    return render(request, 'public/contect_us.html', {'form': form})

def complaint_success(request):
    return render(request, 'public/complaint_success.html')

@login_required
def view_complaints(request):
    complaints = ContactUsComplaint.objects.all()  # या कोई फिल्टर
    return render(request, 'public/view_complaints.html', {'complaints': complaints})

@login_required
def delete_complaint(request, complaint_id):
    try:
        complaint = ContactUsComplaint.objects.get(id=complaint_id)
    except ContactUsComplaint.DoesNotExist:
        raise Http404("Complaint not found")

    # Delete the complaint
    complaint.delete()
    return redirect('view_complaints') 

@login_required
def public_change_credentials(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        user = request.user
        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)
        user.save()

        messages.success(request, 'Username / Password changed successfully. Please log in again.')
        logout(request)
        return redirect('login')

    return render(request, 'public/change_credentials.html')


@login_required
def police_dashboard(request):
    try:
        police_profile = request.user.policeprofile
        pincode = police_profile.pincode  # ✅ अगर बाकी views में भी pincode से filter है
    except PoliceProfile.DoesNotExist:
        return render(request, 'unauthorized.html')

    # Filter by pincode just like other views
    reports = CrimeReport.objects.filter(pincode=pincode)

    # ✅ Count using lowercase status values
    waiting_count = reports.filter(status='waiting').count()
    pending_count = reports.filter(status='pending').count()
    in_progress_count = reports.filter(status='in_progress').count()
    solved_count = reports.filter(status='solved').count()

    context = {
        'waiting_count': waiting_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'solved_count': solved_count,
    }
    return render(request, 'police_dashboard.html', context)

@login_required
def update_status(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id)

    if request.method == 'POST':
        new_status = request.POST['status']
        report.status = new_status
        if new_status in ['pending', 'in_progress']:
            report.investigation_notes = request.POST.get('investigation_notes', '')
        report.save()
        messages.success(request, f"Status updated to {new_status}.")
        return redirect('police_all_reports')

    return render(request, 'police/update_status.html', {'report': report})

@login_required
def police_all_reports(request):
    try:
        police_profile = request.user.policeprofile  # ✅ Get police profile
        pincode = police_profile.pincode             # ✅ Get pincode from PoliceProfile
    except PoliceProfile.DoesNotExist:
        return render(request, 'unauthorized.html')  # ❌ If not a police user, deny access

    reports = CrimeReport.objects.filter(pincode=pincode, status='waiting')
    return render(request, 'police/all_reports.html', {'reports': reports})

@login_required
def pending_reports(request):
    try:
        police_profile = request.user.policeprofile
    except PoliceProfile.DoesNotExist:
        return render(request, 'unauthorized.html')  # Police user ही देख सकता है

    reports = CrimeReport.objects.filter(status='pending', pincode=police_profile.pincode)
    return render(request, 'police/pending_reports.html', {'reports': reports})

@login_required
def in_progress_reports(request):
    try:
        police_profile = request.user.policeprofile
    except PoliceProfile.DoesNotExist:
        return render(request, 'unauthorized.html')

    reports = CrimeReport.objects.filter(status='in_progress', pincode=police_profile.pincode)
    return render(request, 'police/in_progress_reports.html', {'reports': reports})

@login_required
def solved_reports(request):
    try:
        police_profile = request.user.policeprofile
    except PoliceProfile.DoesNotExist:
        return render(request, 'unauthorized.html')

    reports = CrimeReport.objects.filter(status='solved', pincode=police_profile.pincode)
    return render(request, 'police/solved_reports.html', {'reports': reports})

@login_required
def delete_report(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id)
    report.delete()
    messages.success(request, "Report deleted successfully.")
    return redirect('solved_reports') 

@login_required
def police_change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            logout(request)
            messages.success(request, "Password changed successfully. Please log in again.")
            return redirect('login')
    return render(request, 'police/change_password.html')


def is_admin(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.user_type not in ['public', 'police'])

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Total users
    total_users = User.objects.count()

    # Total police and public
    total_police = PoliceProfile.objects.count() 
    total_public = Profile.objects.filter(user_type='public').count()

    # Crime report status wise counts
    waiting_cases = CrimeReport.objects.filter(status='waiting').count()
    pending_cases = CrimeReport.objects.filter(status='pending').count()
    progress_cases = CrimeReport.objects.filter(status='in_progress').count()
    solved_cases = CrimeReport.objects.filter(status='solved').count()
    total_complaints = ContactUsComplaint.objects.count()

    context = {
        'total_users': total_users,
        'total_police': total_police,
        'total_public': total_public,
        'waiting_cases': waiting_cases,
        'pending_cases': pending_cases,
        'progress_cases': progress_cases,
        'solved_cases': solved_cases,
        'total_complaints': total_complaints,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_police_view(request):
    if request.method == 'POST':
        form = AddPoliceForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            state = form.cleaned_data['state']
            district = form.cleaned_data['district']
            city = form.cleaned_data['city']
            station = form.cleaned_data['station']
            pincode = form.cleaned_data['pincode']

            user = User.objects.create_user(username=username, email=email, password=password)
            PoliceProfile.objects.create(
                user=user,
                name=name,
                state=state,
                district=district,
                city=city,
                station=station,
                pincode=pincode
            )

            # Send mail to police
            subject = "Police Account Created"
            message = f"""Dear {name},

Your police account has been created.

Login Credentials:
Username: {username}
Password: {password}

Station: {station}, {city}, {district}, {state} - {pincode}

Please login and update your password.

- Crime Monitoring Admin
"""
            send_mail(subject, message, 'admin@crimeportal.com', [email])

            messages.success(request, "Police profile created and email sent.")
            return redirect('add_police')
    else:
        form = AddPoliceForm()
    return render(request, 'admin/add_police.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def view_officers(request):
    officers = PoliceProfile.objects.all()
    data = []

    for officer in officers:
        officer_user = officer.user
        reports = CrimeReport.objects.filter(pincode=officer.pincode)

        data.append({
            'profile': officer,
            'user': officer_user,
            'email': officer_user.email,
            'contact_no': officer_user.profile.contact_no if hasattr(officer_user, 'profile') else 'N/A',
            'waiting': reports.filter(status='waiting').count(),
            'pending': reports.filter(status='pending').count(),
            'in_progress': reports.filter(status='in_progress').count(),
            'solved': reports.filter(status='solved').count(),
        })

    return render(request, 'admin/view_officers.html', {'data': data})

@login_required
@user_passes_test(is_admin)
def delete_officer(request, officer_id):
    try:
        officer = User.objects.get(id=officer_id)
        officer.delete()
        messages.success(request, "Officer deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "Officer not found.")
    return redirect('view_officers')

@login_required
@user_passes_test(is_admin)
def view_public_users(request):
    public_users = User.objects.filter(profile__user_type='public')
    data = []

    for user in public_users:
        reports = CrimeReport.objects.filter(reporter=user)
        solved_count = reports.filter(status='solved').count()

        report_destinations = []
        for report in reports:
            pincode = report.pincode
            police = PoliceProfile.objects.filter(pincode=pincode).first()
            if police:
                report_destinations.append({
                    'pincode': pincode,
                    'station': police.station,
                    'state': police.state,
                    'district': police.district,
                    'city': police.city,
                    'assigned_to': police.user.username,
                })
            else:
                report_destinations.append({
                    'pincode': pincode,
                    'station': 'Not Assigned',
                    'state': 'N/A',
                    'district': 'N/A',
                    'city': 'N/A',
                    'assigned_to': 'N/A',
                })

        data.append({
            'user': user,
            'email': user.email,
            'total_reports': reports.count(),
            'solved_reports': solved_count,
            'report_destinations': report_destinations,
        })

    return render(request, 'admin/view_public_users.html', {'data': data})

@login_required
@user_passes_test(is_admin)
def delete_public_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('view_public_users')

@login_required
@user_passes_test(is_admin)
def admin_complaints_view(request):
    complaints = ContactUsComplaint.objects.all().order_by('-submitted_at')  # Latest first
    return render(request, 'admin/admin_complaints.html', {'complaints': complaints})

@login_required
@user_passes_test(is_admin)
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(ContactUsComplaint, id=complaint_id)
    if request.method == "POST":
        complaint.delete()
    return redirect('admin_complaints')

@login_required
@user_passes_test(is_admin)
def change_admin_credentials(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        user = request.user

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)

        user.save()
        messages.success(request, 'Credentials updated successfully. Please log in again.')
        return redirect('login')  # or your login URL name
    return render(request, 'admin/change_credentials.html')

















    