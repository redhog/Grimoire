from copy import copy

def derive(baseClass, * classes):
    extraClasses = ()
    for extraClass in classes:
        if extraClass not in baseClass.__bases__:
            extraClasses += (extraClass,)
    if not extraClasses:
        return baseClass
    res = copy(baseClass)
    res.__bases__ += extraClasses
    return res

def override(baseClass, * classes):
    extraClasses = ()
    for extraClass in classes:
        if extraClass not in baseClass.__bases__:
            extraClasses += (extraClass,)
    if not extraClasses:
        return baseClass
    res = copy(baseClass)
    res.__bases__ = extraClasses + res.__bases__
    return res

def mixInDerive(baseClass, * classes):
    extraClasses = ()
    for extraClass in classes:
        if extraClass not in baseClass.__bases__:
            extraClasses += (extraClass,)
    if extraClasses:
        baseClass.__bases__ += extraClasses

def mixInOverride(baseClass, * classes):
    extraClasses = ()
    for extraClass in classes:
        if extraClass not in baseClass.__bases__:
            extraClasses += (extraClass,)
    if extraClasses:
        baseClass.__bases__ = extraClasses + baseClass.__bases__

