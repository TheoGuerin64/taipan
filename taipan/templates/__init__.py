from jinja2 import Environment, PackageLoader

ENV = Environment(
    loader=PackageLoader("taipan"),
)

__all__ = ["ENV"]
