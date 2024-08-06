from dataclasses import dataclass, field
from typing import Any

from taipan.templates import ENV


@dataclass
class Function:
    name: str
    template: str
    libraries: list[str] = field(default_factory=list)


FUNCTIONS = [
    Function("print", "functions/print.j2", ["stdio.h"]),
    Function("input", "functions/input.j2", ["stdio.h"]),
]

FUNCTION_MAPPING = {func.name: func for func in FUNCTIONS}


def render(name: str, **kwargs: Any) -> tuple[str, list[str]]:
    func = FUNCTION_MAPPING[name]
    template = ENV.get_template(func.template)
    return template.render(**kwargs), func.libraries


__all__ = ["render"]
