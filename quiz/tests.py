import json

from django.test import TestCase
from django.urls import reverse

from authentication.models import User

from .models import Quiz, QuizAnswerOption, QuizAttempt, QuizCategory, QuizQuestion


class QuizBaseTestCase(TestCase):
    def setUp(self):
        self.category = QuizCategory.objects.create(
            name='Din Test',
            slug='din-test',
            is_active=True,
        )
        self.quiz = Quiz.objects.create(
            category=self.category,
            title='Temel Bilgiler',
            slug='temel-bilgiler',
            description='Acilan quiz',
            difficulty='easy',
            subcategory='Akaid',
            thumbnail='https://example.com/quiz.jpg',
            time_limit=45,
            passing_score=80,
            is_active=True,
        )
        QuizQuestion.objects.create(
            quiz=self.quiz,
            question='Ilk soru',
            options=['A', 'B', 'C', 'D'],
            correct_answer=1,
            display_order=0,
            is_active=True,
        )
        QuizQuestion.objects.create(
            quiz=self.quiz,
            question='Ikinci soru',
            options=['Dogru', 'Yanlis'],
            correct_answer=0,
            display_order=1,
            is_active=True,
        )


class QuizApiTests(QuizBaseTestCase):
    def test_quizzes_api_returns_structure(self):
        response = self.client.get(reverse('quiz:quizzes_api'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('quizzes', payload)
        self.assertIsInstance(payload['quizzes'], list)
        self.assertEqual(len(payload['quizzes']), 1)

        first_quiz = payload['quizzes'][0]
        self.assertIn('id', first_quiz)
        self.assertIn('category', first_quiz)
        self.assertIn('questions', first_quiz)
        self.assertIsInstance(first_quiz['questions'], list)


class QuizModelSerializationTests(QuizBaseTestCase):
    def test_api_uses_admin_managed_models(self):
        response = self.client.get(reverse('quiz:quizzes_api'))
        payload = response.json()
        created_quiz = next(item for item in payload['quizzes'] if item['id'] == 'temel-bilgiler')

        self.assertEqual(created_quiz['category'], 'Din Test')
        self.assertEqual(created_quiz['subcategory'], 'Akaid')
        self.assertEqual(created_quiz['timeLimit'], 45)
        self.assertEqual(created_quiz['questions'][0]['correctAnswer'], 1)

    def test_api_serializes_image_answer_question_types(self):
        image_question = QuizQuestion.objects.create(
            quiz=self.quiz,
            question_type=QuizQuestion.TYPE_TEXT_QUESTION_IMAGE_ANSWERS,
            question='Gorselden dogru secenegi bul',
            options=[],
            correct_answer=0,
            display_order=2,
            is_active=True,
        )
        QuizAnswerOption.objects.create(
            question=image_question,
            image='https://example.com/answer-1.jpg',
            image_alt='Birinci cevap',
            is_correct=False,
            display_order=0,
            is_active=True,
        )
        QuizAnswerOption.objects.create(
            question=image_question,
            image='https://example.com/answer-2.jpg',
            image_alt='Ikinci cevap',
            is_correct=True,
            display_order=1,
            is_active=True,
        )

        response = self.client.get(reverse('quiz:quizzes_api'))
        payload = response.json()
        created_quiz = next(item for item in payload['quizzes'] if item['id'] == 'temel-bilgiler')
        serialized_question = next(
            question for question in created_quiz['questions']
            if question['question'] == 'Gorselden dogru secenegi bul'
        )

        self.assertEqual(serialized_question['questionType'], QuizQuestion.TYPE_TEXT_QUESTION_IMAGE_ANSWERS)
        self.assertEqual(serialized_question['correctAnswer'], 1)
        self.assertEqual(serialized_question['options'][1]['image'], 'https://example.com/answer-2.jpg')


class QuizAttemptApiTests(QuizBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='test1234',
        )

    def test_submit_attempt_persists_result(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('quiz:submit_quiz_attempt'),
            data=json.dumps({
                'quiz_id': self.quiz.slug,
                'answers': [1, 0],
                'elapsed_seconds': 18,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(QuizAttempt.objects.count(), 1)

        attempt = QuizAttempt.objects.get()
        self.assertEqual(attempt.correct_count, 2)
        self.assertEqual(attempt.percentage, 100)
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.answers.count(), 2)

    def test_submit_attempt_snapshots_image_answer_data(self):
        image_quiz = Quiz.objects.create(
            category=self.category,
            title='Gorselli Quiz',
            slug='gorselli-quiz',
            description='Gorselli cevaplar',
            difficulty='medium',
            time_limit=30,
            passing_score=50,
            is_active=True,
        )
        image_question = QuizQuestion.objects.create(
            quiz=image_quiz,
            question_type=QuizQuestion.TYPE_TEXT_QUESTION_IMAGE_ANSWERS,
            question='Dogru gorseli sec',
            options=[],
            correct_answer=0,
            display_order=0,
            is_active=True,
        )
        QuizAnswerOption.objects.create(
            question=image_question,
            image='https://example.com/wrong.jpg',
            image_alt='Yanlis cevap',
            is_correct=False,
            display_order=0,
            is_active=True,
        )
        QuizAnswerOption.objects.create(
            question=image_question,
            image='https://example.com/correct.jpg',
            image_alt='Dogru cevap',
            is_correct=True,
            display_order=1,
            is_active=True,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse('quiz:submit_quiz_attempt'),
            data=json.dumps({
                'quiz_id': image_quiz.slug,
                'answers': [1],
                'elapsed_seconds': 9,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        answer = QuizAttempt.objects.get(quiz=image_quiz).answers.get()
        self.assertEqual(answer.selected_answer_image, 'https://example.com/correct.jpg')
        self.assertEqual(answer.correct_answer_image, 'https://example.com/correct.jpg')
