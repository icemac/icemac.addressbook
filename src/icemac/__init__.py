# declare namespace package, we need this extended version here so the
# package can be installed on a vanilla python where setuptools is not
# installed. The global install.py calls functions inside this
# package.
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:  # pragma: no cover
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
