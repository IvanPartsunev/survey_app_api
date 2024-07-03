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

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.email = None

    def __str__(self):
        return self.email
