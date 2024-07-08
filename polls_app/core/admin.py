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

    def __str__(self):
        return f"{self.name}"


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

    def __str__(self):
        return f"{self.question_text}"


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

    def __str__(self):
        return f"{self.answer_text}"


@admin.register(CommentModel)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "comment_text",
    )

    search_fields = (
        "question",
        "comment_text",
    )

    ordering = (
        "question",
        "comment_text",
    )

    def __str__(self):
        return f"{self.comment_text}"
