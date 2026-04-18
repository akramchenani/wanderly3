from django.contrib import admin
from .models import Partner, Hotel, Restaurant, Coffee, Agency

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'partner_type', 'is_approved', 'created_at']
    list_filter = ['partner_type', 'is_approved']
    actions = ['approve_partners']

    def approve_partners(self, request, queryset):
        queryset.update(is_approved=True)
        from notifications.models import Notification
        for partner in queryset:
            Notification.objects.create(
                user=partner.user,
                notif_type='approval',
                content='Your partner account has been approved!'
            )
    approve_partners.short_description = "Approve selected partners"

admin.site.register(Hotel)
admin.site.register(Restaurant)
admin.site.register(Coffee)
admin.site.register(Agency)
