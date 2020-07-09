from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from learning import views

class TestUrls(SimpleTestCase):

    def test_template_view_url(self):
        resolver = resolve(reverse('learning'))
        self.assertEqual(resolver.func.view_class, views.Learning)

    def test_manage_models_url(self):
        resolver = resolve(reverse('learning-models'))
        self.assertEqual(resolver.func.view_class, views.LearningModels)

    def test_manage_files_url(self):
        resolver = resolve(reverse('learning-files'))
        self.assertEqual(resolver.func.view_class, views.LearningFiles)

    def test_members_completed_url(self):
        resolver = resolve(reverse('members-completed'))
        self.assertEqual(resolver.func.view_class, views.MembersCompleted)
