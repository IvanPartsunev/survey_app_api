from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from polls_app.core.models import AnswerModel, CommentModel, QuestionModel, ProductModel
from polls_app.custom_exeption import ApplicationError

UserModel = get_user_model()


class CoreViewsTests(APITestCase):

    def setUp(self):
        self.user = UserModel.objects.create_user(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            is_active=True
        )

        # Obtain JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.product = ProductModel.objects.create(
            name="Product test name",
            owner=self.user,
        )

        self.question = QuestionModel.objects.create(
            owner=self.user,
            question_type="Text",
            question_text="Sample Question",
            is_active=True,
            product=self.product,
        )

        self.answer = AnswerModel.objects.create(
            question=self.question,
            answer_text="Sample Answer",
            votes=0,
            owner = self.user
        )

        self.comment = CommentModel.objects.create(
            question=self.question,
            comment_text="Sample Comment"
        )

        self.data = {
            "question_type": "Single choice",
            "question_text": "Updated Question",
            "is_active": True,
            "answers": [
                {
                    "pk": self.answer.id,
                    "answer_text": "Updated Answer",
                    "votes": 5
                }
            ],
            "comments": [
                {
                    "pk": self.comment.id,
                    "comment": "Updated Comment",
                    "context": {
                        "question_pk": self.question.pk
                    }
                }
            ]
        }

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_list_products(self):
        self.authenticate()

        response = self.client.get("/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response contains the product
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.product.name)
        self.assertEqual(response.data[0]["pk"], self.product.pk)

        # Check if product_questions data is present
        self.assertIn("product_questions", response.data[0])
        self.assertEqual(len(response.data[0]["product_questions"]), 1)

    def test_update_product(self):
        self.authenticate()

        data = {
            "name": "Updated Product Name"
        }

        response = self.client.patch(f"/products/{self.product.pk}/", data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the product has been updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, data["name"])

    def test_delete_product(self):
        self.authenticate()

        response = self.client.delete(f"/products/{self.product.pk}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the product has been deleted
        self.assertFalse(ProductModel.objects.filter(pk=self.product.pk).exists())

    def test_create_question(self):
        self.authenticate()

        data = {
            "product_id": self.product.pk,
            "question_type": "Single choice",
            "question_text": "New Sample Question"
        }

        response = self.client.post('/questions/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the new question has been created
        self.assertEqual(response.data['question_text'], data['question_text'])
        self.assertEqual(response.data['question_type'], data['question_type'])
        self.assertIsNotNone(response.data['id'])

        # Ensure the question is linked to the product
        question = QuestionModel.objects.get(pk=response.data['id'])
        self.assertEqual(question.product.pk, self.product.pk)

    def test_retrieve_question(self):
        self.authenticate()

        response = self.client.get(f'/questions/{self.question.pk}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the question details
        self.assertEqual(response.data['question_text'], self.question.question_text)
        self.assertEqual(response.data['pk'], self.question.pk)

        # Check if answers and comments are included
        self.assertIn('answers', response.data)
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['answers']), 1)  # One answer linked to this question
        self.assertEqual(len(response.data['comments']), 1) # One comment linked to this question

    def test_update_question(self):
        # Authenticate the user
        self.authenticate()

        # Data to update the question
        data = {
            "question_text": "Updated Question Text",
            "question_type": "Multiple choices"
        }

        # Make a PATCH request to update the question
        response = self.client.patch(f'/questions/{self.question.pk}/', data=data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the question has been updated
        self.question.refresh_from_db()
        self.assertEqual(self.question.question_text, data['question_text'])
        self.assertEqual(self.question.question_type, data['question_type'])

    def test_delete_question(self):
        self.authenticate()

        response = self.client.delete(f'/questions/{self.question.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the question has been deleted
        self.assertFalse(QuestionModel.objects.filter(pk=self.question.pk).exists())

    # def test_update_question_assert_success(self):
    #     self.authenticate()
    #
    #     url = reverse("question_rud", args=[self.question.id])
    #     response = self.client.put(url, self.data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     self.question.refresh_from_db()
    #     self.answer.refresh_from_db()
    #
    #     self.assertEqual(self.question.question_text, "Updated Question")
    #     self.assertEqual(self.answer.answer_text, "Updated Answer")
    #     self.assertEqual(self.answer.votes, 5)
    #
    # def test_update_question_create_new_answer_assert_success(self):
    #     self.authenticate()
    #
    #     new_data = {
    #         "question_type": "Text",
    #         "question_text": "Updated Question Again",
    #         "is_active": True,
    #         "answers": [
    #             {
    #                 "answer_text": "New Answer",
    #                 "votes": 10
    #             }
    #         ]
    #     }
    #
    #     url = reverse("question_rud", args=[self.question.id])
    #     response = self.client.put(url, new_data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     new_answer = AnswerModel.objects.get(answer_text="New Answer")
    #     self.assertEqual(new_answer.answer_text, "New Answer")
    #     self.assertEqual(new_answer.votes, 10)
    #
    # def test_update_question_create_new_answer_assert_error(self):
    #     self.authenticate()
    #
    #     user_2 = UserModel.objects.create_user(
    #         email="test2@test.com",
    #         username="testuser2",
    #         password="testpassword",
    #         is_active=True
    #     )
    #
    #     product_2 = ProductModel.objects.create(
    #         name="Product2 test name",
    #         owner=user_2,
    #     )
    #
    #     question_2 = QuestionModel.objects.create(
    #         owner=user_2,
    #         question_type="Text",
    #         question_text="Sample Question",
    #         is_active=True,
    #         product=product_2,
    #     )
    #
    #     self.answer = AnswerModel.objects.create(
    #         question=question_2,
    #         answer_text="Sample Answer 2",
    #         votes=0
    #     )
    #
    #     new_data = {
    #         "question_type": "Text",
    #         "question_text": "Updated Question Again",
    #         "is_active": True,
    #         "answers": [
    #             {
    #                 "pk": self.answer.pk,
    #                 "answer_text": "New Answer",
    #                 "votes": 10
    #             }
    #         ]
    #     }
    #
    #     url = reverse("question_rud", args=[self.question.id])
    #     response = self.client.put(url, new_data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    #     self.assertEqual(response.data["error"],
    #                      "Answer with this Primary key already exists for another user. "
    #                      "No pk should be provided when creating new answer.")
    #
    # def test_comment_create_assert_success(self):
    #     self.authenticate()
    #
    #     new_data = {
    #         "comment": "New Comment",
    #         "context": {
    #             "question_pk": self.question.pk
    #         }
    #     }
    #
    #     url = reverse("comment_create_list")
    #     response = self.client.post(url, new_data, format="json")
    #
    #     pk = response.data.get("pk")
    #     new_comment = CommentModel.objects.get(pk=pk)
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     self.assertEqual(new_comment.comment, "New Comment")
    #
    # def test_comment_create_question_does_not_exists_assert_application_error(self):
    #     self.authenticate()
    #
    #     new_data = {
    #         "comment": "New Comment",
    #         "context": {
    #             "question_pk": 0
    #         }
    #     }
    #
    #     url = reverse("comment_create_list")
    #
    #     with self.assertRaises(ApplicationError) as context:
    #         self.client.post(url, new_data, format="json")
    #
    #     self.assertIn("Question with provided pk does not exists.", str(context.exception))
