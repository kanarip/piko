from piko.db import db

person_groups_t = db.Table('person_groups',
        db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
        db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
    )


