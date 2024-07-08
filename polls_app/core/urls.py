from django.urls import path

from polls_app.core.views import ProductsListApiView, ProductApiView, QuestionsApiView, QuestionsListApiView

# from polls_app.core.views import QuestionsListApiView, ProductsListApiView, ProductsCreateApiView, \
#     QuestionCreateApiView, QuestionRUDApiView, AnswerDeleteApiView, CommentApiView, CommentListCreateApiView
#
# urlpatterns = (
#     path("questions/", QuestionsListApiView.as_view(), name="questions_list"),
#     path("products/", ProductsListApiView.as_view(), name="product_list"),
#     path("product/", ProductsCreateApiView.as_view(), name="product_create"),
#     path("product/<int:pk>/question/", QuestionCreateApiView.as_view(), name="question_create"),
#     path("question/<int:pk>", QuestionRUDApiView.as_view(), name="question_rud"),
#     path("answer/<int:pk>", AnswerDeleteApiView.as_view(), name="answer_delete"),
#     path("comment/", CommentListCreateApiView.as_view(), name="comment_create_list"),
#     path("comment/<int:pk>", CommentApiView.as_view(), name="comment_delete"),
# )

urlpatterns = (
    path("products/", ProductsListApiView.as_view(), name="products"),
    path("products/<int:pk>/", ProductApiView.as_view(), name="product"),
    path("products/<int:product_pk>/questions", QuestionsListApiView.as_view(), name="questions"),
    # path("products/<int:product_pk>/questions/<int:question_pk>/", ProductApiView.as_view(), name="product"),
)
