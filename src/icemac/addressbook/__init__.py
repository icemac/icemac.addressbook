import grokcore.component.zcml


copyright = '''(c) 2008-2015 Michael Howitz'''


def pytest_skip_tests(name):
    """grokcore.component.zcml.skip_tests() adapted to py.test."""
    return name in ['tests', 'ftests', 'testing', 'conftest']

# Monkey patch until new grokcore.component version supports pytest
grokcore.component.zcml.skip_tests = pytest_skip_tests
