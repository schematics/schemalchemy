
"""
SchemAlchemy = Schematics + SQLAlchemy


## Usage

0. Import schemalchemy (before schematics)
1. Inherit from schemalchemy `Base`
2. Define the SQLAlchemy columns (or provide a Table)
3. Define the Schematics fields

Note: Column property names must be '_' + field_name (see about SQLAlchemy
    `column_prefix` if you need to customize the prefix).


## Example

    class Person(Base):

        _id = Column('id', Integer, primary_key=True)
        _name = Column('name', String(50))

        id = IntType(default=1)
        name = StringType()


"""

import schematics.models

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


class SchemAlchemyFieldDescriptor(schematics.models.FieldDescriptor):
    def __set__(self, instance, value):
        """
        Field setter override to set same value into table column properties.

        """
        super(SchemAlchemyFieldDescriptor, self).__set__(instance, value)
        if hasattr(self, 'column_name'):
            instance_dict = orm.base.instance_dict(instance)
            instance_dict[self.column_name] = getattr(instance, self.name)


class SchemAlchemyModelMeta(schematics.models.ModelMeta, DeclarativeMeta):
    """
    SchemAlchemy common metaclass.

    Assumes the base metaclasses do not conflict, as in, they do not define the
    same methods.

    """

    def __init__(cls, classname, bases, dict_):
        """
        Map the Schematics fields to the SQLAlchemy columns using synonym
        properties.

        """
        super(SchemAlchemyModelMeta, cls).__init__(classname, bases, dict_)
        if not hasattr(cls, '__mapper__'):
            return
        mapper = cls.__mapper__
        for field_name in cls._fields:
            column_name = (mapper.column_prefix or '') + field_name
            if not column_name in mapper.column_attrs:
                continue
            field_descriptor = cls.__dict__.get(field_name)
            field_descriptor.column_name = column_name
            field_synonym = orm.synonym(column_name, descriptor=field_descriptor)
            mapper.add_property(field_name, field_synonym)


def _reconstructor(self):
    """
    Call Schematics __init__ and trigger the descriptors for all mapped fields
    when loading from database.

    """
    self.__init__()
    cls = self.__class__
    for field_name in self._fields:
        field_descriptor = cls.__dict__.get(field_name)
        if not hasattr(field_descriptor, 'column_name'):
            continue
        column_name = field_descriptor.column_name
        value = orm.base.instance_dict(self).get(column_name)
        setattr(self, field_name, value)


# Schematics monkeypatching

schematics.models.FieldDescriptor = SchemAlchemyFieldDescriptor
schematics.models.ModelMeta = SchemAlchemyModelMeta
schematics.models.Model.__mapper_args__ = {'column_prefix': '_'}
schematics.models.Model._reconstructor = orm.reconstructor(_reconstructor)


# For model definition inherit from the `Base` class below instead of `Model`

Base = declarative_base(
    cls=schematics.models.Model,
    metaclass=SchemAlchemyModelMeta,
    constructor=None)
