SchemAlchemy
===========

Schematics + SQLAlchemy


## Usage

0. Import schemalchemy (before schematics)
1. Inherit from schemalchemy `Base`
2. Define the SQLAlchemy columns (or provide a Table)
3. Define the Schematics fields

Note: Column property names must be '_' + field_name (see about SQLAlchemy
    `column_prefix` if you need to customize the prefix).


## Example

<pre lang="python"><code>

from schemalchemy import Base
from schematics.types import IntType, StringType
from sqlalchemy import Column, Integer, String


class Person(Base):

    __tablename__ = 'person'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String(50))

    id = IntType(default=1)
    name = StringType()

</code></pre>

