import os

class ChangeSet:

    def __init__(self, **kwargs):
        self.location = kwargs['location']
        self.schema = kwargs['schema']
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.sql = kwargs['sql']
        self.file = os.path.join(self.location, self.type, self.schema, self.name + '.sql')
        self.fullname ='%s.%s' % (self.schema, self.name)
