import os
from typing import Annotated, Union, Literal

import yaml
from pydantic import BaseModel, Field, AnyHttpUrl

from verdandi.widget import ALL_WIDGETS


CONFIGURATION_PATH = os.getenv("VERDANDI_CONFIG_FILE", "api-config.yaml")


def widget_config_for(widget_type):
    class WidgetConfiguration(BaseModel):
        name: Literal[widget_type.name]  # ty: ignore[invalid-type-form]
        position: tuple[int, int]
        config: widget_type

    return WidgetConfiguration


_all_widget_configs = [widget_config_for(w) for w in ALL_WIDGETS]


class ApiConfiguration(BaseModel):
    base_url: AnyHttpUrl
    size: tuple[int, int]
    widgets: list[Annotated[Union[*_all_widget_configs], Field(discriminator="name")]]

    @classmethod
    def load(cls, path: str | None = None) -> "ApiConfiguration":
        with open(path or CONFIGURATION_PATH) as file:
            data = yaml.load(
                file,
                Loader=yaml.CSafeLoader,  # ty: ignore[possibly-unbound-attribute]
            )

        return cls(**data)


configuration: ApiConfiguration = ApiConfiguration.load()
