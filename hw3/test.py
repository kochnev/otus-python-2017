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
            "token": "aa34e991ff440298f58c8021c8ce0d337fdc01e75488f6fbae94a16e\
            7c8c2ed49514e8da4df2ec398bcdd67ca5bd9a3600d2b09c698a27c6e0a2dad8ee\
            e9a634",
            "arguments": {"phone": "79175002040", "email": "ivanov@otus.ru",
                          "first_name": "Ivanov", "last_name": "Иванов",
                          "birthday": "01.01.1990", "gender": 1}
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

    def test_charfield(self):
        self.online_score_request["account"] = 100
        response, code = self.get_response(self.online_score_request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertIn("must be string", response)



if __name__ == "__main__":
    unittest.main()
