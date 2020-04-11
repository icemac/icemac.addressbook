import pytest
import six


def test_fixtures__UserFactory__1(address_book, UserFactory):
    """It raises a `LookupError` if the role is unknown."""
    with pytest.raises(LookupError) as err:
        UserFactory(address_book, u'first_name', u'last_name',
                    u'email@example.com', u'password', [u'unknown-role'])
    if six.PY2:  # pragma: no cover
        assert ("Role title u'unknown-role' unknown. Known ones:"
                " [u'Administrator',"
                " u'Archive Visitor',"
                " u'Archivist',"
                " u'Editor',"
                " u'Visitor']"
                == str(err.value))
    else:  # pragma: no cover
        assert ("Role title 'unknown-role' unknown. Known ones:"
                " ['Administrator',"
                " 'Archive Visitor',"
                " 'Archivist',"
                " 'Editor',"
                " 'Visitor']"
                == str(err.value))
