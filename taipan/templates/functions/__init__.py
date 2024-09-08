from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from taipan.templates import ENV


@dataclass
class Function:
    template: str
    libraries: list[str] = field(default_factory=list)


class Functions(Enum):
    print = Function("functions/print.j2", ["stdio.h"])
    input = Function("functions/input.j2", ["stdio.h"])

    def render(self, **args: Any) -> tuple[str, list[str]]:
        template = ENV.get_template(self.value.template)
        return template.render(**args), self.value.libraries


__all__ = ["Functions"]
