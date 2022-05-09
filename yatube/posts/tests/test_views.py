from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')


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
        )
        cls.true_group = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )

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
