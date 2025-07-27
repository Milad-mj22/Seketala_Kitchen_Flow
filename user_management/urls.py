from django.contrib import admin

from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from users.views import CustomLoginView, ResetPasswordView, ChangePasswordView

from users.forms import LoginForm


urlpatterns = [
    path('admin/', admin.site.urls),

    

    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='users/login.html',
                                           authentication_form=LoginForm), name='login'),

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

     path('password-change/', ChangePasswordView.as_view(), name='password_change'),
     path('menu/', include('menu.urls'), name='password_change'),
     path('order_flow/', include('order_flow.urls'), name='password_change'),
     path('stone_flow/', include('StoneFlow.urls'), name='password_change'),
     path('api/', include('api.urls')),  # Add this line
     path('SocialApps/', include('SocialApps.urls')),  # ← add this line
     path('formApp/', include('formApp.urls')),  # ← add this line
     path('mines/', include('mines.urls')),
     path('dashboard/', include('dashboard.urls')),
     path('utils/', include('utils.urls')),

     path('', include('users.urls')),

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
