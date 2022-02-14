from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.author.username}/':
                'posts/profile.html',
            f'/posts/{self.post.pk}/edit/':
                'posts/create_post.html',
            f'/posts/{self.post.pk}/':
                'posts/post_detail.html',
            f'/group/{self.group.slug}/':
                'posts/group_list.html',
            '/create/': 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_access_page(self):
        """Страницы доступны."""
        # открытые страницы
        pages_for_all = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author.username}/',
            f'/posts/{self.post.pk}/',
        )
        for address in pages_for_all:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # только авторизованному
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # только автору
        response = self.authorized_author.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_404(self):
        """Несуществующая страница отвечает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
