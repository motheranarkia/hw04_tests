from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованный клиент
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # авторизованный клиент автор
        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        # авторизованный клиент не-автор
        cls.non_author = User.objects.create_user(username='test_non_author')
        cls.authorized_non_author_client = Client()
        cls.authorized_non_author_client.force_login(cls.non_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
        }

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in PostURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_urls_guest(self):
        """Страницы, доступные для неавторизованного клиента"""
        urls = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
        }
        for adress, expected in urls.items():
            with self.subTest(adress=adress):
                response = PostURLTests.guest_client.get(
                    adress
                )
                self.assertEqual(response.status_code, expected)

    def test_urls(self):
        """Страницы, доступные для авторизованного клиента"""
        urls = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
            '/create/',
            f'/posts/{self.post.id}/edit/',
        }
        for adress in urls:
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_page_404(self):
        """Несуществующая страница отвечает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_edit_post(self):
        """Автор может редактировать свою запись"""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}
                    ), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_author_can_not_edit_post(self):
        """Не-автор не может редактировать запись"""
        response = self.authorized_non_author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}
                    ), follow=True)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.non_author}))
