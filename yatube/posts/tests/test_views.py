from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POST_PER_PAGE

from ..models import Group, Post

User = get_user_model()
FIRST_PAGE_POSTS = 13
SECOND_PAGE_POSTS = 3


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
            with self.subTest(fixture=fixture):
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


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )

    def setUp(self):
        for post_temp in range(FIRST_PAGE_POSTS):
            Post.objects.create(
                text=f'text{post_temp}', author=self.author, group=self.group
            )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_posts.html':
                reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.author}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), POST_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index') + '?page=2',
            'posts/group_posts.html':
                reverse('posts:group_posts',
                        kwargs={'slug': self.group.slug}) + '?page=2',
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.author}) + '?page=2',
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(
                    response.context['page_obj']), SECOND_PAGE_POSTS
                )
