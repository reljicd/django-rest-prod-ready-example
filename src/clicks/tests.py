import base64

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from clicks.models import Click

CAMPAIGN = 4510461
AFTER_DATE = '2021-11-07 03:10:00'
BEFORE_DATE = '2021-11-07 03:20:00'


def set_up_test_data():
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 02:10:00')
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 03:10:34')
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 03:13:03')
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 03:18:51')
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 03:19:53')
    Click.objects.create(campaign=CAMPAIGN,
                         timestamp='2021-11-07 03:50:34')


class TestClickModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()

    def test_campaign_clicks(self):
        self.assertEqual(Click.count_campaign_clicks(CAMPAIGN), 6)

    def test_campaign_clicks_missing_campaign(self):
        self.assertEqual(Click.count_campaign_clicks(0), 0)

    def test_campaign_clicks_between_dates(self):
        self.assertEqual(Click.count_campaign_clicks(
            CAMPAIGN, after_date=AFTER_DATE, before_date=BEFORE_DATE), 4)

    def test_campaign_clicks_after_date(self):
        self.assertEqual(Click.count_campaign_clicks(
            CAMPAIGN, after_date=AFTER_DATE), 5)

    def test_campaign_clicks_before_date(self):
        self.assertEqual(Click.count_campaign_clicks(
            CAMPAIGN, before_date=BEFORE_DATE), 5)

    def test_count_campaign_between_missing_dates(self):
        self.assertEqual(Click.count_campaign_clicks(
            CAMPAIGN, after_date='2022-11-07 03:10:34',
            before_date='2022-11-07 03:10:34'), 0)

    def test_campaign_clicks_malformed_date_exception(self):
        self.assertRaises(ValidationError, Click.count_campaign_clicks,
                          CAMPAIGN, after_date='03:10:34 2022-12-07')
        self.assertRaises(ValidationError, Click.count_campaign_clicks,
                          CAMPAIGN, after_date='2022-13-07 03:10:34')
        self.assertRaises(ValidationError, Click.count_campaign_clicks,
                          CAMPAIGN, after_date='2022.12.07 03:10:34')
        self.assertRaises(ValidationError, Click.count_campaign_clicks,
                          CAMPAIGN, after_date='2022-12')


class TestClickView(APITestCase):
    URL = reverse("clicks:campaign", args=(CAMPAIGN,))
    USERNAME = 'user'
    PASSWORD = 'pass'

    def setUp(self):
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(
                f'{self.USERNAME}:{self.PASSWORD}'.encode()).decode(),
        }
        response = self.client.post(reverse('knox_login'), **auth_headers)
        token = response.data['token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username=cls.USERNAME, password=cls.PASSWORD)
        set_up_test_data()

    @classmethod
    def url_with_dates(cls, after_date: str = '', before_date: str = ''):
        after_date.replace(' ', '+')
        before_date.replace(' ', '+')
        return f'{cls.URL}?after_date={after_date}&before_date={before_date}'

    def test_campaign_clicks(self):
        response = self.client.get(self.URL)
        expected_result = {'campaign': CAMPAIGN,
                           'clicks': 6}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)

    def test_campaign_clicks_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 401)

    def test_campaign_clicks_missing_campaign(self):
        url = reverse("clicks:campaign", args=(0,))
        response = self.client.get(url)
        expected_result = {'campaign': 0,
                           'clicks': 0}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)

    def test_campaign_clicks_between_dates(self):
        url = self.url_with_dates(after_date=AFTER_DATE,
                                  before_date=BEFORE_DATE)
        response = self.client.get(url)
        expected_result = {'campaign': CAMPAIGN,
                           'after_date': AFTER_DATE,
                           'before_date': BEFORE_DATE,
                           'clicks': 4}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)

    def test_campaign_clicks_after_date(self):
        url = self.url_with_dates(after_date=AFTER_DATE)
        response = self.client.get(url)
        expected_result = {'campaign': CAMPAIGN,
                           'after_date': AFTER_DATE,
                           'clicks': 5}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)

    def test_campaign_clicks_before_date(self):
        url = self.url_with_dates(before_date=BEFORE_DATE)
        response = self.client.get(url)
        expected_result = {'campaign': CAMPAIGN,
                           'before_date': BEFORE_DATE,
                           'clicks': 5}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)

    def test_count_campaign_between_missing_dates(self):
        url = self.url_with_dates(after_date='2022-11-07 03:10:34',
                                  before_date='2022-11-07 03:10:34')
        response = self.client.get(url)
        expected_result = {'campaign': CAMPAIGN,
                           'after_date': '2022-11-07 03:10:34',
                           'before_date': '2022-11-07 03:10:34',
                           'clicks': 0}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)
