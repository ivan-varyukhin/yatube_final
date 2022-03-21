from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        expected_post_name = post.text[:30]
        post_verbose_name = post._meta.get_field('text').verbose_name
        post_help_text = post._meta.get_field('text').help_text
        texts = {
            expected_post_name: str(post),
            post_verbose_name: 'Текст',
            post_help_text: 'Текст сообщения',
        }

        for value, expected in texts.items():
            with self.subTest(value=value):
                self.assertEquals(value, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        post = GroupModelTest.post
        group = GroupModelTest.group
        expected_group_name = group.title
        group_verbose_name = post._meta.get_field('group').verbose_name
        group_help_text = post._meta.get_field('group').help_text
        texts = {
            expected_group_name: str(group),
            group_verbose_name: 'Группа',
            group_help_text: 'Группа',
        }

        for value, expected in texts.items():
            with self.subTest(value=value):
                self.assertEquals(value, expected)
