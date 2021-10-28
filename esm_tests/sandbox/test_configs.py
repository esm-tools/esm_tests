from configs import UserConfig

import pytest
import os


class TestUserConfig:
    def test_creation(self):
        user_config = UserConfig()
        assert user_config.account is None
        assert user_config.script_dir is None
        assert user_config.test_dir == os.getcwd()
        assert UserConfig(account=123) != user_config
