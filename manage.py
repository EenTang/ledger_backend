import os
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import Role
from flask_script import Manager


app = create_app(os.environ.get('ENV') or 'dev')

manager = Manager(app)
migrate = Migrate(app, db)
# migrate = Migrate(app, Base)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # Role.insert_roles()
    manager.run()
