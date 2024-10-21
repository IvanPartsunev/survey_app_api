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
            owner = self.user,
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
                    "id": self.answer.id,
                    "answer_text": "Updated Answer",
                    "votes": 5
                }
            ],
            "comments": [
                {
                    "id": self.comment.id,
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
        self.assertEqual(response.data[0]["id"], self.product.pk)

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
        self.assertEqual(response.data['id'], self.question.pk)

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

    def test_create_answer(self):
        self.authenticate()

        data = {
            "question_id": self.question.pk,
            "answer_text": "New Sample Answer",
        }

        response = self.client.post('/answers/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the new answer has been created
        self.assertEqual(response.data['answer_text'], data['answer_text'])

        # Ensure the answer is linked to the question
        answer = AnswerModel.objects.get(pk=response.data['id'])
        self.assertEqual(answer.question.pk, self.question.pk)

    def test_update_answer(self):
        self.authenticate()

        data = {
            "answer_text": "Updated Answer Text"
        }

        response = self.client.patch(f'/answers/{self.answer.id}/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the answer has been updated
        self.answer.refresh_from_db()  # Refresh from the database
        self.assertEqual(self.answer.answer_text, data['answer_text'])

    def test_delete_answer(self):
        self.authenticate()

        response = self.client.delete(f'/answers/{self.answer.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the answer has been deleted
        self.assertFalse(AnswerModel.objects.filter(pk=self.answer.pk).exists())
