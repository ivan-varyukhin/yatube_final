import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsPostCreateTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = FormsPostCreateTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        group_pk = FormsPostCreateTests.group.pk
        user = FormsPostCreateTests.user
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'New',
            'group': group_pk,
            'image': uploaded,
        }
        self.assertEquals(Post.objects.count(), posts_count)
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEquals(Post.objects.count(), posts_count + 1)
        new_post = Post.objects.filter(
            text='New',
            group=group_pk,
            image='posts/small.gif'
        )
        self.assertTrue(new_post.exists())
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': user.username}
        ))

    def test_edit_post(self):
        new_group = Group.objects.create(
            title='Тестовое название группы 2',
            description='Тестовое писание группы',
            slug='test-slug-2'
        )

        post = Post.objects.create(
            text='Тест ',
            author=FormsPostCreateTests.user,
            group=FormsPostCreateTests.group,
        )

        form_new_data = {
            'text': 'Тест 2',
            'group': new_group.pk
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_new_data,
            follow=True
        )

        post.refresh_from_db()
        self.assertEquals(post.text, 'Тест 2')
        self.assertEquals(post.group, new_group)
