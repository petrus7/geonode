from django.conf import settings
from tastypie.test import ResourceTestCaseMixin

from django.urls import reverse
from geonode import geoserver
from geonode.layers.models import Layer
from geonode.utils import check_ogc_backend
from geonode.tests.base import GeoNodeBaseTestSupport
from geonode.base.populate_test_data import all_public


class PermissionsApiTests(ResourceTestCaseMixin, GeoNodeBaseTestSupport):

    def setUp(self):
        super(PermissionsApiTests, self).setUp()
        self.user = 'admin'
        self.passwd = 'admin'
        self.list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'layers'})
        all_public()
        self.perm_spec = {"users": {}, "groups": {}}

    def test_layer_get_list_unauth_all_public(self):
        """
        Test that the correct number of layers are returned when the
        client is not logged in and all are public
        """

        resp = self.api_client.get(self.list_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_layers_get_list_unauth_some_public(self):
        """
        Test that if a layer is not public then not all are returned when the
        client is not logged in
        """
        layer = Layer.objects.all()[0]
        layer.set_permissions(self.perm_spec)

        resp = self.api_client.get(self.list_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_layers_get_list_auth_some_public(self):
        """
        Test that if a layer is not public then all are returned if the
        client is not logged in
        """
        self.api_client.client.login(username=self.user, password=self.passwd)
        layer = Layer.objects.all()[0]
        layer.set_permissions(self.perm_spec)

        resp = self.api_client.get(self.list_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 8)

    def test_layer_get_list_layer_private_to_one_user(self):
        """
        Test that if a layer is only visible by admin, then does not appear
        in the unauthenticated list nor in the list when logged is as bobby
        """
        perm_spec = {"users": {"admin": ['view_resourcebase']}, "groups": {}}
        layer = Layer.objects.all()[0]
        layer.set_permissions(perm_spec)
        resp = self.api_client.get(self.list_url)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        self.api_client.client.login(username='bobby', password='bob')
        resp = self.api_client.get(self.list_url)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

        self.api_client.client.login(username=self.user, password=self.passwd)
        resp = self.api_client.get(self.list_url)
        self.assertEqual(len(self.deserialize(resp)['objects']), 8)

        layer.is_published = False
        layer.save()

        # with resource publishing
        with self.settings(RESOURCE_PUBLISHING=True):
            resp = self.api_client.get(self.list_url)
            self.assertEqual(len(self.deserialize(resp)['objects']), 8)

            self.api_client.client.login(username='bobby', password='bob')
            resp = self.api_client.get(self.list_url)
            self.assertEqual(len(self.deserialize(resp)['objects']), 2)

            self.api_client.client.login(username=self.user, password=self.passwd)
            resp = self.api_client.get(self.list_url)
            self.assertEqual(len(self.deserialize(resp)['objects']), 8)

    def test_layer_get_detail_unauth_layer_not_public(self):
        """
        Test that layer detail gives 404 when not public and not logged in
        """
        layer = Layer.objects.all()[0]
        layer.set_permissions(self.perm_spec)
        self.assertHttpNotFound(self.api_client.get(
            self.list_url + str(layer.id) + '/'))

        self.api_client.client.login(username=self.user, password=self.passwd)
        resp = self.api_client.get(self.list_url + str(layer.id) + '/')
        self.assertValidJSONResponse(resp)

        # with delayed security
        with self.settings(DELAYED_SECURITY_SIGNALS=True):
            if check_ogc_backend(geoserver.BACKEND_PACKAGE):
                from geonode.security.utils import sync_geofence_with_guardian
                sync_geofence_with_guardian(layer, self.perm_spec)
                self.assertTrue(layer.dirty_state)

                self.client.login(username=self.user, password=self.passwd)
                resp = self.client.get(self.list_url)
                self.assertEqual(len(self.deserialize(resp)['objects']), 8)

                self.client.logout()
                resp = self.client.get(self.list_url)
                self.assertEqual(len(self.deserialize(resp)['objects']), 0)

                from django.contrib.auth import get_user_model
                get_user_model().objects.create(
                    username='imnew',
                    password='pbkdf2_sha256$12000$UE4gAxckVj4Z$N\
                    6NbOXIQWWblfInIoq/Ta34FdRiPhawCIZ+sOO3YQs=')
                self.client.login(username='imnew', password='thepwd')
                resp = self.client.get(self.list_url)
                self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_new_user_has_access_to_old_layers(self):
        """Test that a new user can access the public available layers"""
        from django.contrib.auth import get_user_model
        get_user_model().objects.create(
            username='imnew',
            password='pbkdf2_sha256$12000$UE4gAxckVj4Z$N\
            6NbOXIQWWblfInIoq/Ta34FdRiPhawCIZ+sOO3YQs=')
        self.api_client.client.login(username='imnew', password='thepwd')
        resp = self.api_client.get(self.list_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        # with delayed security
        if check_ogc_backend(geoserver.BACKEND_PACKAGE):
            _ogc_geofence_enabled = settings.OGC_SERVER
            try:
                _ogc_geofence_enabled['default']['GEOFENCE_SECURITY_ENABLED'] = True
                with self.settings(DELAYED_SECURITY_SIGNALS=True,
                                   OGC_SERVER=_ogc_geofence_enabled,
                                   DEFAULT_ANONYMOUS_VIEW_PERMISSION=True):
                    layer = Layer.objects.all()[0]
                    layer.set_default_permissions()
                    layer.refresh_from_db()
                    self.assertTrue(layer.dirty_state)

                    self.client.login(username=self.user, password=self.passwd)
                    resp = self.client.get(self.list_url)
                    self.assertEqual(len(self.deserialize(resp)['objects']), 8)

                    self.client.logout()
                    resp = self.client.get(self.list_url)
                    self.assertEqual(len(self.deserialize(resp)['objects']), 0)

                    self.client.login(username='imnew', password='thepwd')
                    resp = self.client.get(self.list_url)
                    self.assertEqual(len(self.deserialize(resp)['objects']), 0)
            finally:
                _ogc_geofence_enabled['default']['GEOFENCE_SECURITY_ENABLED'] = False
