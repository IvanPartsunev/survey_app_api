# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.urls import reverse
# from django.utils.http import urlsafe_base64_encode
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model
#
# from polls_app.core.models import AnswerModel, CommentModel, QuestionModel
#
# UserModel = get_user_model()
#
#
# class CoreViewsTests(APITestCase):
#
#     def setUp(self):
#         self.user = UserModel.objects.create_user(email="test@email.com", username='testuser', password='testpassword')
#         self.user.is_active = True
#         self.user.save()
#         self.client.login(username='testuser', password='testpassword')
#
#         self.question = QuestionModel.objects.create(
#             owner=self.user,
#             question_type='text',
#             question_text='Sample Question',
#             is_active=True
#         )
#
#         self.answer = AnswerModel.objects.create(
#             question=self.question,
#             answer_text='Sample Answer',
#             votes=0
#         )
#
#         self.comment = CommentModel.objects.create(
#             question=self.question,
#             comment_text='Sample Comment'
#         )
#
#         self.url = reverse('question-detail', args=[self.question.id])
#         self.data = {
#             "question_type": "text",
#             "question_text": "Updated Question",
#             "is_active": True,
#             "answers": [
#                 {
#                     "pk": self.answer.id,
#                     "answer_text": "Updated Answer",
#                     "votes": 5
#                 }
#             ],
#             "comments": [
#                 {
#                     "pk": self.comment.id,
#                     "comment_text": "Updated Comment"
#                 }
#             ]
#         }
#
#     def test_update_question(self):
#         response = self.client.put(self.url, self.data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         self.question.refresh_from_db()
#         self.answer.refresh_from_db()
#         self.comment.refresh_from_db()
#
#         self.assertEqual(self.question.question_text, "Updated Question")
#         self.assertEqual(self.answer.answer_text, "Updated Answer")
#         self.assertEqual(self.answer.votes, 5)
#         self.assertEqual(self.comment.comment_text, "Updated Comment")
#
#     def test_update_question_with_existing_answer_pk(self):
#         new_answer = AnswerModel.objects.create(
#             question=self.question,
#             answer_text='New Answer',
#             votes=0
#         )
#         new_data = {
#             "question_type": "text",
#             "question_text": "Updated Question Again",
#             "is_active": True,
#             "answers": [
#                 {
#                     "pk": new_answer.id,
#                     "answer_text": "New Answer Updated",
#                     "votes": 10
#                 }
#             ],
#             "comments": [
#                 {
#                     "pk": self.comment.id,
#                     "comment_text": "Updated Comment Again"
#                 }
#             ]
#         }
#         response = self.client.put(self.url, new_data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         new_answer.refresh_from_db()
#         self.assertEqual(new_answer.answer_text, "New Answer Updated")
#         self.assertEqual(new_answer.votes, 10)
#
#     def test_update_question_with_duplicate_answer_pk(self):
#         duplicate_data = {
#             "question_type": "text",
#             "question_text": "Updated Question Again",
#             "is_active": True,
#             "answers": [
#                 {
#                     "pk": self.answer.id,
#                     "answer_text": "Updated Answer",
#                     "votes": 5
#                 },
#                 {
#                     "pk": self.answer.id,
#                     "answer_text": "Duplicate Answer",
#                     "votes": 10
#                 }
#             ],
#             "comments": [
#                 {
#                     "pk": self.comment.id,
#                     "comment_text": "Updated Comment Again"
#                 }
#             ]
#         }
#         response = self.client.put(self.url, duplicate_data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
#         self.assertEqual(response.data['error'],
#                          "Answer with this Primary key already exists. No pk should be provided when creating new answer.")
