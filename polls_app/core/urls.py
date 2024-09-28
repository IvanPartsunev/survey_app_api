from django.urls import path

from polls_app.core.views import ProductsListCreateApiView, ProductRetrieveUpdateDeleteApiView, QuestionsApiView, QuestionsListApiView, \
    AnswersCreateApiView, AnswersReadUpdateDeleteApiView, CommentsCreateApiView, CommentsReadUpdateDeleteApiView

urlpatterns = (
    path("products/", ProductsListCreateApiView.as_view(), name="products"),
    path("products/<int:pk>/", ProductRetrieveUpdateDeleteApiView.as_view(), name="product"),
    path("questions/", QuestionsListApiView.as_view(), name="questions"),
    path("questions/<int:question_pk>/", QuestionsApiView.as_view(), name="question"),
    path("answers/", AnswersCreateApiView.as_view(), name="answer"),
    path("answers/<int:answer_pk>", AnswersReadUpdateDeleteApiView.as_view(), name="answers"),
    path("comments/", CommentsCreateApiView.as_view(), name="comment"),
    path("comments/<int:comment_pk>/", CommentsReadUpdateDeleteApiView.as_view(), name="comments"),
)
