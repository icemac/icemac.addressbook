# Starting point of data serialization for full text index, not complete, yet


def FieldSerializer(field, obj):
    """Serialize the value of a field to a unicode value."""
    return unicode(field.get(obj))


def FieldNoSerializer(field, obj):
    """Serialize the value of a field to the empty string."""
    return u''
