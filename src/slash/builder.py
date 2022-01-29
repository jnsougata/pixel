from typing import Any


class _Option:
    data: Any


class Choice:
    def __init__(self, name: str, value: Any):
        self.data = {
            "name": name,
            "value": value
        }


class StrOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 3,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class IntOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 4,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class BoolOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 5,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class UserOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 6,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class ChannelOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 7,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class RoleOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 8,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class MentionableOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 9,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class NumberOption(_Option):
    def __init__(self, name: str, description: str, required: bool = False, choices: list[Choice] = None):
        self.data = {
            "name": name,
            "description": description,
            "type": 10,
            "required": required,
            "choices": [choice.data for choice in choices] if choices else []
        }


class SlashCommand:

    def __init__(self, name: str, description: str, options: list[_Option] = None):
        self.name = name
        self.description = description
        self._payload = {
            "name": name,
            "description": description,
            "type": 1,
            "options": [option.data for option in options] if options else []
        }

    @staticmethod
    def subcommand(name: str, description: str, options: list):
        return {
            "name": name,
            "description": description,
            "type": 1,
            "options": options
        }

    @staticmethod
    def subcommand_group(name: str, description: str, options: list):

        return {
            "name": name,
            "description": description,
            "type": 2,
            "options": options
        }

    @staticmethod
    def create_subcommand(name: str, description: str):
        return {
            "name": name,
            "description": description,
            "type": 1,
        }

    @staticmethod
    def set_choice(name: str, value):
        return {"name": name, "value": value}

    @property
    def to_dict(self):
        return self._payload
