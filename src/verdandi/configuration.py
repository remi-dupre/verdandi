import logging
import os
from datetime import datetime
from typing import Annotated, Union, Literal
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, AnyHttpUrl
from simpleeval import simple_eval

from verdandi.widget import ALL_WIDGETS


logger = logging.getLogger(__name__)


def widget_config_for(widget_type):
    class WidgetConfiguration(BaseModel):
        name: Literal[widget_type.name]  # ty: ignore[invalid-type-form]
        position: tuple[int, int]
        when: str = "True"
        config: widget_type

        def is_displayed_at(self, now: datetime) -> bool:
            res = simple_eval(
                self.when,
                names={
                    "now": {
                        "hour": now.hour,
                        "minute": now.minute,
                        "weekday": now.weekday(),
                        "month": now.month,
                        "day": now.day,
                    }
                },
            )

            if not isinstance(res, bool):
                logger.warning("`when` does not evaluate to bool for %s", self.name)

            return bool(res)

    return WidgetConfiguration


_all_widget_configs = [widget_config_for(w) for w in ALL_WIDGETS]


class ApiConfiguration(BaseModel):
    base_url: AnyHttpUrl
    size: tuple[int, int]
    widgets: list[Annotated[Union[*_all_widget_configs], Field(discriminator="name")]]
    use_secret: bool = False

    @classmethod
    def load(cls, path: str | Path | None = None) -> "ApiConfiguration":
        if path is None:
            path = os.getenv("VERDANDI_CONFIG_FILE", "api-config.yaml")

        with open(path) as file:
            data = yaml.load(file, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))

        return cls(**data)

    def secret(self) -> str | None:
        if not self.use_secret:
            return None

        secret = os.getenv("VERDANDI_SECRET")

        if secret is None:
            raise Exception("VERDANDI_SECRET is not set")

        return secret
