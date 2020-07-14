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

from datetime import datetime, timedelta
from tastypie.test import ResourceTestCaseMixin

from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_anonymous_user
from geonode.groups.models import GroupProfile
from geonode.tests.base import GeoNodeBaseTestSupport
from geonode.base.populate_test_data import all_public


class SearchApiTests(ResourceTestCaseMixin, GeoNodeBaseTestSupport):
    """Test the search"""

    def setUp(self):
        super(SearchApiTests, self).setUp()

        self.list_url = reverse(
            'api_dispatch_list',
            kwargs={
                'api_name': 'api',
                'resource_name': 'layers'})
        all_public()
        self.norman = get_user_model().objects.get(username="norman")
        self.norman.groups.add(Group.objects.get(name='anonymous'))
        self.test_user = get_user_model().objects.get(username='test_user')
        self.test_user.groups.add(Group.objects.get(name='anonymous'))
        self.bar = GroupProfile.objects.get(slug='bar')
        self.anonymous_user = get_anonymous_user()
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

    def test_category_filters(self):
        """Test category filtering"""

        # check we get the correct layers number returnered filtering on one
        # and then two different categories
        filter_url = self.list_url + '?category__identifier=location'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        filter_url = self.list_url + '?category__identifier__in=location&category__identifier__in=biota'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_tag_filters(self):
        """Test keywords filtering"""

        # check we get the correct layers number returnered filtering on one
        # and then two different keywords
        filter_url = self.list_url + '?keywords__slug=layertagunique'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        filter_url = self.list_url + '?keywords__slug__in=layertagunique&keywords__slug__in=populartag'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_owner_filters(self):
        """Test owner filtering"""

        # check we get the correct layers number returnered filtering on one
        # and then two different owners
        filter_url = self.list_url + '?owner__username=user1'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        filter_url = self.list_url + '?owner__username__in=user1&owner__username__in=foo'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_title_filter(self):
        """Test title filtering"""

        # check we get the correct layers number returnered filtering on the
        # title
        filter_url = self.list_url + '?title=layer2'

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

    def test_date_filter(self):
        """Test date filtering"""

        # check we get the correct layers number returnered filtering on the
        # dates
        step = timedelta(days=60)
        now = datetime.now()
        fstring = '%Y-%m-%d'

        def to_date(val):
            return val.date().strftime(fstring)

        d1 = to_date(now - step)
        filter_url = self.list_url + '?date__exact={}'.format(d1)

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        d3 = to_date(now - (3 * step))
        filter_url = self.list_url + '?date__gte={}'.format(d3)

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)

        d4 = to_date(now - (4 * step))
        filter_url = self.list_url + '?date__range={},{}'.format(d4, to_date(now))

        resp = self.api_client.get(filter_url)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 0)
