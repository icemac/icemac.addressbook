from ZODB.ConflictResolution import PersistentReference
import zope.security.proxy


def _get_cmp_keys(self, other):
    """Patch taken from

    https://github.com/zopefoundation/zope.keyreference/pull/6.

    """
    if self.key_type_id == other.key_type_id:  # pragma: no cover
        # While it makes subclassing this class inconvenient,
        # comparing the object's type is faster than doing an
        # isinstance check.  The intent of using type instead
        # of isinstance is to avoid loading state just to
        # determine if we're in conflict resolution.
        if type(self.object) is PersistentReference:
            # We are doing conflict resolution.
            assert isinstance(other(), PersistentReference), (
                'other object claims to be '
                'zope.app.keyreference.persistent but, during conflict '
                'resolution, object is not a PersistentReference')
            self_name = self.object.database_name
            other_name = other().database_name
            if (self_name is None) ^ (other_name is None):
                # one of the two database_names are None during conflict
                # resolution.  At this time the database_name is
                # inaccessible, not unset (it is the same database as the
                # object being resolved).  If they were both None, we
                # would know they are from the same database, so we can
                # compare the oids.  If neither were None, we would be
                # able to reliably compare.  However, in this case,
                # one is None and the other is not, so we can't know how
                # they would sort outside of conflict resolution.  Give
                # up.
                raise ValueError('cannot sort reliably')
            self_oid = self.object.oid
            other_oid = other().oid
        else:
            self_name = self.object._p_jar.db().database_name
            self_oid = self.object._p_oid
            other_obj = zope.security.proxy.getObject(other())
            other_name = other_obj._p_jar.db().database_name
            other_oid = other_obj._p_oid
        return (self_name, self_oid), (other_name, other_oid)

    return self.key_type_id, other.key_type_id  # pragma: no cover
