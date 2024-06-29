from django.contrib import admin

from polls_app.core.models import ProductModel, QuestionModel, AnswerModel


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
