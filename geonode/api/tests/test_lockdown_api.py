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
from django.test.utils import override_settings
from geonode.tests.base import GeoNodeBaseTestSupport


# noinspection DuplicatedCode
@override_settings(API_LOCKDOWN=True)
class LockdownApiTests(ResourceTestCaseMixin, GeoNodeBaseTestSupport):
    """Test the api lockdown functionality"""

    def setUp(self):
        super(LockdownApiTests, self).setUp()
        self.profiles_list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'profiles'})
        self.groups_list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'groups'})
        self.owners_list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'owners'})
        self.tag_list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'keywords'})
        self.region_list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'regions'})

    def test_owners_lockdown(self):
        filter_url = self.owners_list_url

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        # now test with logged in user
        self.api_client.client.login(username='bobby', password='bob')
        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 9)

    def test_regions_lockdown(self):
        filter_url = self.region_list_url

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        self.api_client.client.login(username='bobby', password='bob')
        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 200)

    def test_tags_lockdown(self):
        filter_url = self.tag_list_url

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        self.api_client.client.login(username='bobby', password='bob')
        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 5)
