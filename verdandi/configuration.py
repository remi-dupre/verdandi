import os
from typing import Union, Literal

import yaml
from pydantic import BaseModel

from verdandi.widget import ALL_WIDGETS


CONFIGURATION_PATH = os.getenv("VERDANDI_CONFIG_FILE", "api-config.yaml")


def widget_config_for(widget_type):
    class WidgetConfiguration(BaseModel):
        name: Literal[widget_type.name]
        position: tuple[int, int]
        config: widget_type

    return WidgetConfiguration


_all_widget_configs = [widget_config_for(w) for w in ALL_WIDGETS]


class ApiConfiguration(BaseModel):
    size: tuple[int, int]
    widgets: list[Union[*_all_widget_configs]]

    @classmethod
    def load(cls) -> "ApiConfiguration":
        with open("api-config.yaml") as file:
            data = yaml.load(file, Loader=yaml.CSafeLoader)  # ty: ignore[possibly-unbound-attribute]

        return cls(**data)


configuration = ApiConfiguration.load()
