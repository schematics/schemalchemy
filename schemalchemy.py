
"""
SchemAlchemy = Schematics + SQLAlchemy


## Usage

0. Import schemalchemy (before schematics)
1. Inherit from schemalchemy `Base`
2. Define the Schematics fields
3. Define the SQLAlchemy columns (or provide a Table)
4. Use the same name for the columns that map to the fields, plus a prefix
5. Set `__mapper_args__['column_prefix']` to that prefix


## Example

    class Person(Base):

        __mapper_args__ = {'column_prefix': '_'}  # required by SchemAlchemy

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

        Assumes the column properties are named as:
            `column_prefix` + `field_name`

        Relies on the `column_prefix` to be defined in the `__mapper_args__`
        dict of the instance to set the column properties.

        """
        super(SchemAlchemyFieldDescriptor, self).__set__(instance, value)
        prefix = instance.get('__mapper_args__', {}).get('column_prefix')
        if prefix:
            setattr(instance, prefix + self.name, instance._data[self.name])


class SchemAlchemyModelMeta(schematics.models.ModelMeta, DeclarativeMeta):
    """
    SchemAlchemy common metaclass.

    Assumes the base metaclasses do not conflict, as in, they do not define the
    same methods.

    """
    pass


# Schematics monkeypatching

schematics.models.FieldDescriptor = SchemAlchemyFieldDescriptor
schematics.models.ModelMeta = SchemAlchemyModelMeta
schematics.models.Model._reconstructor = orm.reconstructor(
    schematics.models.Model.__init__.im_func)  # call init when loaded from db


# For model definition inherit from the `Base` class below instead of `Model`

Base = declarative_base(
    cls=schematics.models.Model,
    metaclass=SchemAlchemyModelMeta,
    constructor=None)
