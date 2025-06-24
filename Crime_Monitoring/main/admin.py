from django.contrib import admin
from .models import Profile, ContactUsComplaint


    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username',)

@admin.register(ContactUsComplaint)
class ContactUsComplaintAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'email', 'state', 'district', 'submitted_at', 'complaint')
    list_filter = ('state', 'district')
    search_fields = ('name', 'complaint', 'contact_no')


