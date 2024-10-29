from django.urls import include, path
from django.conf import settings
from . import views  # Import your views
from django.contrib.auth import views as auth_views

# Main URL patterns
urlpatterns = [
    path('', views.home, name='home'),  # Existing home view
    path('login/', views.custom_login_view, name='login'),  # Custom login page
    path('logout/', views.logout_view, name='logout'),  # Custom logout view
    path('dashboard/', views.dashboard, name='dashboard'),  # Restricted page
    path('admin-view/', views.admin_view, name='admin_view'),  # Admin-only page
    path('viewer-view/', views.viewer_view, name='viewer_view'),  # Viewer-only page
    path('upload_excel/', views.upload_excel, name='upload_excel'),
    path('chart_data/', views.get_chart_data, name='chart_data'),
    path('approve-update/', views.approve_update, name='approve_update'),
    path('confirm_upload/', views.confirm_upload, name='confirm_upload'),
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Include the Django Debug Toolbar URLs if the DEBUG setting is True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
