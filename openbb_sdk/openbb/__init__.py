# flake8: noqa
from openbb_core.app.static.app_factory import app as obb

sdk = obb


def _rebuild_python_interface() -> None:
    """Rebuild the Python SDK."""
    from openbb_core.app.static.package_builder import (  # pylint: disable=import-outside-toplevel
        PackageBuilder,
    )

    PackageBuilder.build()
