
from schemalchemy import Base
from schematics.types import IntType, StringType
from schematics.transforms import whitelist
from schematics.types.serializable import serializable

from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, synonym

DATABASE = 'test.db'


class Person(Base):
    """
    Example using a SQLAlchemy Table definition.

    Note the Column name strings must match the Schematics properties.

    """

    class Options:
        roles = {
            'public': whitelist('name', 'company_name')
        }

    __table__ = Table('person', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('company_id', Integer, ForeignKey('company.id'))
    )

    id = IntType(default=1)
    name = StringType()
    company_id = synonym('_company_id')

    @serializable
    def company_name(self):
        return self.company.name


class Company(Base):
    """
    Example of setting the columns directly.

    Note the Column properties must match the Schematics properties with
    the column_prefix.

    """

    __tablename__ = 'company'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String(50))
    people = relationship('Person', backref='company')

    id = IntType(default=1)
    name = StringType()


def init_db():
    engine = create_engine('sqlite:///' + DATABASE)
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
    p.company = c
    session.add(p)
    session.add(c)
    session.commit()
    fp = fixture_person()
    fc = fixture_company()
    fc.people.append(fp)
    assert_equal(p.serialize(), fp.serialize())
    assert_equal(c.serialize(), fc.serialize())
    assert_equal(p._company_id, p.company_id)
    assert_equal(p.company, c)
    assert_in(p, c.people)
    print 'Created:'
    print '\tPerson ', p.serialize()
    print '\tCompany', c.serialize()


def test_load_data(session):
    p = session.query(Person).first()
    c = session.query(Company).first()
    fp = fixture_person()
    fc = fixture_company()
    fc.people.append(fp)
    assert_equal(p.serialize(), fp.serialize())
    assert_equal(c.serialize(), fc.serialize())
    print 'Loaded:'
    print '\tPerson ', p.serialize()
    print '\tCompany', c.serialize()


def assert_equal(v1, v2):
    assert v1 == v2, '%s != %s' % (v1, v2)


def assert_in(v1, v2):
    assert v1 in v2, '%s not in %s' % (v1, v2)


if __name__ == '__main__':
    import os
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    session = init_db()
    test_insert_data(session())
    test_load_data(session())
    print 'All tests OK'
