from .utils import APITestCase, CreateMailTemplateMixin, ignore_external
from ..factories import UserFactory
from ..mails import EmailConfirm
from ..utils import random_key
from ..models import User


@ignore_external
class SigninTestCase(APITestCase):
    PATH = 'signin/'

    def test_valid(self):
        user = UserFactory(email_confirmed=True)
        response = self.client.post(self.PATH, {
            'email': user.email,
            'password': user._password,
        })
        print(response.json())
        assert response.status_code == 200

    def test_invalid(self):
        user = UserFactory(email_confirmed=True)
        response = self.client.post(self.PATH, {
            'email': user.email,
            'password': user._password + '123',
        })
        assert response.status_code == 400

    def test_unconfirmed(self):
        user = UserFactory(email_confirmed=False)
        response = self.client.post(self.PATH, {
            'email': user.email,
            'password': user._password,
        })
        assert response.status_code == 423


@ignore_external
class LogoutTestCase(APITestCase):
    PATH = 'logout/'

    def test_logout(self):
        user = UserFactory()
        self.login(user)
        response = self.client.post(self.PATH)
        assert response.status_code == 204
        self.logout()


@ignore_external
class SignupTestCase(CreateMailTemplateMixin, APITestCase):
    PATH = 'signup/'

    @classmethod
    def setUpTestData(cls):
        cls.create_mail_template(EmailConfirm)

    def test_singup(self):
        password = random_key()
        response = self.client.post(self.PATH, {
            'email': 'test@example.com',
            'first_name': 'First',
            'last_name': 'Last',
            'password': password,
        })
        assert response.status_code == 202
        user = User.objects.get()
        assert user.is_active
        assert user.check_password(password)
        assert not user.email_confirmed
        assert user.email_confirm_code is not None

    def test_duplicate(self):
        user = UserFactory()
        response = self.client.post(self.PATH, {
            'email': user.email,
            'first_name': 'John',
            'last_name': 'Doe',
            'password': '123123',
        })
        assert response.status_code == 400

    def test_uppercase(self):
        user = UserFactory()
        response = self.client.post(self.PATH, {
            'email': user.email.capitalize(),
            'first_name': 'John',
            'last_name': 'Doe',
            'password': '12345',
        })
        assert response.status_code == 400
