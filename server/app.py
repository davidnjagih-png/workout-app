from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

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


# Schema instances: list views omit nested links to keep responses small.
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()


def error_response(message, status):
    return make_response({'errors': message}, status)


@app.errorhandler(ValidationError)
def handle_schema_error(err):
    """Marshmallow schema validation failed on the request body."""
    return error_response(err.messages, 400)


@app.errorhandler(ValueError)
def handle_model_error(err):
    """A model @validates method rejected a value."""
    db.session.rollback()
    return error_response([str(err)], 400)


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    """A database constraint (unique, check, not null) rejected the write."""
    db.session.rollback()
    return error_response(['Request violates a database constraint.'], 409)


@app.errorhandler(404)
def handle_not_found(err):
    return error_response(['Resource not found.'], 404)


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date).all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    """Return one workout with its exercises and their reps/sets/duration."""
    workout = db.get_or_404(Workout, id)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = WorkoutSchema(exclude=('workout_exercises',)).load(request.get_json() or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(workout_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    """Delete a workout; its WorkoutExercises are removed by the ORM cascade."""
    workout = db.get_or_404(Workout, id)
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    """Return one exercise with the workouts it appears in."""
    exercise = db.get_or_404(Exercise, id)
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    return make_response({}, 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    return make_response({}, 204)



# ---------- WorkoutExercises ----------

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST'],
)
def add_exercise_to_workout(workout_id, exercise_id):
    return make_response({}, 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
