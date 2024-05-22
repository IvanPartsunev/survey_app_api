from django.urls import path

from polls_app.core.views import QuestionsListApiView

urlpatterns = (
    path("", QuestionsListApiView.as_view(), name="questions_list"),
)
