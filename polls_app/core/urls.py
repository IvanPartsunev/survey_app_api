from django.urls import path

from polls_app.core.views import QuestionsListApiView, ProductsListApiView, ProductsCreateApiView, \
    QuestionCreateApiView, QuestionRUDApiView

urlpatterns = (
    path("questions/", QuestionsListApiView.as_view(), name="questions_list"),
    path("products/", ProductsListApiView.as_view(), name="product_list"),
    path("product/", ProductsCreateApiView.as_view(), name="product-create"),
    path("product/<int:pk>/question/", QuestionCreateApiView.as_view(), name="question-create"),
    path("question/<int:pk>", QuestionRUDApiView.as_view(), name="question-rud"),
)
