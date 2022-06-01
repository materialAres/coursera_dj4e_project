from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from ads.models import Ad


class ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_'
                     'user',
            email='test@email.com',
            password='secret'
        )
        Ad.objects.create(
            title='just a test',
            price=4,
            text='Ehy',
            owner=self.user,
        )

    # Home Page View
    def test_home_view_url_exists_at_proper_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_view_url_by_name_and_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_menu.html')

    # Ad List View
    def test_ad_list_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/')
        self.assertEqual(response.status_code, 200)

    def test_ad_list_view_url_by_name_and_correct_template(self):
        response = self.client.get(reverse('ads:all'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_list.html')

    # Ad Detail View
    def test_ad_detail_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1')
        no_response = self.client.get('ads/ad/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)

    def test_ad_details_belong_to_proper_ad(self):
        response = self.client.get('/ads/ad/1')
        self.assertContains(response, 'just a test')
        self.assertContains(response, 'Ehy')
        self.assertContains(response, 4)

    def test_ad_detail_view_url_by_name_and_correct_template(self):
        response = self.client.get(reverse('ads:ad_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_detail.html')

    # Ad Create view
    def test_ad_create_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/create')
        self.assertEqual(response.status_code, 302)

    def test_ad_create_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_create'))
        self.assertEqual(response.status_code, 302)

    # Ad Update View
    def test_ad_update_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1/update')
        self.assertEqual(response.status_code, 302)

    def test_ad_update_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    # Ad Delete View
    def test_ad_delete_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1/delete')
        self.assertEqual(response.status_code, 302)

    def test_ad_delete_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    # Comment Create View
    def test_comment_create_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1/comment')
        self.assertEqual(response.status_code, 302)

    def test_comment_create_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_comment_create', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    # Comment Delete View
    def test_comment_delete_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/comment/1/delete')
        self.assertEqual(response.status_code, 302)

    def test_comment_delete_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_comment_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    # Favorite View
    def test_favorite_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1/favorite')
        self.assertEqual(response.status_code, 302)

    def test_favorite_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_favorite', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    # Unfavorite View
    def test_unfavorite_view_url_exists_at_proper_location(self):
        response = self.client.get('/ads/ad/1/unfavorite')
        self.assertEqual(response.status_code, 302)

    def test_unfavorite_view_url_by_name(self):
        response = self.client.get(reverse('ads:ad_unfavorite', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
