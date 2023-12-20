from django.test import TestCase

from aiarena.core.tests.test_mixins import LoggedInMixin


class AdminViewsTestCase(LoggedInMixin, TestCase):
    """
    Test that all expected core models have an admin endpoint.
    """

    MODELS_WITH_NO_EXPECTED_ENDPOINT = ["RelativeResult"]  # add models that don't need to have an admin endpoint

    def setUp(self):
        super().setUp()
        self.client.login(username="staff_user", password="x")

    def test_all_core_admin_endpoints(self):
        endpoints = self.__get_endpoints_to_test()
        for endpoint in endpoints:
            self.__test_admin_core_endpoint(endpoint)

    def __get_endpoints_to_test(self) -> list:
        core_models = self.__get_all_core_models()
        return self.__remove_models_with_no_endpoint(core_models)

    def __remove_models_with_no_endpoint(self, core_models):
        # .lower() is required because the admin endpoint is lowercase
        endpoints = [
            model.lower() for model in core_models if model not in AdminViewsTestCase.MODELS_WITH_NO_EXPECTED_ENDPOINT
        ]
        return endpoints

    def __get_all_core_models(self):
        from aiarena.core.models import __all__ as core_models

        return core_models

    def __test_admin_core_endpoint(self, endpoint: str):
        response = self.client.get(f"/admin/core/{endpoint}/")
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200 for /admin/core/{endpoint}/, got {response.status_code}")
