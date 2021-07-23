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

    def __init__(self, commons):
        self.commons = commons
        self.sosdir = commons.get('sosdir')
        self.conditions = []

    @classmethod
    def name(cls):
        if cls.checker_name:
            return cls.checker_name
        return cls.__name__.lower()

    def analyze(self, data=None):
        if not data:
            data = {}
        for condition in self.conditions:
            data['matchers'] = (condition['matchers']
                                if condition.get('matchers') else [])
            status, error = getattr(self, condition['validator'])(data)
            condition['status'] = status
            condition['error'] = error

    def status(self):
        for condition in self.conditions:
            if 'status' not in condition:
                raise Exception("Condition in checker (%s) does not have "
                                "'status'" % self.checker_name)
            if not condition['status']:
                return False
        return True

    def passed(self):
        outputs = []
        for condition in self.conditions:
            if condition['status']:
                outputs.append(condition['name'] +
                               ' - ' + condition['description'])
        return outputs

    def failed(self):
        outputs = []
        for condition in self.conditions:
            print(condition)
            if 'status' not in condition:
                raise Exception("Condition in checker (%s) does not have "
                                "'status'" % self.checker_name)
            if condition['status']:
                continue
            if type(condition.get('error')) == list:
                outputs.extend([condition['name'] + ' - ' +
                                i for i in condition['error']])
            elif condition.get('error'):
                outputs.append(condition['name'] + ' - ' + condition['error'])
            else:
                outputs.append(condition['name'] +
                               ' - ' + condition['description'])
        return outputs

    def verbose(self):
        pass
