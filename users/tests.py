from django.test import RequestFactory, TestCase, override_settings

from users.context_processors import site_marketing_data


class SiteMarketingDataTests(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/')


    @override_settings(
        ADSENSE_CLIENT_ID='ca-pub-test-client',
        GOOGLE_SITE_VERIFICATION='verification-token',
        DEBUG=False,
    )
    def test_site_marketing_data_exposes_verification_and_adsense(self):
        context = site_marketing_data(self.request)


        self.assertEqual(context['google_site_verification'], 'verification-token')
        self.assertEqual(context['adsense_client_id'], 'ca-pub-test-client')
        self.assertTrue(context['enable_adsense'])


    @override_settings(ADSENSE_CLIENT_ID='ca-pub-test-client', DEBUG=True)
    def test_site_marketing_data_disables_adsense_in_debug(self):
        context = site_marketing_data(self.request)


        self.assertFalse(context['enable_adsense'])
