import Grimoire.Performer, Grimoire.Types, Grimoire.Utils, string, ldap, types, operator

A = Grimoire.Types.AnnotatedValue
Ps = Grimoire.Types.ParamsType.derive
R = Grimoire.Types.RestrictedType.derive

PSW = Grimoire.Types.PasswordType
NES = Grimoire.Types.NonemptyStringType
NEU = Grimoire.Types.NonemptyUnicodeType

syntaxtab = {
    '1.3.6.1.1.1.0.0': NES,				# RFC2307 NIS Netgroup Triple
    '1.3.6.1.1.1.0.1': NES,				# RFC2307 Boot Parameter
    '1.3.6.1.4.1.1466.115.121.1.40': NES,		# Octet String
    '1.3.6.1.4.1.1466.115.121.1.28': None,		# JPEG
    '1.3.6.1.4.1.1466.115.121.1.41': NEU,		# Postal Address
    '1.2.826.0.1.3344810.7.1': None,			# Serial Number and Issuer
    '1.3.6.1.4.1.1466.115.121.1.52': NES,		# Telex Number
    '1.3.6.1.4.1.1466.115.121.1.50': NES,		# Telephone Number
    '1.3.6.1.4.1.1466.115.121.1.27': types.IntType,	# Integer
    '1.3.6.1.4.1.1466.115.121.1.49': None,		# Supported Algorithm
    '1.3.6.1.4.1.1466.115.121.1.39': NES,		# Other Mailbox
    '1.3.6.1.4.1.1466.115.121.1.38': NES,		# OID
    '1.3.6.1.4.1.1466.115.121.1.15': NEU,		# Directory String
    '1.3.6.1.4.1.1466.115.121.1.12': NES,		# Distinguished Name
    '1.3.6.1.4.1.1466.115.121.1.11': NES,		# Country String
    '1.3.6.1.4.1.1466.115.121.1.10': None,		# Certificate Pair
    '1.3.6.1.4.1.1466.115.121.1.44': NES,		# Printable String
    '1.3.6.1.4.1.1466.115.121.1.26': types.StringType,	# IA5 String
    '1.3.6.1.4.1.1466.115.121.1.34': NES,		# Name And Optional UID
    '1.3.6.1.4.1.1466.115.121.1.24': NES,		# Generalized Time
    '1.3.6.1.4.1.1466.115.121.1.36': types.IntType,	# Numeric String
    '1.3.6.1.4.1.1466.115.121.1.22': NES,		# Facsimile Telephone Number
    '1.3.6.1.4.1.1466.115.121.1.7': Grimoire.Types.BooleanType,		# Boolean
    '1.3.6.1.4.1.1466.115.121.1.6': None,	        # Bit String
    '1.3.6.1.4.1.1466.115.121.1.5': None,		# Binary
    '1.3.6.1.4.1.1466.115.121.1.4': None,		# Audio
    '1.3.6.1.4.1.1466.115.121.1.9': None,		# Certificate List
    '1.3.6.1.4.1.1466.115.121.1.8': None,      		# Certificate
    }

attributetab = {
    'userPassword': (Grimoire.Types.NewPasswordType, 'Password/passphrase'),
    'sn': (NEU, 'Surname'),
    'cn': (NEU, 'Common name'),
    'givenName': (NEU, 'Given name'),
    'initials': (NEU, 'Initials'),
    'grimoireSwedishIDNumber': (NES, 'Personal identification number'),

    'title': (NEU, 'Title'),
    'ou': (NEU, 'Organizational unit'),
    'roomNumber': (types.IntType, 'Room number'),

    'telephoneNumber': (NES, 'Telephone number'),
    'facsimileTelephoneNumber': (NES, 'Facsimile telephone number'),
    'street': (NEU, 'Street'),
    'postOfficeBox': (NEU, 'Post office box'),
    'postalCode': (NES, 'Postal code'),
    'postalAddress': (NEU, 'Postal address'),

    'homePhone': (NES, 'Home telephone number'),
    'homePostalAddress': (NEU, 'Home postal address'),
    'mobile': (NES, 'Mobile telephone number'),
    'pager': (NES, 'Pager number'),

    'preferredLanguage': (R(types.StringType, []), 'Preferred language'),

    'grimoireSecondaryUid': (NES, 'Mail username'),

    'description': (NEU, 'Description'),

    'associatedDomain': (NES, 'RFC1274: Domain associated with object'),
    'grimoireMailDomain': (NES, 'Domain at which users should have their e-mail-adresses'),
    'grimoireSecondaryMailDomain': (NES, 'Domain for mail-aliased e-mail-adresses'),
    }

def typeOfSyntax(schema, syntax):
    if syntax in syntaxtab and syntaxtab[syntax]:
        return syntaxtab[syntax]
    syntaxObj = schema.get_obj(ldap.schema.models.LDAPSyntax, syntax)
    if not syntaxObj:
        raise TypeError('Unknown syntax')
    syntax = syntaxObj.get_id()
    if syntax in syntaxtab and syntaxtab[syntax]:
        return syntaxtab[syntax]
    if syntaxObj.not_human_readable:
        raise TypeError('Unknown syntax')
    return NEU

def typeOfAttribute(schema, names, syntax):
    for name in names:
        if name in attributetab and attributetab[name]:
            return attributetab[name][0]
    return typeOfSyntax(schema, syntax)

def descOfAttribute(names, desc):
    for name in names:
        if name in attributetab and attributetab[name]:
            return attributetab[name][1]
    return desc

class Performer(Grimoire.Performer.Base):
    class ldapattributes(Grimoire.Performer.Method):
        __path__ = ['ldapattributes', '$ldapservername']
        def _call(self, objectClasses, include = [], exclude = [], convertToParams = True, convertType = None):
            conn = self._callWithUnlockedTree(self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters,
                                              ['local', 'ldap', 'admin', 'conn'], cache=True)

            schema = ldap.schema.SubSchema(conn.read_subschemasubentry_s(conn.search_subschemasubentry_s(conn.realm)))
            def getComment(objectClasses):
                if not objectClasses:
                    return None
                objectClasses = [schema.get_obj(ldap.schema.models.ObjectClass, objectClass) for objectClass in objectClasses]
                for objectClass in objectClasses:
                    if objectClass.desc:
                        return objectClass.desc
                return getComment(reduce(operator.__add__, [objectClass.sup for objectClass in objectClasses]))
            comment = getComment(objectClasses)

            required, optional = schema.attribute_types(objectClasses)
            def syntax(attributeType):
                if attributeType.syntax is not None:
                    return attributeType.syntax
                if attributeType.sup:
                    for sup in attributeType.sup:
                        try:
                            return syntax(schema.get_obj(ldap.schema.models.AttributeType, sup))
                        except TypeError:
                            pass
                raise TypeError('Object does not have a syntax')
            include = [name.lower() for name in include]
            exclude = [name.lower() for name in exclude]
            def extract(attributes):
                def extractAttribute(attribute):
                    def check():
                        if attribute.get_id() in exclude:
                            raise Grimoire.Utils.FilterOutError()
                        if attribute.get_id() in include:
                            return
                        for name in attribute.names:
                            name = name.lower()
                            if name in include:
                                return
                            elif name in exclude:
                                raise Grimoire.Utils.FilterOutError()
                        if include:
                            raise Grimoire.Utils.FilterOutError()
                    check()
                    return (attribute.names, (attribute.desc, syntax(attribute)))
                return list(Grimoire.Utils.Map(extractAttribute, attributes.itervalues()))
            required = extract(required)
            optional = extract(optional)

            if not convertToParams:
                return (comment, dict(required), dict(optional))

            def convertAttribute((names, (desc, syntax))):
                try:
                    return (names[0], A(typeOfAttribute(schema, names, syntax), descOfAttribute(names, desc)))
                except TypeError:
                    raise Grimoire.Utils.FilterOutError()

            return A(Ps(Grimoire.Utils.Map(convertAttribute,
                                           required + optional),
                        len(required),
                        convertType = convertType),
                     comment)
        _call = Grimoire.Utils.cachingFunction(_call)

        def _params(self):
            return A(Ps([('objectClasses',
                          A(Grimoire.Types.StringListType,
                            "Object-classes to list attributes for")),
                         ('include',
                          A(Grimoire.Types.StringListType,
                            "Attributes to include in listing (or all if empty)")),
                         ('exclude',
                          A(Grimoire.Types.StringListType,
                            "Attributes to exclude fom listing")),
                         ('convertToParams',
                          A(Grimoire.Types.BooleanType,
                            "Convert attribute listing to a parameter list specification for a Grimoire method")),
                         ('convertType',
                          A(Grimoire.Types.ParamsType,
                            "If converting to a parameter list specification, set convertType in that ParamsType object to this value")),
                         ],
                        1),
                     'List attributes of a set of LDAP object classes')
        _params = Grimoire.Utils.cachingFunction(_params)

    class ldapattributes_ofentry(Grimoire.Performer.SubMethod):
        __path__ = ['ldapattributes', 'ofentry', '$ldapservername']
        def _call(self, path, include = [], exclude = [], convertToParams = True, convertType = None, addCurrentAsDefault = True):
            conn = self._callWithUnlockedTree(
                lambda:
                    self._getpath(Grimoire.Types.TreeRoot).directory.get.parameters(
                        ['local', 'ldap', 'admin', 'conn'], cache=True))
            dn = string.join(Grimoire.Utils.Reverse(path) + [conn.realm], ',')
            entry = conn.result(conn.search(dn, ldap.SCOPE_BASE))[1][0][1]
            res = self._getpath(Grimoire.Types.MethodBase,
                                path=['ldapattributes', '$ldapservername']
                                )(entry['objectClass'], include, exclude, convertToParams, convertType)
            if addCurrentAsDefault:
                comment = Grimoire.Types.getComment(res)
                res = Grimoire.Types.getValue(res)
                res = A(
                    res.addDefaults(entry),
                    comment)
            return res
        def _dir(self, path, depth):
            return self._callWithUnlockedTree(
                lambda: self._getpath(Grimoire.Types.MethodBase,
                                      path=['ldapentries', '$ldapservername'] + path
                                      )(depth, stripTypes = 0))
        def _params(self, path):
            return A(Ps([('include',
                          A(Grimoire.Types.StringListType,
                            "Attributes to include in listing (or all if empty)")),
                         ('exclude',
                          A(Grimoire.Types.StringListType,
                            "Attributes to exclude fom listing")),
                         ('convertToParams',
                          A(Grimoire.Types.BooleanType,
                            "Convert attribute listing to a parameter list specification for a Grimoire method")),
                         ('convertType',
                          A(Grimoire.Types.ParamsType,
                            "If converting to a parameter list specification, set convertType in that ParamsType object to this value")),
                         ('addCurrentAsDefault',
                          A(Grimoire.Types.BooleanType,
                            "Add current values of entry as default values")),
                         ],
                        1),
                     'List attributes of the LDAP object classes of an LDAP entry')
        _params = Grimoire.Utils.cachingFunction(_params)
