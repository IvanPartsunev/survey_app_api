from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from polls_app.core.models import AnswerModel, CommentModel, QuestionModel, ProductModel
from polls_app.core.services import decode_comment_jwt_token_service
from polls_app.custom_exeption import ApplicationError

UserModel = get_user_model()


class CoreViewsTests(APITestCase):

    def setUp(self):
        self.user_1 = UserModel.objects.create_user(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            is_active=True
        )

        # Obtain JWT token for the user
        refresh = RefreshToken.for_user(self.user_1)
        self.access_token = str(refresh.access_token)

        self.product = ProductModel.objects.create(
            name="Product test name",
            owner=self.user_1,
        )

        self.question = QuestionModel.objects.create(
            owner=self.user_1,
            question_type="Text",
            question_text="Sample Question",
            is_active=True,
            product=self.product,
        )

        self.answer = AnswerModel.objects.create(
            question=self.question,
            answer_text="Sample Answer",
            votes=0,
            owner=self.user_1,
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
        self.assertEqual(len(response.data['comments']), 1)  # One comment linked to this question

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

    def test_vote_on_answer_authenticated_user(self):
        """Test voting on an answer as an authenticated user."""
        self.authenticate()
        response = self.client.post(f'/answers/{self.answer.pk}/vote')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Your vote has been counted.")

        # Verify that the vote count increased by 1
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.votes, 1)

    def test_vote_on_answer_anonymous_user(self):
        """Test voting on an answer as an anonymous user with cookie handling."""
        response = self.client.post(f'/answers/{self.answer.pk}/vote')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Your vote has been counted.")

        # Verify the vote count has increased
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.votes, 1)

        # Check if the answer ID was added to the voted_answers cookie
        self.assertIn("voted_answers", response.cookies)
        voted_answers_cookie = response.cookies["voted_answers"].value
        self.assertIn(str(self.answer.pk), voted_answers_cookie)

    def test_prevent_duplicate_vote_anonymous_user(self):
        """Test that an anonymous user cannot vote on the same answer more than once."""
        # First vote
        response = self.client.post(f'/answers/{self.answer.pk}/vote')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Set the voted_answers cookie to simulate a previous vote
        voted_answers_cookie = response.cookies["voted_answers"].value
        self.client.cookies["voted_answers"] = voted_answers_cookie

        # Attempt to vote again on the same answer
        second_response = self.client.post(f'/answers/{self.answer.pk}/vote')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data["detail"], "You have already voted on this answer.")

        # Ensure the vote count did not increase
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.votes, 1)

    def test_prevent_duplicate_vote_authenticated_user(self):
        """Test that an authenticated user cannot vote on the same answer more than once."""
        self.authenticate()

        # First vote
        response = self.client.post(f'/answers/{self.answer.pk}/vote')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to vote again on the same answer
        second_response = self.client.post(f'/answers/{self.answer.pk}/vote')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data["detail"], "You have already voted on this answer.")

        # Ensure the vote count did not increase
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.votes, 1)


class CommentsApiTests(APITestCase):

    def setUp(self):
        self.user_2 = UserModel.objects.create_user(
            email="auth_user@test.com",
            username="authuser",
            password="authpassword",
            is_active=True
        )

        # Obtain JWT token for the authenticated user
        refresh = RefreshToken.for_user(self.user_2)
        self.access_token = str(refresh.access_token)

        self.product = ProductModel.objects.create(
            name="Product test name",
            owner=self.user_2,
        )

        self.question = QuestionModel.objects.create(
            owner=self.user_2,
            question_type="Text",
            question_text="Sample Question",
            is_active=True,
            product=self.product,
        )

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_create_comment_authenticated_user(self):
        """Test creating a comment as an authenticated user."""
        self.authenticate()

        data = {
            "question_id": self.question.pk,
            "comment_text": "This is a test comment by an authenticated user.",
        }
        response = self.client.post('/comments/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment_text"], data["comment_text"])

    def test_create_comment_anonymous_user(self):
        """Test creating a comment as an anonymous user with cookie handling."""
        data = {
            "question_id": self.question.pk,
            "comment_text": "This is a test comment by an anonymous user.",
        }
        response = self.client.post('/comments/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment_text"], data["comment_text"])

        # Check if a token has been set in the cookie
        self.assertIn("anonymous_user_token", response.cookies)
        self.assertTrue(response.cookies["anonymous_user_token"]["httponly"])

    def test_prevent_duplicate_comment_anonymous_user(self):
        """Test that an anonymous user cannot comment more than once on the same question."""
        data = {
            "question_id": self.question.pk,
            "comment_text": "First anonymous comment.",
        }
        first_response = self.client.post('/comments/', data=data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        second_response = self.client.post('/comments/', data=data, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", second_response.data)
        self.assertEqual(second_response.data["detail"],
                         f"Question ID {self.question.id} already has a comment from this user.")

    def test_update_comment_authenticated_user(self):
        """Authenticated user updates their comment."""
        self.authenticate()
        comment = CommentModel.objects.create(
            question=self.question,
            comment_text="Original comment",
            owner=self.user_2.username,
        )

        data = {"comment_text": "Updated comment by authenticated user."}
        response = self.client.patch(f'/comments/{comment.pk}/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.comment_text, data["comment_text"])

    def test_update_comment_anonymous_user(self):
        """Anonymous user attempts to update their comment."""
        comment_data = {
            "question_id": self.question.pk,
            "comment_text": "Anonymous comment",
        }
        create_response = self.client.post('/comments/', data=comment_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Get cookie token to simulate ownership check
        token = create_response.cookies["anonymous_user_token"].value
        self.client.cookies["anonymous_user_token"] = token

        # Update the comment as the same anonymous user
        data = {"comment_text": "Updated anonymous comment"}
        comment_id = create_response.data["id"]
        update_response = self.client.patch(f'/comments/{comment_id}/', data=data, format='json')

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        comment = CommentModel.objects.get(pk=comment_id)
        self.assertEqual(comment.comment_text, data["comment_text"])

    def test_delete_comment_anonymous_user_removes_cookie_entry(self):
        """Anonymous user deletes their comment, removing the question from the cookie."""
        # Create the comment first
        comment_data = {
            "question_id": self.question.pk,
            "comment_text": "Anonymous comment for deletion",
        }
        create_response = self.client.post('/comments/', data=comment_data, format='json')
        comment_id = create_response.data["id"]
        token = create_response.cookies["anonymous_user_token"].value

        self.client.cookies["anonymous_user_token"] = token

        # Delete the comment
        delete_response = self.client.delete(f'/comments/{comment_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the comment ID is removed from the JWT token in the cookie
        updated_token = delete_response.cookies.get("anonymous_user_token").value
        payload = decode_comment_jwt_token_service(updated_token)
        self.assertNotIn(self.question.pk, payload["questions"])


class PermissionsTests(APITestCase):

    def setUp(self):
        # Setup for authenticated user
        self.authenticated_user = UserModel.objects.create_user(
            email="auth_user@test.com",
            username="authuser",
            password="authpassword",
            is_active=True
        )
        refresh = RefreshToken.for_user(self.authenticated_user)
        self.access_token = str(refresh.access_token)

        # Anonymous user setup
        self.anonymous_user_token = None  # This will be set after creating a comment

        # Create a product, question, answer, and comment
        self.product = ProductModel.objects.create(name="Test Product", owner=self.authenticated_user)
        self.question = QuestionModel.objects.create(
            owner=self.authenticated_user,
            question_type="Text",
            question_text="Sample Question",
            is_active=True,
            product=self.product
        )
        self.answer = AnswerModel.objects.create(
            question=self.question,
            answer_text="Sample Answer",
            votes=0,
            owner=self.authenticated_user,
        )

        # Comment created by anonymous user
        comment_data = {
            "question_id": self.question.pk,
            "comment_text": "Anonymous comment"
        }
        response = self.client.post('/comments/', data=comment_data, format='json')
        self.anonymous_user_token = response.cookies.get("anonymous_user_token").value
        self.client.cookies["anonymous_user_token"] = self.anonymous_user_token
        self.comment = CommentModel.objects.get(pk=response.data["id"])

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_view_access_permissions_for_anonymous_user(self):
        """Anonymous user with no token should not access restricted endpoints."""
        # Try to access a protected product detail endpoint
        response = self.client.get(f'/products/{self.product.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_permissions_for_anonymous_user_with_token(self):
        """Anonymous user with a valid token should access their own comments."""
        # Set the JWT cookie token for the anonymous user
        self.client.cookies["anonymous_user_token"] = self.anonymous_user_token

        response = self.client.patch(f'/comments/{self.comment.pk}/',
                                     data={"question_id": self.question.pk, "comment_text": "Anonymous comment"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["comment_text"], self.comment.comment_text)

    def test_access_permissions_for_authenticated_user(self):
        """Authenticated user should access their own product, question, and answer."""
        self.authenticate()

        # Access product
        response = self.client.patch(f'/products/{self.product.pk}/', data={"name": "Test Product 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(response.data["data"]["name"], self.product.name)

        # Access question
        response = self.client.patch(f'/questions/{self.question.pk}/', data={"question_text": "string 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(response.data["data"]["question_text"], self.question.question_text)

        # Access answer
        response = self.client.patch(f'/answers/{self.answer.pk}/', data={"answer_text": "New text"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.answer.refresh_from_db()
        self.assertEqual(response.data["data"]["answer_text"], self.answer.answer_text)

    def test_anonymous_user_cannot_edit_or_delete_another_user_comment(self):
        """Anonymous user should not be able to edit or delete other users' comments."""

        foreign_comment = CommentModel.objects.create(
            question=self.question,
            comment_text="Comment",
            owner=self.authenticated_user.username,
        )

        self.client.credentials()

        data = {"comment_text": "Malicious edit attempt"}

        response = self.client.patch(f'/comments/{foreign_comment.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to delete another user's comment
        response = self.client.delete(f'/comments/{foreign_comment.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_cannot_edit_or_delete_another_user_comment(self):
        """Authenticated user should not edit or delete another user's comment."""
        another_user = UserModel.objects.create_user(email="other@test.com", username="otheruser", password="password")

        foreign_comment = CommentModel.objects.create(
            question=self.question,
            comment_text="Comment",
            owner=another_user.username,
        )

        self.client.credentials()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)


        # Attempt to update comment
        data = {"comment_text": "Unauthorized edit"}
        response = self.client.patch(f'/comments/{foreign_comment.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to delete comment
        response = self.client.delete(f'/comments/{foreign_comment.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_anonymous_user_with_valid_token_can_delete_own_comment(self):
        """Anonymous user with a valid token should delete their comment, removing it from the token."""
        # Set the valid anonymous user token

        self.client.cookies["anonymous_user_token"] = self.anonymous_user_token

        response = self.client.delete(f'/comments/{self.comment.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        print("Response status code:", response.status_code)
        print("Response data:", response.data)

        # Ensure the comment is deleted
        self.assertFalse(CommentModel.objects.filter(pk=self.comment.pk).exists())

        # Check that the comment is removed from the token
        updated_token = response.cookies.get("anonymous_user_token").value
        payload = decode_comment_jwt_token_service(updated_token)
        self.assertNotIn(str(self.comment.question.pk), payload["questions"])

    def test_authenticated_user_can_edit_own_comment(self):
        """Authenticated user should edit their own comment."""
        self.authenticate()
        comment = CommentModel.objects.create(
            question=self.question,
            comment_text="Original comment",
            owner=self.authenticated_user.username,
        )

        data = {"comment_text": "Edited comment by authenticated user"}
        response = self.client.patch(f'/comments/{comment.pk}/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.comment_text, data["comment_text"])

    def test_anonymous_user_edit_or_delete_invalid_token(self):
        """Anonymous user with an invalid token cannot edit or delete comments."""
        # Set an invalid token
        self.client.cookies["anonymous_user_token"] = "invalid_token"

        # Attempt to update comment
        data = {"comment_text": "Invalid token edit attempt"}
        response = self.client.patch(f'/comments/{self.comment.pk}/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Attempt to delete comment
        response = self.client.delete(f'/comments/{self.comment.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
