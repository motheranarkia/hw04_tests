from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.non_author = User.objects.create_user(username='test_non_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_non_author = Client()
        self.authorized_non_author.force_login(self.non_author)

    def test_create_post(self):
        """при отправке валидной формы создаётся новая запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_edit_post(self):
        """при отправке валидной формы происходит изменение поста."""
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group.id, form_data['group'])

    def test_guest_can_not_create_new_post(self):
        """неавторизованный клиент перенаправляется на страницу
        авторизации"""
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:create_post'),
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(posts_count, Post.objects.count())

    def test_user_can_not_edit_post(self):
        """пользователь не может редактировать чужой пост"""
        form_data = {
            'text': 'Измененный тестовый пост',
        }
        response = self.authorized_non_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.non_author})
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            PostFormFormTests.post.text
        )
