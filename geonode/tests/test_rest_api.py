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
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import AnonymousUser, Group

from geonode.api.authorization import GroupAuthorization, GroupProfileAuthorization, ProfileAuthorization
from geonode.groups.models import GroupProfile
from geonode.people.models import Profile
from geonode.tests.base import GeoNodeBaseTestSupport


class TestGroupResAuthorization(GeoNodeBaseTestSupport):
    # Group fixture is loaded in base class

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Group.objects.exclude(name='anonymous'))
    def test_super_admin_user(self, super_mock):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test', is_staff=True, is_superuser=True)
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupAuthorization().read_list([], mock_bundle)
        self.assertEqual(Group.objects.exclude(name='anonymous').count(), groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Group.objects.exclude(name='anonymous'))
    @patch('geonode.people.models.Profile.group_list_all', return_value=[2])
    def test_regular_user_hide_private(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(1, groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Group.objects.exclude(name='anonymous'))
    @patch('geonode.people.models.Profile.group_list_all', return_value=[1])
    def test_regular_user(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(2, groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Group.objects.exclude(name='anonymous'))
    @patch('geonode.people.models.Profile.group_list_all', return_value=[1])
    def test_anonymous_user(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': AnonymousUser()
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(1, groups.count())


class TestGroupProfileResAuthorization(GeoNodeBaseTestSupport):
    # Group fixture is loaded in base class

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list', return_value=GroupProfile.objects.all())
    def test_super_admin_user(self, super_mock):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test', is_staff=True, is_superuser=True)
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupProfileAuthorization().read_list([], mock_bundle)
        self.assertEqual(GroupProfile.objects.all().count(), groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list', return_value=GroupProfile.objects.all())
    @patch('geonode.people.models.Profile.group_list_all', return_value=[2])
    def test_regular_user_hide_private(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupProfileAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(1, groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list', return_value=GroupProfile.objects.all())
    @patch('geonode.people.models.Profile.group_list_all', return_value=[1])
    def test_regular_user(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile(username='test')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupProfileAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(2, groups.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list', return_value=GroupProfile.objects.all())
    @patch('geonode.people.models.Profile.group_list_all', return_value=[1])
    def test_anonymous_user(self, super_mock, mocke_profile):
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': AnonymousUser()
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)

        groups = GroupProfileAuthorization().read_list(['not_empty_but_fake'], mock_bundle)
        self.assertEqual(1, groups.count())


class TestProfileAuthorization(GeoNodeBaseTestSupport):

    # def add_user_to_public_group(self):

    def setUp(self):
        self.u = Profile.objects.create_user(username='new_public_user', email="zaq@ws.com")
        # public group from fixture
        g = GroupProfile.objects.get(title='bar')

        # private group from fixture
        self.p_g = GroupProfile.objects.get(title='Registered Members')

        # adjust groups to test cases
        self.p_g.leave(self.u)
        g.join(self.u)

        self._prepare_another_test_group()

    def _prepare_another_test_group(self):
        g = Group.objects.create(name='test')
        u = Profile.objects.create_user(username='test_priv_user', email="zaaq@ws.com")
        gp = GroupProfile.objects.create(title='test', access='private', group=g)
        self.p_g.leave(u)
        gp.join(u)

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_anonymous_user(self, profile_list):
        public_users_count = 1
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': AnonymousUser()
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(public_users_count, users.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_public_group_user(self, profile_list):
        public_users_count = 1
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': self.u
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(public_users_count, users.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_private_group_user(self, profile_list):
        # private and public users
        expected_users_count = 4
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile.objects.get(username='norman')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(expected_users_count, users.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_private_another_private_user(self, profile_list):
        # private users of user private (1) and public (1) group
        expected_users_count = 2
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile.objects.get(username='test_priv_user')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(expected_users_count, users.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_private_both_private_user(self, profile_list):
        # private users of all groups
        expected_users_count = 5
        user = Profile.objects.get(username='test_priv_user')
        self.p_g.join(user)
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile.objects.get(username='test_priv_user')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(expected_users_count, users.count())

    @patch('geonode.api.authorization.ApiLockdownAuthorization.read_list',
           return_value=Profile.objects.exclude(username='AnonymousUser'))
    def test_private_admin_user(self, profile_list):
        # private and public users
        expected_users_count = 5
        mock_bundle = MagicMock()
        request_mock = MagicMock()
        r_attr = {
            'user': Profile.objects.get(username='admin')
        }
        attrs = {
            'request': request_mock
        }
        request_mock.configure_mock(**r_attr)
        mock_bundle.configure_mock(**attrs)
        users = ProfileAuthorization().read_list(profile_list, mock_bundle)
        self.assertEqual(expected_users_count, users.count())


