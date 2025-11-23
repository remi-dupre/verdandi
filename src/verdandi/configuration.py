import os
from typing import Annotated, Union, Literal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, AnyHttpUrl

from verdandi.widget import ALL_WIDGETS


def widget_config_for(widget_type):
    class WidgetConfiguration(BaseModel):
        name: Literal[widget_type.name]  # ty: ignore[invalid-type-form]
        position: tuple[int, int]
        when: str = "True"
        config: widget_type

    return WidgetConfiguration


_all_widget_configs = [widget_config_for(w) for w in ALL_WIDGETS]


class ApiConfiguration(BaseModel):
    base_url: AnyHttpUrl
    size: tuple[int, int]
    widgets: list[Annotated[Union[*_all_widget_configs], Field(discriminator="name")]]

    @classmethod
    def load(cls, path: str | Path | None = None) -> "ApiConfiguration":
        if path is None:
            path = os.getenv("VERDANDI_CONFIG_FILE", "api-config.yaml")

        with open(path) as file:
            data = yaml.load(file, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))

        return cls(**data)
