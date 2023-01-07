from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        User.objects.create_user(username='auth')

    def test_create_user(self):
        '''Проверка создания юзера'''

        count_old_users = User.objects.all().count()

        User.objects.create_user(username='new_auth')
        count_new_users = User.objects.all().count()

        self.assertEqual(count_old_users + 1, count_new_users)
