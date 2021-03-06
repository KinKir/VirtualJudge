from django.urls import path

from submission import views

urlpatterns = [

    path('submission/', views.SubmissionAPI.as_view(), name='submission'),
    path('verdict/<int:submission_id>/', views.VerdictAPI.as_view(), name='verdict'),
    path('submissions/', views.SubmissionListAPI.as_view(), name='submissions'),
    path('reload/<int:submission_id>/', views.ReloadAPI.as_view(), name='reload'),
]
