from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Entity(Base):
    __tablename__ = "ENTITIES"
    entity_id = Column(Integer, primary_key=True)
    production_name = Column(String)
    entity_type = Column(String)
    # one-to-many relationship declaration
    tasks = relationship("Task")
    # inheritance
    __mapper_args__ = {'polymorphic_on': entity_type}


class Casting(Base):
    __tablename__ = "CASTINGS"

    casting_id = Column(Integer, primary_key=True, index=True)
    shot = Column(Integer, ForeignKey('SHOTS.shot_id'))
    asset = Column(Integer, ForeignKey('ASSETS.asset_id'))


class Shot(Entity, Base):
    __tablename__ = 'SHOTS'

    shot_id = Column(None, ForeignKey('ENTITIES.entity_id'), primary_key=True)
    sequence = Column(Integer)
    shot_number = Column(Integer)
    cut_in = Column(Integer)
    cut_out = Column(Integer)
    # many-to-many bidirectional relationship
    assets = relationship('Asset', secondary=Casting.__table__, backref='SHOTS')
    # joined table inheritance
    __mapper_args__ = {'polymorphic_identity': 'SHOT'}


class Asset(Entity, Base):
    __tablename__ = 'ASSETS'

    asset_id = Column(None, ForeignKey('ENTITIES.entity_id'), primary_key=True)
    asset_name = Column(String)
    description = Column(String)
    # many-to-many bidirectional relationship
    shots = relationship('Shot', secondary=Casting.__table__, backref='ASSETS')
    # joined table inheritance
    __mapper_args__ = {'polymorphic_identity': 'ASSET'}


class Task(Base):
    __tablename__ = 'TASKS'

    task_id = Column(Integer, primary_key=True)
    entity = Column(Integer, ForeignKey('ENTITIES.entity_id'))
    task_name = Column(String)
    state = Column(String)


def drop_tables(engine):
    Entity.__table__.drop(engine)
    Shot.__table__.drop(engine)
    Asset.__table__.drop(engine)
    Casting.__table__.drop(engine)
    Task.__table__.drop(engine)


def get_engine(name):
    path = 'sqlite:///D:\\path\\to\\wherever\\you\\want\\sql_rdbms\\{0}'.format(name)
    engine = create_engine(path, echo=True)
    return engine


def create_tables(engine):
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


if __name__ == "__main__":

    # SET UP
    engine = get_engine('a_nice_db')
    session = get_session(engine)
    create_tables(engine)

    # DELETE
    # drop_tables(engine)

    # POPULATE TABLES
    seq1_shot1_cool = Shot(production_name='cool_prod', sequence=1, shot_number=1, cut_in=10, cut_out=20)
    seq1_shot2_cool = Shot(production_name='cool_prod', sequence=1, shot_number=2, cut_in=15, cut_out=23)
    seq1_shot1_not_cool = Shot(production_name='less_cool_prod', sequence=1, shot_number=1, cut_in=155, cut_out=223)
    seq1_shot2_not_cool = Shot(production_name='less_cool_prod', sequence=1, shot_number=2, cut_in=15, cut_out=23)

    session.add(seq1_shot1_cool)
    session.add(seq1_shot2_cool)
    session.add(seq1_shot1_not_cool)
    session.add(seq1_shot2_not_cool)

    asset_1 = Asset(production_name='cool_prod', asset_name='chair', description='a chair')
    asset_2 = Asset(production_name='cool_prod', asset_name='table', description='a table')

    asset_3 = Asset(production_name='less_cool_prod', asset_name='tree', description='a tree')
    asset_4 = Asset(production_name='less_cool_prod', asset_name='rock', description='a rock')
    asset_5 = Asset(production_name='less_cool_prod', asset_name='chair', description='a chair')

    session.add(asset_1)
    session.add(asset_2)
    session.add(asset_3)
    session.add(asset_4)
    session.add(asset_5)

    for shot in session.query(Shot).filter(Shot.production_name == 'cool_prod').filter(Shot.sequence == 1).filter(
            Shot.shot_number == 2):
        task_1 = Task(entity=shot.shot_id, task_name='LAYOUT', state='WIP')
    session.add(task_1)

    # TEST QUERIES TO POPULATE CASTINGS

    for asset in session.query(Asset).filter(Asset.asset_name == 'chair').filter(Asset.production_name =="cool_prod"):
        asset_1 = asset.asset_id

    for asset in session.query(Asset).filter(Asset.asset_name == 'chair').filter(Asset.production_name =="less_cool_prod"):
        asset_2 = asset.asset_id

    casting_1 = Casting(shot=1, asset=asset_1)
    casting_2 = Casting(shot=3, asset=asset_2)

    session.add(casting_1)
    session.add(casting_2)

    # TEST QUERIES

    # query production name for each shot
    for shot in session.query(Shot).order_by(Shot.shot_id):
        print(shot.production_name, shot.sequence, shot.shot_number)

    # print task name, state and shot_id
    for task in session.query(Task).order_by(Task.task_id):
        print(task.task_name, task.state)

    session.commit()
