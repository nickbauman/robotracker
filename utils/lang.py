
def info(object, spacing=10, collapse=1):
    """Print methods and doc strings.

    Takes module, class, list, dictionary, or string."""
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print "\n".join(["%s %s" %
                     (method.ljust(spacing),
                     processFunc(str(getattr(object, method).__doc__)))
        for method in methodList])

    if __name__ == "__main__":
        print info.__doc__


def clone_entity(e, **extra_args):
    """Clones a GAE entity, adding or overriding constructor attributes.

    The cloned entity will have exactly the same property values as the original
    entity, except where overridden. By default it will have no parent entity or
    key name, unless supplied.

    Args:
      e: The entity to clone
      extra_args: Keyword arguments to override from the cloned entity and pass
        to the constructor.
    Returns:
      A cloned, possibly modified, copy of entity e.
    """
    klass = e.__class__
    props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
    props.update(extra_args)
    return klass(**props)