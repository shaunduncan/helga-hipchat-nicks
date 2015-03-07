import pytest

from mock import Mock, patch

import helga_hipchat_nicks as hipchat_nicks


class TestHipChatNicks(object):

    def setup(self):
        self.settings = Mock(HIPCHAT_API_TOKEN='foo',
                             HIPCHAT_API_ENDPOINT='https://api.hipchat.com')

        with patch.multiple(hipchat_nicks, settings=self.settings):
            self.plugin = hipchat_nicks.HipChatNicks()

    def test_setup_correctly(self):
        assert self.plugin.api_token == self.settings.HIPCHAT_API_TOKEN
        assert self.plugin.api_endpoint == 'https://api.hipchat.com'
        assert isinstance(self.plugin.client, hipchat_nicks.HypChat)
        assert self.plugin.nick_map == {}

    def test_init_nicks(self):
        users = [
            {'name': 'Foo Bar', 'mention_name': 'foobar', 'id': 1},
            {'name': 'Baz Qux', 'mention_name': 'bazqux', 'id': 2},
            {'name': 'Abc 123', 'mention_name': 'abc123', 'id': 3},
        ]

        expected = {
            'Foo Bar': '@foobar',
            'Baz Qux': '@bazqux',
            'Abc 123': '@abc123',
        }

        with patch.object(self.plugin, 'client'):
            self.plugin.client.users.return_value = {'items': users}
            self.plugin._init_nicks()

            assert self.plugin.nick_map == expected

    def test_init_nicks_gets_jid_name(self):
        users = [
            {'name': 'Foo Bar', 'mention_name': 'foobar', 'id': 1},
            {'name': 'Baz Qux', 'mention_name': 'bazqux', 'id': 2},
            {'name': 'Abc 123', 'mention_name': 'abc123', 'id': 3},
        ]

        details = [
            {'xmpp_jid': '1_1@example.com'},
            {'xmpp_jid': '1_2@example.com'},
            {'xmpp_jid': '1_3@example.com'},
        ]

        expected = {
            'Foo Bar': '@foobar',
            'Baz Qux': '@bazqux',
            'Abc 123': '@abc123',
            '1_1': '@foobar',
            '1_2': '@bazqux',
            '1_3': '@abc123',
        }

        with patch.object(self.plugin, 'client'):
            self.plugin.client.users.return_value = {'items': users}
            self.plugin.client.get_user.side_effect = details
            self.plugin._init_nicks()

            assert self.plugin.nick_map == expected

    @pytest.mark.parametrize('nick,expected', [
        ('foo', 'foo'),  # Not in map
        ('bar', '@foobar'),  # In map
    ])
    def test_preprocess(self, nick, expected):
        with patch.object(self.plugin, 'nick_map', {'bar': '@foobar'}):
            _, real_nick, _ = self.plugin.preprocess(Mock(), '#bots', nick, 'message')

            assert real_nick == expected
