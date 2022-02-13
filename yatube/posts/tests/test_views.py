from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group


User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_author")
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_pages_obj = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.user: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        first_post = response.context.get('page_obj')[0]
        self.assertEqual(first_post, self.post)
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(response.context['group'], self.post.group)

    def test_profile_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_pk = response.context['post'].pk
        self.assertEqual(post_pk, self.post.pk)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_new_post(self):
        """Проверка что пост появляется на главной странице,
        на странице выбранной группы и в профайле пользователя."""

        post = Post.objects.create(
            author=self.user,
            text=self.post.text,
            group=self.group
        )
        for page in self.templates_pages_obj:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(
                    post, response.context['page_obj']
                )

    def test_post_new_not_in_group(self):
        """Проверка поста в другой группе."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='posts_author',
        )
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='Тестовое описание группы',
        )
        cls.post = [
            Post.objects.create(
                text='Пост №' + str(i),
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group
            )
            for i in range(13)]

    def test_index_page_contains_ten_records(self):

        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
