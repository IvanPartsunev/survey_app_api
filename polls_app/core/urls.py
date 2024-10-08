from django.urls import path

from polls_app.core.views import ProductsListCreateApiView, ProductRetrieveUpdateDeleteApiView, QuestionRetrieveUpdateDeleteApiView, QuestionCreateApiView, \
    AnswersCreateApiView, AnswersReadUpdateDeleteApiView, CommentsCreateApiView, CommentsUpdateDeleteApiView

urlpatterns = (
    path("products/", ProductsListCreateApiView.as_view(), name="products"),
    path("product/<int:pk>/", ProductRetrieveUpdateDeleteApiView.as_view(), name="product"),
    path("question/", QuestionCreateApiView.as_view(), name="question"),
    path("question/<int:pk>/", QuestionRetrieveUpdateDeleteApiView.as_view(), name="question"),
    path("answers/", AnswersCreateApiView.as_view(), name="answer"),
    path("answers/<int:pk>", AnswersReadUpdateDeleteApiView.as_view(), name="answers"),
    path("comments/", CommentsCreateApiView.as_view(), name="comment"),
    path("comments/<int:pk>/", CommentsUpdateDeleteApiView.as_view(), name="comments"),
)
