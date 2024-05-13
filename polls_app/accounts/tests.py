from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class AccountViewsTests(APITestCase):

    def test_create_account_assert_successful_create(self):

        url = reverse("register_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserModel.objects.count(), 1)
        self.assertEqual(UserModel.objects.get(email="testmail@test.com").email, "testmail@test.com")

    def test_create_account_assert_account_exists(self):
        UserModel.objects.create_user(email="testmail@test.com", password="testpassword")

        url = reverse("register_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_login_account_assert_successful_login(self):
        """
        Ensure obtain a token by logging in.
        """

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        url = reverse("login_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_password_reset_assert_successful(self):

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        url = reverse("reset_password_api_view")
        data = {"email": "testmail@test.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_assert_not_found(self):

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        url = reverse("reset_password_api_view")
        data = {"email": "testmail_wrong@test.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_confirm_assert_successful(self):

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        data = {"password": "testmailtest"}

        encoded_pk = urlsafe_base64_encode(str(user.pk).encode())
        token = PasswordResetTokenGenerator().make_token(user)

        url = reverse("reset_password_confirm_api_view", kwargs={"encoded_pk": encoded_pk, "token": token})
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_assert_invalid_token(self):

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        url = reverse("reset_password_api_view")
        data = {"email": "testmail@test.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("reset_password_confirm_api_view", kwargs={"encoded_pk": "test", "token": "test"})
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)