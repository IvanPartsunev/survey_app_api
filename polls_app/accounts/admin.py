from django.contrib import admin

from polls_app.accounts.models import AccountModel


@admin.register(AccountModel)
class AccountModelAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "auth_provider",
    )

    list_display_links = (
        "email",
        "username",
    )

    list_filter = (
        "auth_provider",
    )

    search_fields = (
        "email",
        "username",
    )

    def __str__(self):
        return f"{self.email} with Username: {self.username}"
