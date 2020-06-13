from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
# from app.models import Base
from flask_script import Manager


app = create_app('dev')

manager = Manager(app)
migrate = Migrate(app, db)
# migrate = Migrate(app, Base)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
