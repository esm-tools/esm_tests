#!/usr/bin/env python3
from dataclasses import dataclass
import pathlib
import os
import inspect

from loguru import logger
import yaml


class UserConfigPathExistsError(Exception):
    """Raise when the path already exists"""


@dataclass(frozen=True)
class UserConfig:
    """Describes user preferences"""

    account: str = None
    script_dir: str = None
    test_dir: str = os.getcwd()

    def to_yaml(self, yaml_path: str, force_override: bool = False) -> None:
        if not force_override and pathlib.Path(yaml_path).is_file():
            raise UserConfigPathExistsError(
                f"{yaml_path} already exists, not overriding!"
            )
        with open(yaml_path, "w", encoding="utf-8") as user_config_yml:
            yaml.safe_dump(self.__dict__, user_config_yml)

    @classmethod
    def from_yaml(cls, yaml_path: str):
        with open(yaml_path, "r", encoding="utf-8") as user_config_yml:
            yaml_dict = yaml.safe_load(user_config_yml)
        return cls(**yaml_dict)

    def ask_for_account(self) -> None:
        pass

    def ask_for_test_dir(self) -> None:
        pass

    def ask_for_script_dir(self) -> None:
        pass

    def display_info(self) -> None:
        stack = inspect.stack()
        logger.info(f"Requested Display Info from:")
        logger.info(f"{stack[1].filename}, line {stack[1].lineno}")
        print("\n")
        logger.info(f"Using account {self.account}")
        logger.info(f"Using test directory {self.test_dir}")
        logger.info(f"Using script directory {self.script_dir}")
