from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import models as auth_models
from django.db import models

from polls_app.accounts.managers import AccountManager


class AccountModel(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        max_length=150,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
            "blank": _("This field is required.")
        },
    )

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    auth_provider = models.CharField(
        max_length=150,
        default="App auth",
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.email} with Username: {self.username}"
