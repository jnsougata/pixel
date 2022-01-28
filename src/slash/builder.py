from typing import Any
from dataclasses import dataclass


class Slash:

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._payload = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [],
        }

    def add_options(self, options: list):
        self._payload["options"] = options

    def subcommand(self, name: str, description: str, options: list):
        self._payload["options"].append(
            {
                "name": name,
                "description": description,
                "type": 1,
                "options": options
            }
        )

    def subcommand_group(self, name: str, description: str, options: list):
        self._payload["options"].append(
            {
                "name": name,
                "description": description,
                "type": 2,
                "options": options
            }
        )

    @staticmethod
    def create_subcommand(name: str, description: str):
        return {
            "name": name,
            "description": description,
            "type": 1,
        }

    @staticmethod
    def set_str_option(name: str, description: str, required: bool = False, choices: list = None):
        return {
            "name": name,
            "description": description,
            "type": 3,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_int_option(name: str, description: str, required: bool = False, choices: list = None):
        return {
            "name": name,
            "description": description,
            "type": 4,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_bool_option(name: str, description: str, required: bool = False, choices: list = None):
        return {
            "name": name,
            "description": description,
            "type": 5,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_user_option(name: str, description: str, required: bool = False, choices: list = None):
        return {
            "name": name,
            "description": description,
            "type": 6,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_channel_option(name: str, description: str, choices: list = None, required: bool = False):
        return {
            "name": name,
            "description": description,
            "type": 7,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_role_option(name: str, description: str, choices: list = None, required: bool = False):
        return {
            "name": name,
            "description": description,
            "type": 8,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_mentionable_option(name: str, description: str, required: bool = False, choices: list = None):
        return {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_number_option(name: str, description: str, choices: list = None, required: bool = False):
        return {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": choices if choices else []
        }

    @staticmethod
    def set_choice(name: str, value):
        return {"name": name, "value": value}

    @property
    def object(self):
        return self._payload
