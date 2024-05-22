from rest_framework import views as api_views
from rest_framework import generics as views

from polls_app.core.models import QuestionModel


class QuestionApiView(views.ListAPIView):
    pass
