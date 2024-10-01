from dataclasses import asdict

import flake8.main.application as app
from flake8.api import legacy as flake8
from flake8.options.parse_args import parse_args

from ..params.flake8_params import Flake8Params


def get_custom_style_guide(params: Flake8Params):
    """
    Create a custom flake8 StyleGuide based on the provided parameters.

    Args:
        params (Flake8Params): The parameters to customize the style guide.

    Returns:
        flake8.api.legacy.StyleGuide: A custom StyleGuide configured with the given parameters.

    Raises:
        Exception: If an option present in params is not valid for the flake8 configuration.
    """
    params_dict = asdict(params)
    flake8_app = app.Application()
    flake8_app.plugins, flake8_app.options = parse_args(
        [f"--max-complexity={params.max_complexity}"]
    )
    options = flake8_app.options
    for key, value in params_dict.items():
        if key in {"per_file_ignores", "extend_ignore"}:
            continue

        try:
            getattr(options, key)
            setattr(options, key, value)
        except AttributeError:
            raise Exception(f'Could not update option "{key}"')

    flake8_app.make_formatter()
    flake8_app.make_guide()
    flake8_app.make_file_checker_manager([])

    return flake8.StyleGuide(flake8_app)
