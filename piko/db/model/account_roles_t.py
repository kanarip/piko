from piko.db import db

account_roles_t = db.Table('account_roles',
        db.Column('account_id', db.Integer, db.ForeignKey('account.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
    )


