from ..base import BaseForm, BaseView
from mock import Mock, patch
import pytest


def test_base__BaseView__url__1():
    """It prefixes the `view_name` with `@@`."""
    view = BaseView()
    view.request = Mock()
    with patch('zope.traversing.browser.absoluteURL') as absoluteURL:
        absoluteURL.return_value = 'http://base.url'
        assert 'http://base.url/@@index.html' == view.url(Mock(), 'index.html')


def test_base__BaseView__url__2():
    """It does not prefix `view_name` starting with `++`."""
    view = BaseView()
    view.request = Mock()
    with patch('zope.traversing.browser.absoluteURL') as absoluteURL:
        absoluteURL.return_value = 'http://base.url'
        assert 'http://base.url/++path++foo' == view.url(Mock(), '++path++foo')


def test_base__BaseView__url__3():
    """It adds keyword arguments as query arguments."""
    view = BaseView()
    view.request = Mock()
    with patch('zope.traversing.browser.absoluteURL') as absoluteURL:
        absoluteURL.return_value = 'http://base.url'
        assert 'http://base.url/@@view?a=2&b=q&b=w' == view.url(
            Mock(), 'view', a=2, b=['q', 'w'])


def test_base__BaseForm__fields__1():
    """It cannot be set twice."""
    form = BaseForm()
    form.fields = Mock()
    with pytest.raises(ValueError):
        form.fields = Mock()
