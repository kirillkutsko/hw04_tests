from posts.forms import PostForm
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Kirill')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Текст поста',
            'group': Group.objects.get(slug="test-slug").id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username])
        )

        self.assertEqual(Post.objects.count(), posts_count+1)

        self.assertTrue(
            Post.objects.filter(
                text='Текст поста',
                author=self.user,
                group=Group.objects.get(slug="test-slug")
            ).exists()
        )
