from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.true_group = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """
        Проверить правильность контекста у постов на страницах:
        posts:index,
        posts:group_posts,
        posts:profile.
        """
        fixture_page = [
            (self.post, reverse('posts:index')),
            (self.post, reverse(
                'posts:group_posts', args=[self.group.slug])),
            (self.post, reverse(
                'posts:profile', args=[self.user.username])),
        ]
        for fixture, page in fixture_page:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertIn(fixture, response.context['page_obj'])

    def test_template_pages_show_correct_context(self):
        """
        Проверить правильность контекста у шаблонов posts:group_posts,
        posts:profile.
        """
        fixture_context = [
            (self.group, 'group', reverse(
                'posts:group_posts', args=[self.group.slug])),
            (self.user, 'author', reverse(
                'posts:profile', args=[self.user.username])),
            (self.post, 'post', reverse(
                'posts:post_detail', args=[self.post.id])),
        ]
        for fixture, context, address in fixture_context:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(fixture, response.context[context])

    def test_post_in_true_group(self):
        """
        Проверить правильность группы у поста.
        """
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    args=[self.true_group.slug]))
        self.assertNotIn(self.post, response.context['page_obj'])
