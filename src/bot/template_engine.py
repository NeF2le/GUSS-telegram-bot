from typing import Any, Optional
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

template_folder = os.path.abspath("bot/templates")

env = Environment(
    loader=FileSystemLoader(template_folder),
    autoescape=select_autoescape(["html"])
)


def render_template(name: str, values: Optional[dict[str, Any]] = None, **kwargs):
    """
    Renders template & returns text.
    :param name: Name of template
    :param values: Values for a template (optional)
    :param kwargs: Keyword-arguments for a template (high-priority)
    """

    if not name.endswith('.html'):
        name += '.html'

    template = env.get_template(name)

    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)

    return rendered_template
