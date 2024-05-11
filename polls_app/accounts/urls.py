from django.urls import path, include

from polls_app.accounts.views import CreateAccountApiView

urlpatterns = (
    path("register/", CreateAccountApiView.as_view(), name="api_register_view"),
)