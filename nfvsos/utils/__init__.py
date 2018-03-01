import inspect

# Inspired and copied from sosreport


def import_module(module_fqname, superclasses=None):
    """Imports the module module_fqname and returns a list of defined classes
    from that module. If superclasses is defined then the classes returned will
    be subclasses of the specified superclass or superclasses. If superclasses
    is plural it must be a tuple of classes."""
    module_name = module_fqname.rpartition(".")[-1]
    module = __import__(module_fqname, globals(), locals(), [module_name])
    modules = [class_ for cname, class_ in
               inspect.getmembers(module, inspect.isclass)
               if class_.__module__ == module_fqname]
    if superclasses:
        modules = [m for m in modules if issubclass(m, superclasses)]

    return modules


def import_plugin(name, superclasses=None):
    """Import name as a module and return a list of all classes defined in that
    module. superclasses should be a tuple of valid superclasses to import,
    this defaults to (Plugin,).
    """
    checker_fqname = "nfvsos.checkers.%s" % name
    if not superclasses:
        superclasses = (Checker,)
    return import_module(checker_fqname, superclasses)


class Checker(object):
    """ This is the base class for nfvsos analyzer, which checks for a specific
    condition to be succesful based on the sosreport information provided.
    """
    checker_name = ''
    checker_profiles = ()
    checker_files = ()

    def analyze(self, base_path):
        pass

    def passed(self):
        pass

    def failed(self):
        pass
