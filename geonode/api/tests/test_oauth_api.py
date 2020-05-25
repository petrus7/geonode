# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2020 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from tastypie.test import ResourceTestCaseMixin

from django.urls import reverse
from django.contrib.auth import get_user_model

from geonode import geoserver
from geonode.layers.models import Layer
from geonode.decorators import on_ogc_backend
from geonode.base.auth import get_or_create_token
from geonode.tests.base import GeoNodeBaseTestSupport
from geonode.base.populate_test_data import all_public


class OAuthApiTests(ResourceTestCaseMixin, GeoNodeBaseTestSupport):
    def setUp(self):
        super(OAuthApiTests, self).setUp()

        self.user = 'admin'
        self.passwd = 'admin'
        self._user = get_user_model().objects.get(username=self.user)
        self.token = get_or_create_token(self._user)
        self.auth_header = 'Bearer {}'.format(self.token)
        self.list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'layers'})
        all_public()
        self.perm_spec = {"users": {}, "groups": {}}

    @on_ogc_backend(geoserver.BACKEND_PACKAGE)
    def test_outh_token(self):
        with self.settings(SESSION_EXPIRED_CONTROL_ENABLED=False, DELAYED_SECURITY_SIGNALS=False):
            # all public
            resp = self.api_client.get(self.list_url)
            self.assertValidJSONResponse(resp)
            self.assertEqual(len(self.deserialize(resp)['objects']), 0)

            perm_spec = {"users": {"admin": ['view_resourcebase']}, "groups": {}}
            layer = Layer.objects.all()[0]
            layer.set_permissions(perm_spec)
            resp = self.api_client.get(self.list_url)
            self.assertEqual(len(self.deserialize(resp)['objects']), 0)

            resp = self.api_client.get(self.list_url, authentication=self.auth_header)
            self.assertEqual(len(self.deserialize(resp)['objects']), 8)

            layer.is_published = False
            layer.save()
