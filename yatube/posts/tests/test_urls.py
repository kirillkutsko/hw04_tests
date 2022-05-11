from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_for_authorized_client(self):
        """
        Доступность url адресов для авторизованного пользователя
        """
        test_urls = (
            '/',
            '/group/test_slug/',
            '/profile/auth/',
            f'/posts/{self.post.id}/',
            '/create/'
        )
        for url in test_urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_for_author_exists(self):
        """
        Cтраница редактирования поста доступна только автору
        """
        testing_url = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(testing_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_posts', kwargs={'slug': 'test_slug'}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': f'{self.user}'}),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': f'{self.post.id}'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_user(self):
        """URL-адрес использует соответствующий шаблон для auth_users"""
        templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_page(self):
        """
        Запрос к несуществующей странице
        """
        response = self.guest_client.get('/unknown/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """
        Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_1post_create_url_redirect_anonymous_on_admin_login(self):
        """
        Страница по адресу /edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
