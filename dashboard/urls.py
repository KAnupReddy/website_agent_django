from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),
    path('businesses', views.businesses, name='businesses'),
    path('businesses/add', views.create, name='business_add'),
    path('businesses/<int:pk>', views.show, name='business_detail'),
    path('businesses/<int:pk>/run', views.run_pipeline, name='business_run'),
    path('businesses/<int:pk>/status', views.update_status, name='business_status'),
    path('businesses/<int:pk>/download', views.download, name='business_download'),
    path('businesses/<int:pk>/delete', views.delete_business, name='business_delete'),
    path('businesses/<int:pk>/regenerate', views.regenerate, name='business_regenerate'),

    # Design preview (serve raw HTML)
    path('preview/<int:design_id>', views.preview, name='preview'),
]
