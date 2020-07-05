from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from learning import views

class TestUrls(SimpleTestCase):

    def test_template_view_url(self):
        resolver = resolve(reverse('learning'))
        self.assertEqual(resolver.func.view_class, views.Learning)

    def test_manage_models_url(self):
        resolver = resolve(reverse('models'))
        self.assertEqual(resolver.func.view_class, views.LearningModels)
