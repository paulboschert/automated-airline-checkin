#!/usr/bin/env python3
import unittest
from Calculator import Calculator
from unittest.mock import MagicMock

from pytest_mock import MockerFixture
from requests_mock.mocker import Mocker as RequestMocker

class TestSystem(unittest.TestCase):
    def setUp(self):

    def test_add(self):
        add_result = self.calculator.add(1, 2)
        self.assertEqual(add_result, 3)

    def test_subtract(self):
        subtract_result = self.calculator.subtract(1, 1)
        self.assertEqual(subtract_result, 0)

    def test_currency_converter(self):
        conversion_result = self.calculator.usd_to_gbp(10)
        self.assertEqual(conversion_result, 8.2)

    def test_request(requests_mock: RequestMocker) -> None:
        mock_post = requests_mock.get(
            utils.BASE_URL + "test", status_code=200, text='{"success": "get"}'
        )

        response = utils.make_request("GET", "test", {"header": "test"}, {"test": "params"})

        assert response == {"success": "get"}
    
        last_request = mock_post.last_request
        assert last_request.method == "GET"
        assert last_request.url == utils.BASE_URL + "test?test=params"
        assert last_request.headers["header"] == "test"


if __name__ == '__main__':
    unittest.main()

