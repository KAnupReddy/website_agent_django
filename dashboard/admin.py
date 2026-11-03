from django.contrib import admin

from .models import Business, Deployment, Design, Email, Enrichment


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business_type', 'location', 'status', 'website_status', 'created_at')
    list_filter = ('status', 'website_status', 'business_type')
    search_fields = ('name', 'location', 'email', 'phone')


@admin.register(Enrichment)
class EnrichmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'tone', 'color_palette', 'created_at')


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'version', 'style_name', 'status', 'created_at')
    list_filter = ('status', 'style_name')


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'design', 'url', 'status', 'deployed_at')
    list_filter = ('status',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'to_email', 'sent_status', 'response_status', 'sent_at')
    list_filter = ('sent_status', 'response_status')
