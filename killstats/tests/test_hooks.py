from django.test import TestCase

from killstats.hooks import get_extension_logger


class TestTemplateTags(TestCase):
    def test_logger_fail(self):
        with self.assertRaises(TypeError):
            get_extension_logger(1234)
