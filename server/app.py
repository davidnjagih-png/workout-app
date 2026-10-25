from flask import Flask, make_response
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# render_as_batch lets Alembic alter SQLite tables (SQLite has limited ALTER support).
migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)


@event.listens_for(Engine, 'connect')
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignores foreign keys unless this pragma is set on each connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    return make_response({}, 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    return make_response({}, 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    return make_response({}, 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    return make_response({}, 204)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
