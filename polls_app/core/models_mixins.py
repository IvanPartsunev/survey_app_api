from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()


class CreateUpdateOwnerMixin(models.Model):
    created_on = models.DateField(auto_now_add=True)
    edited_on = models.DateField(auto_now=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        abstract = True




