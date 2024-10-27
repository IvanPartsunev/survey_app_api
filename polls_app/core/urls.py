from django.urls import path

from polls_app.core.views import ProductsListCreateApiView, ProductRetrieveUpdateDeleteApiView, \
    QuestionRetrieveUpdateDeleteApiView, QuestionCreateApiView, \
    AnswersCreateApiView, AnswersUpdateDeleteApiView, CommentsCreateApiView, CommentsUpdateDeleteApiView, \
    AnswerVoteApiView, QuestionActivateDeactivateApiView

urlpatterns = (
    path("products/", ProductsListCreateApiView.as_view(), name="products_create_retrieve"),
    path("products/<int:pk>/", ProductRetrieveUpdateDeleteApiView.as_view(), name="products_update_delete"),
    path("questions/", QuestionCreateApiView.as_view(), name="questions_create_retrieve"),
    path("questions/<int:pk>/", QuestionRetrieveUpdateDeleteApiView.as_view(), name="questions_update_delete"),
    path("questions/<int:pk>/activate-deactivate", QuestionActivateDeactivateApiView.as_view(), name="questions_update_delete"),
    path("answers/", AnswersCreateApiView.as_view(), name="answers_create"),
    path("answers/<int:pk>/", AnswersUpdateDeleteApiView.as_view(), name="answers_update_delete"),
    path("answers/<int:pk>/vote", AnswerVoteApiView.as_view(), name="answers_vote"),
    path("comments/", CommentsCreateApiView.as_view(), name="comment_create"),
    path("comments/<int:pk>/", CommentsUpdateDeleteApiView.as_view(), name="comments_update_delete"),
)
