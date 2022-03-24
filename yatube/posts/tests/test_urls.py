from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            first_name='Имя',
            last_name='Фамилия',
            username='test_user',
            email='test@test.ru'
        )
        cls.user_2 = User.objects.create(
            username='test_user_2'
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
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_2 = PostURLTests.user_2
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_urls_uses_correct_template(self):
        user = PostURLTests.user
        group = PostURLTests.group
        post = PostURLTests.post

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{group.slug}/',
            'posts/profile.html': f'/profile/{user.username}/',
            'posts/post_detail.html': f'/posts/{post.id}/',
            'posts/create_post.html': f'/posts/{post.id}/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url(self):
        group = PostURLTests.group
        user = PostURLTests.user
        post = PostURLTests.post

        response_index = self.guest_client.get('/')
        response_group = self.guest_client.get(f'/group/{group.slug}/')
        response_profile = self.guest_client.get(f'/profile/{user.username}/')
        response_post = self.guest_client.get(f'/posts/{post.id}/')
        response_post_edit = self.authorized_client.get(
            f'/posts/{post.id}/edit/'
        )

        response_follow_index = self.authorized_client_2.get('/follow/')
        response_follow = self.authorized_client_2.get(
            f'/profile/{user.username}/follow/'
        )
        response_unfollow = self.authorized_client_2.get(
            f'/profile/{user.username}/unfollow/'
        )

        response_404 = self.guest_client.get('/notexistant_page/')

        test_dict = {
            response_index.status_code: 200,
            response_group.status_code: 200,
            response_profile.status_code: 200,
            response_post.status_code: 200,
            response_post_edit.status_code: 200,

            response_follow_index.status_code: 200,
            response_follow.status_code: 302,
            response_unfollow.status_code: 302,

            response_404.status_code: 404,
        }

        for value, expected in test_dict.items():
            with self.subTest(value=value):
                self.assertEquals(value, expected)
