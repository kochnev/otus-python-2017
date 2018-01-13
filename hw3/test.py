# -*- coding: utf-8 -*-

import unittest
import api


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

        self.online_score_request = {
            "account": "user", "login": "user", "method": "online_score",
            "token":
            "aa34e991ff440298f58c8021c8ce0d337fdc01e75488f6fbae94a16e7c8c2ed49514e8da4df2ec398bcdd67ca5bd9a3600d2b09c698a27c6e0a2dad8eee9a634",
            "arguments": {"phone": "79175002040", "email": "ivanov@otus.ru",
                          "first_name": "Ivanov", "last_name": "Иванов",
                          "birthday": "01.01.1990", "gender": 1}
        }

        self.client_interests_request = {
            "account": "user", "login": "user", "method": "clients_interests",
            "token":
            "aa34e991ff440298f58c8021c8ce0d337fdc01e75488f6fbae94a16e7c8c2ed49514e8da4df2ec398bcdd67ca5bd9a3600d2b09c698a27c6e0a2dad8eee9a634",
            "arguments": {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}
        }

    def get_response(self, request):
            return api.method_handler({
                                   "body": request,
                                   "headers": self.headers
                                  },
                                  self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_correct_online_score_request(self):
        response, code = self.get_response(self.online_score_request)
        self.assertEqual(api.OK, code)
        self.assertEqual(int(response["score"]), 5)

    def test_correct_client_interests_request(self):
        response, code = self.get_response(self.client_interests_request)
        self.assertEqual(api.OK, code)
    
    def test_char_field(self):
        r = self.online_score_request.copy()
        r["account"] = 100
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertIn("must be string", response)

    def test_arguments_field(self):
        r = self.online_score_request.copy()
        r["arguments"] = 100
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertIn("must be dictionary", response)

    def test_email_field(self):
        r = self.online_score_request.copy()
        r["arguments"]["email"] = "hello"
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertIn("email", response)

    def test_phone_field_short_number(self):
        r = self.online_score_request.copy()
        r["arguments"]["phone"] = 123
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_phone_field_not_digit(self):
        r = self.online_score_request.copy()
        r["arguments"]["phone"] = "123"
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_phone_field_wrong_format(self):
        r = self.online_score_request.copy()
        r["arguments"]["phone"] = 49153215544
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_date_field(self):
        r = self.client_interests_request.copy()
        r["arguments"]["date"] = "0101988"
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_birthday_field(self):
        r = self.online_score_request.copy()
        r["arguments"]["birthday"] = "0101988"
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_gender_field(self):
        r = self.online_score_request.copy()
        r["arguments"]["gender"] = 3
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_client_ids_field(self):
        r = self.client_interests_request.copy()
        r["arguments"]["client_ids"] = {}
        response, code = self.get_response(r)
        self.assertEqual(api.INVALID_REQUEST, code)


if __name__ == "__main__":
    unittest.main()
