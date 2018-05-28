# We cannot depend here on something besides the standard library as this is
# also used when installing the dependencies!
try:
    import configparser
except ImportError:
    # Python 2
    import ConfigParser as configparser  # noqa
