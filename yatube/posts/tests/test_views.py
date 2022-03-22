import shutil
import tempfile
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Тест',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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
            post.image: "posts/small.gif",
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


class CommentsViewsTests(TestCase):
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
        self.user = CommentsViewsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment_for_guest(self):
        post = CommentsViewsTests.post

        response = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': post.id
                }
            )
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_add_comment_for_auth_user(self):

        post = CommentsViewsTests.post

        comments_count = Comment.objects.filter(
            post=post.id
        ).count()
        form_data = {
            'text': 'Тестовый комментарий',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={
                        'post_id': post.id
                    }
                    ),
            data=form_data,
            follow=True
        )
        comments = Post.objects.filter(
            id=post.id
        ).values_list('comments', flat=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': post.id
                }
            )
        )
        self.assertEqual(
            comments.count(),
            comments_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                post=post.id,
                text=form_data['text']
            ).exists()
        )


class CacheViewsTest(TestCase):
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
            text='Тестовое сообщение',
            group=cls.group,
            author=cls.user
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_cache_index(self):
        response = CacheViewsTest.authorized_client.get(reverse('posts:index'))
        posts = response.content

        Post.objects.create(
            text='Новое тестовое сообщение',
            author=CacheViewsTest.user,
        )
        response_old = CacheViewsTest.authorized_client.get(
            reverse('posts:index')
        )
        old_posts = response_old.content
        self.assertEqual(
            old_posts,
            posts,
            'Страница не кешируется'
        )
        cache.clear()
        response_new = CacheViewsTest.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, 'Кеш не обновляется')
