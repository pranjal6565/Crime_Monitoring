"""
URL configuration for Crime_Monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views
from main.views import home
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('safety-tips/', views.safety_tips, name='safety_tips'),
    path('about_us/', views.about_us, name='about_us'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/public/', views.public_dashboard, name='public_dashboard'),
    path('public/submit/', views.submit_crime_report, name='submit_crime'),
    path('public/my-reports/',views.my_reports_view, name='my_reports'),
    path('public/contact-us/', views.contact_us, name='contect_us'),
    path('public/complaint-success/', views.complaint_success, name='complaint_success'),
    path('public/view_complaints/', views.view_complaints, name='view_complaints'),
    path('delete_complaint/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('public/change-credentials/', views.public_change_credentials, name='public_change_credentials'),

    path('dashboard/police/', views.police_dashboard, name='police_dashboard'),
    path('police/reports/', views.police_all_reports, name='police_all_reports'),
    path('police/report/update/<int:report_id>/', views.update_status, name='update_status'),
    path('police/reports/pending/', views.pending_reports, name='pending_reports'),
    path('police/reports/in-progress/', views.in_progress_reports, name='in_progress_reports'),
    path('police/reports/solved/', views.solved_reports, name='solved_reports'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('police/change-password/', views.police_change_password, name='police_change_password'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('add-police/', views.add_police_view, name='add_police'),
    path('view-officers/', views.view_officers, name='view_officers'),
    path('delete-officer/<int:officer_id>/', views.delete_officer, name='delete_officer'),
    path('view-public-users/', views.view_public_users, name='view_public_users'),
    path('delete-public-user/<int:user_id>/', views.delete_public_user, name='delete_public_user'),
    path('admin-complaints/', views.admin_complaints_view, name='admin_complaints'),
    path('admin-complaints/delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('change-credentials/', views.change_admin_credentials, name='change_admin_credentials'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)