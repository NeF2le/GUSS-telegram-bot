from typing import Any, Optional
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.enums import MenuName

template_folder = os.path.abspath("bot/menu_templates")

env = Environment(
    loader=FileSystemLoader(template_folder),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True
)
env.add_extension('jinja2.ext.do')


def render_template(menu_name: MenuName | str, values: Optional[dict[str, Any]] = None, **kwargs):
    """
    Renders template & returns text.
    :param menu_name: A MenuName object meaning a name of template.
    :param values: Values for a template (optional).
    :param kwargs: Keyword-arguments for a template (high-priority).
    """

    name = menu_name.value if isinstance(menu_name, MenuName) else menu_name
    if not name.endswith('.html'):
        name += '.html'

    template = env.get_template(name)

    if values:
        rendered_template = template.render(values, **kwargs)
    else:
        rendered_template = template.render(**kwargs)

    return rendered_template
