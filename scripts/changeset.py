import os

class ChangeSet:

    def __init__(self, **kwargs):
        if 'file' in kwargs:
            splits = kwargs['file'].split('/')
            if len(splits) == 3:
                splits.insert(2, '')
            if len(splits) != 4:
                raise ValueError('Incorrect file format for % ' % kwargs['file'])
            self.location = splits[0]
            self.schema = splits[2]
            self.name = splits[3][:-4]
            self.type = splits[1]
            if self.location in ['latest', 'install']:
                if self.type[:-3] == 'xes':
                    self.type = self.type[:-2]
                else:
                    self.type = self.type[:-1]
            elif self.location[0].lower() != 'v':
                raise ValueError('Sql not in correct version folder % ' % kwargs['file'])
        else:
            self.location = kwargs['location']
            self.schema = kwargs['schema']
            self.name = kwargs['name']
            self.type = kwargs['type']
        self.sql = kwargs['sql']
        if self.location in ['latest', 'install']:
            if self.type[:-1] == 'x':
                self.types = self.type + 'es'
            else:
                self.types = self.type + 's'
        else:
            self.types = self.type
        self.file = os.path.join(self.location, self.types, self.schema, self.name + '.sql')
        self.fullname ='%s.%s' % (self.schema, self.name)
        self.author = kwargs.get('author', 'system')
        self.is_formated_sql = self.sql.startswith('--liquibase formatted sql')
        if (kwargs.get('rollback_file', None)):
            self.rollback_file = os.path.join(self.location, self.types, self.schema, self.name + '.rollback.sql')

    def __str__(self):
        return self.fullname
