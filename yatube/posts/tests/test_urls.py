from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост п',
        )

    def setUp(self):
        self.guest_client = Client()
        PostModelTest.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_for_authorized_client(self):
        """Доступность url адресов для
        авторизованного пользователя"""
        test_urls = (
            '/',
            '/group/test_slug/',
            '/profile/HasNoName/',
            f'/posts/{self.post.id}/',
            '/create/'
        )
        for url in test_urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
