from django.urls import path

from polls_app.core.views import QuestionsListApiView, ProductsListApiView, ProductsCreateApiView, \
    ProductQuestionApiView

urlpatterns = (
    path("questions/", QuestionsListApiView.as_view(), name="questions_list"),
    path("products/", ProductsListApiView.as_view(), name="product_list"),
    path("product/", ProductsCreateApiView.as_view(), name="product-create"),
    path("product/<int:pk>/question/", ProductQuestionApiView.as_view(), name="product-rud"),
)
