

def FieldSerializer(field, obj):
    """Serializes the value of a field to a unicode value."""
    return unicode(field.get(obj))


def FieldNoSerializer(field, obj):
    """Serializes the value of a field to the empty string."""
    return u''
