"""
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging

from tornado import testing
from tornado.httpclient import HTTPError, AsyncHTTPClient


class AuthTests(testing.AsyncTestCase):

    _multiprocess_can_split_ = True

    @testing.gen_test
    def auth_providers_test(self):
        logging.debug("Start auth_providers_test")

        response = yield AsyncHTTPClient(self.io_loop).fetch("http://localhost/api/v1/auth/providers")
        auth_providers = json.loads(response.body)
        self.assertTrue(len(auth_providers.keys()) >= 1, "No auth methods enabled %s" % auth_providers)

        if "password" in auth_providers:
            self.assertTrue(
                "regex" in auth_providers["password"],
                "Missing property 'regex' in auth password method %s" % auth_providers
            )

        logging.debug("Completed auth_providers_test")

    @testing.gen_test
    def signup_disabled_test(self):
        logging.debug("Start signup_disabled_test")

        error = None
        try:
            yield AsyncHTTPClient(self.io_loop).fetch(
                "http://localhost/api/v1/auth/signup",
                method="POST",
                body=json.dumps({})
            )
        except HTTPError as http_error:
            error = http_error

        self.assertIsNotNone(error, "No error raised calling /api/v1/auth/signup")
        self.assertEquals(error.code, 403, "/api/v1/auth/signup raised %d instead of 403" % error.code)

        logging.debug("Completed signup_disabled_test")

    @testing.gen_test
    def login_success_test(self):
        logging.debug("Start login_success_test")

        response = yield AsyncHTTPClient(self.io_loop).fetch(
            "http://localhost/api/v1/auth/login",
            method='POST',
            body=json.dumps(dict(username="operations@elasticbox.com", password="elastickube123")))

        self.assertTrue(response.body, "Token not included in response body")
        logging.debug("Completed login_success_test")

    @testing.gen_test
    def login_wrong_password_test(self):
        logging.debug("Start login_wrong_password_test")

        error = None
        try:
            yield AsyncHTTPClient(self.io_loop).fetch(
                "http://localhost/api/v1/auth/login",
                method='POST',
                body=json.dumps(dict(username="operations@elasticbox.com", password="elastickube2")))
        except HTTPError as http_error:
            error = http_error

        self.assertIsNotNone(error, "No error raised calling /api/v1/auth/login")
        self.assertEquals(error.code, 401, "/api/v1/auth/login raised %d instead of 401" % error.code)

        logging.debug("Completed login_wrong_password_test")


if __name__ == '__main__':
    testing.main()
