from django.contrib import admin

from polls_app.core.models import ProductModel, QuestionModel, AnswerModel, CommentModel


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
    )

    search_fields = (
        "name",
        "owner",
    )

    ordering = (
        "name",
        "owner",
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.name = None

    def __str__(self):
        return self.name


@admin.register(QuestionModel)
class QuestionModelAdmin(admin.ModelAdmin):
    list_display = (
        "question_type",
        "question_text",
        "is_active",
        "owner",
        "product",
    )

    search_fields = (
        "question_type",
        "question_text",
        "is_active",
        "owner",
        "product",
    )

    ordering = (
        "question_type",
        "question_text",
        "is_active",
        "owner",
        "product",
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.question_text = None

    def __str__(self):
        return self.question_text


@admin.register(AnswerModel)
class AnswerModelAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "answer_text",
        "votes",
    )

    search_fields = (
        "question",
        "answer_text",
        "votes",
    )

    ordering = (
        "question",
        "answer_text",
        "votes",
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.answer_text = None

    def __str__(self):
        return self.answer_text


@admin.register(CommentModel)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = (
        "question",
    )
