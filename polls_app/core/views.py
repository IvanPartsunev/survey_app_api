from rest_framework import views as api_views
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated

from polls_app.core.Serializers import QuestionSerializer
from polls_app.core.models import QuestionModel


class QuestionsListApiView(views.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (QuestionModel.objects
                    .prefetch_related("question_choices", "question_comments")
                    .filter(owner=self.request.user))
        return queryset
