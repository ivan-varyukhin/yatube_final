from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            first_name='Имя',
            last_name='Фамилия',
            username='test_user',
            email='test@test.ru'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовое писание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тест',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post(self, post, user, group):
        post_test_dict = {
            post.text: post.text,
            post.author.get_full_name(): user.get_full_name(),
            post.group.title: group.title,
        }
        for value, expected in post_test_dict.items():
            with self.subTest(value=value):
                self.assertEquals(value, expected)

    def test_pages_uses_correct_template(self):
        user = PostPagesTests.user
        group = PostPagesTests.group
        post = PostPagesTests.post

        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        user = PostPagesTests.user
        group = PostPagesTests.group

        response = self.authorized_client.get(reverse('posts:index'))

        post_0 = response.context['page_obj'][0]
        self.check_post(post_0, user, group)

    def test_group_show_correct_context(self):
        user = PostPagesTests.user
        group = PostPagesTests.group

        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': group.slug}
        ))

        self.assertEquals(response.context['group'].title, group.title)
        self.assertEquals(response.context['group'].description,
                          group.description)

        post_0 = response.context['page_obj'][0]
        self.check_post(post_0, user, group)

    def test_profile_show_correct_context(self):
        user = PostPagesTests.user
        group = PostPagesTests.group

        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': user.username}
        ))

        post_0 = response.context['page_obj'][0]
        self.check_post(post_0, user, group)

    def test_post_detail_show_correct_context(self):

        user = PostPagesTests.user
        post = PostPagesTests.post
        group = PostPagesTests.group

        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        ))

        post = response.context['post']
        self.check_post(post, user, group)

    def test_post_edit_show_correct_context(self):

        post = PostPagesTests.post

        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': post.id}
        ))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):

        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            first_name='Имя',
            last_name='Фамилия',
            username='test_user',
            email='test@test.ru'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовое писание группы',
            slug='test-slug'
        )
        for i in range(0, 13):
            Post.objects.create(
                text=f'{i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_contains_ten_records(self):
        group = PaginatorViewsTest.group
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': group.slug}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        group = PaginatorViewsTest.group
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        user = PaginatorViewsTest.user
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': user.username}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        user = PaginatorViewsTest.user
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': user.username}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
