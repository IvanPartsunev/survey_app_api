from django.urls import path

from polls_app.core.views import QuestionApiView

urlpatterns = (
    path("questions/", QuestionApiView.as_view, name="questions"),
)
