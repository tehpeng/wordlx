import json

from django.test import TestCase
from django.urls import reverse


def register(tester, username="dave", password="password", email="dave@davemail.com"):
    body = {"username": username, "password": password, "email": email}
    return tester.client.post(
        reverse("game:register"), body, content_type="application/json"
    )


def login(tester, username="dave", password="password"):
    body = {"username": username, "password": password}
    return tester.client.post(
        reverse("game:auth"), body, content_type="application/json"
    )


# def init(tester, username="dave", password="password", is_public=False):
#     register(tester, username=username, password=password)
#     login(tester, username=username, password=password)
#     body = {"is_public":is_public}
#     return tester.client.post(reverse("game:register", body, format="json"))


class RegisterTest(TestCase):
    def test_regis(self):

        response = register(self)
        self.assertContains(response, "user created. username: dave")

    def test_regis_duplicate(self):
        register(self)
        response = register(self)
        self.assertContains(response, "try another username")


class LoginTest(TestCase):
    def test_login_succesful(self):
        register(self)
        response = login(self)
        self.assertContains(response, "login succesful.")

    def test_login_unsuccesful(self):
        register(self)
        response = login(self, username="kevin")
        self.assertContains(response, "login unsuccesful")
        response = login(self, password="kevin")
        self.assertContains(response, "login unsuccesful")


# class InitTest(TestCase):
#     def test_init_succesful(self):
#         register(self)
#         login(self)
#         response = init(self)
#         self.assertContains(response, "login unsuccesful.")
