import unittest

from app.routers.tasks import router


class RouteOrderTests(unittest.TestCase):
    def test_output_compare_precedes_dynamic_output_route(self):
        paths = [route.path for route in router.routes]

        self.assertLess(
            paths.index("/outputs/compare"),
            paths.index("/outputs/{output_id}"),
        )


if __name__ == "__main__":
    unittest.main()
