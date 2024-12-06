from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('course/', views.course, name='course'),
    path('classroom/', views.classroom, name='classroom'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_profile/change_photo/', views.change_photo, name='change_photo'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('my_classes/', views.my_classes, name='my_classes'),
    path('my_exercises/', views.my_exercises, name='my_exercises'),
    path('my_quizzes/', views.my_quizzes, name='my_quizzes'),
    path('register/', views.user_register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('admin-page/', views.admin_page, name='admin-page'),
    path('admin-page/instructor-list/', views.instructor_list, name='instructor-list'),
    path('admin-page/student-list/', views.student_list, name='student-list'),
    path('admin-page/student/<int:pk>/view/', views.student_view, name='student-view'),
    path('admin-page/student/<int:pk>/edit/', views.student_edit, name='student-edit'),
    path('admin-page/student/<int:pk>/delete/', views.student_delete, name='student-delete'),
    path('admin-page/ctu-student-list/', views.ctu_student_list, name='ctu-student-list'),
    path('admin-page/instructor-form/', views.instructor_form, name='instructor-form'),
    #path('admin-page/student-form/', views.student_form, name='student-form'),
    path('admin-page/instructor/<int:pk>/view/', views.instructor_view, name='instructor-view'),
    path('admin-page/instructor/<int:pk>/edit/', views.instructor_edit, name='instructor-edit'),
    path('admin-page/instructor/<int:pk>/delete/', views.instructor_delete, name='instructor-delete'),
    path('view_pdf/<int:course_id>/', views.view_pdf, name='view_pdf'),
    path('create_classroom/', views.create_classroom, name='create_classroom'),
    path('join_classroom/', views.join_classroom, name='join_classroom'),
    path('lectures/<int:classroom_id>/', views.lectures, name='lectures'),
    path('activities/<int:classroom_id>/', views.activities, name='activities'),
    path('students/<int:classroom_id>/', views.students, name='students'),
    path('4pics/', views.four_pics_game, name='four_pics_game'),
    path('4pics/<int:puzzle_id>/', views.four_pics_game, name='four_pics_game'),
    path('unenroll_student/<int:student_id>/<int:classroom_id>/', views.unenroll_student, name='unenroll_student'),
    path('classroom/<int:classroom_id>/invite/', views.generate_invite_link, name='generate_invite_link'),
    path('classroom/join/<str:token>/', views.join_classroom_invite, name='join_classroom_invite'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)