from django.urls import path

from polls_app.core.views import ProductsListCreateApiView, ProductRetrieveUpdateDeleteApiView, QuestionsApiView, QuestionsListApiView, \
    AnswersCreateApiView, AnswersReadUpdateDeleteApiView, CommentsCreateApiView, CommentsReadUpdateDeleteApiView

urlpatterns = (
    path("products/", ProductsListCreateApiView.as_view(), name="products"),
    path("products/<int:pk>/", ProductRetrieveUpdateDeleteApiView.as_view(), name="product"),
    path("products/<int:product_pk>/questions", QuestionsListApiView.as_view(), name="questions"),
    path("products/<int:product_pk>/questions/<int:question_pk>/", QuestionsApiView.as_view(), name="question"),
    path(
        "questions/<int:question_pk>/answers/",
        AnswersCreateApiView.as_view(),
        name="answer"
    ),

    path(
        "questions/<int:question_pk>/answers/<int:answer_pk>",
        AnswersReadUpdateDeleteApiView.as_view(),
        name="answers"
    ),

    path(
        "questions/<int:question_pk>/comments/",
        CommentsCreateApiView.as_view(),
        name="comment"
    ),

    path(
        "questions/<int:question_pk>/comments/<int:comment_pk>/",
        CommentsReadUpdateDeleteApiView.as_view(),
        name="comments"
    ),

)
