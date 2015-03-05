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
            {'name': 'Foo Bar', 'mention_name': 'foobar'},
            {'name': 'Baz Qux', 'mention_name': 'bazqux'},
            {'name': 'Abc 123', 'mention_name': 'abc123'},
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

    @pytest.mark.parametrize('nick,expected', [
        ('foo', 'foo'),  # Not in map
        ('bar', '@foobar'),  # In map
    ])
    def test_preprocess(self, nick, expected):
        with patch.object(self.plugin, 'nick_map', {'bar': '@foobar'}):
            _, real_nick, _ = self.plugin.preprocess(Mock(), '#bots', nick, 'message')

            assert real_nick == expected
