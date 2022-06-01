from django.contrib.auth import get_user_model
from django.test import TestCase

from ads.models import Ad, Comment, Fav


class AdModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test@email.com',
            password='secret'
        )
        Ad.objects.create(title='just a test', text='Ehy', owner=self.user)

    def test_string_representation(self):
        ad = Ad.objects.get(id=1)
        self.assertEqual(str(ad), ad.title)
        
    def test_title_content(self):
        ad = Ad.objects.get(id=1)
        expected_object_title = f'{ad.title}'
        self.assertEqual(expected_object_title, 'just a test')
        self.assertEqual(str(ad), ad.title)

    def test_text_content(self):
        ad = Ad.objects.get(id=1)
        expected_object_text = f'{ad.text}'
        self.assertEqual(expected_object_text, 'Ehy')

    def test_owner(self):
        ad = Ad.objects.get(id=1)
        expected_object_owner = ad.owner
        self.assertEqual(expected_object_owner, self.user)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test@email.com',
            password='secret'
        )
        ad = Ad.objects.create(title='just a test', text='Ehy', owner=self.user)
        Comment.objects.create(text='a comment', ad=ad, owner=self.user)

    def test_title_content(self):
        comment = Comment.objects.get(id=1)
        expected_object_text = f'{comment.text}'
        self.assertEqual(expected_object_text, 'a comment')

    def test_comment_owner(self):
        comment = Comment.objects.get(id=1)
        expected_object_owner = comment.owner
        self.assertEqual(expected_object_owner, self.user)

    def test_comment_belongs_to_ad_by_ad_title(self):
        comment = Comment.objects.get(id=1)
        expected_object_ad_title = f'{comment.ad.title}'
        self.assertEqual(expected_object_ad_title, 'just a test')


class FavModelTest(TestCase):
    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test_user',
            email='test@email.com',
            password='secret'
        )
        ad = Ad.objects.create(title='just a test', text='Ehy', owner=self.sample_user)
        Fav.objects.create(ad=ad, user=self.sample_user)

    def test_favorite_owner(self):
        favorite = Fav.objects.get(id=1)
        expected_object_owner = favorite.user
        self.assertEqual(expected_object_owner, self.sample_user)

    def test_comment_belongs_to_ad_by_ad_title(self):
        favorite = Fav.objects.get(id=1)
        expected_object_ad_title = f'{favorite.ad.title}'
        self.assertEqual(expected_object_ad_title, 'just a test')
        