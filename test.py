
from schemalchemy import Base
from schematics.types import IntType, StringType

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Person(Base):
    """
    Example using a SQLAlchemy Table definition.

    Note the Column name strings must match the Schematics properties.

    """

    __table__ = Table('person', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50))
    )

    id = IntType(default=1)
    name = StringType()


class Company(Base):
    """
    Example of setting the columns directly.

    Note the Column properties must match the Schematics properties with
    the column_prefix.

    """

    __tablename__ = 'company'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String(50))

    id = IntType(default=1)
    name = StringType()


def init_db():
    import os
    if os.path.exists('test.db'):
        os.remove('test.db')
    engine = create_engine('sqlite:///test.db')
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return session


def fixture_person():
    p = Person({'name': 'Paul Eipper'})
    return p


def fixture_company():
    c = Company()
    c.id = 2
    c.name = 'nKey'
    c.validate()
    return c


def test_insert_data(session):
    p = fixture_person()
    c = fixture_company()
    session.add(p)
    session.add(c)
    session.commit()
    assert p.serialize() == fixture_person().serialize(), p.serialize()
    assert c.serialize() == fixture_company().serialize(), c.serialize()
    print 'Created:'
    print p.serialize()
    print c.serialize()


def test_load_data(session):
    p = session.query(Person).first()
    c = session.query(Company).first()
    assert p.serialize() == fixture_person().serialize(), p.serialize()
    assert c.serialize() == fixture_company().serialize(), c.serialize()
    print 'Loaded:'
    print p.serialize()
    print c.serialize()


if __name__ == '__main__':
    session = init_db()
    test_insert_data(session())
    test_load_data(session())
    print 'All tests OK'
