import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Создаем тестовые посты, группу и форму."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='first',
            description='Тестовый заголовок'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Старый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostFormTests.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.group, PostFormTests.group
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostFormTests.user)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Измененный пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk}
        ))
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )
