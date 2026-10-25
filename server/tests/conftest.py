import os
import sys
from datetime import date

# Use a throwaway in-memory database and make server/ importable.
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from app import app as flask_app
from models import db, Exercise, Workout, WorkoutExercise


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.create_all()
        squat = Exercise(name='Squat', category='strength', equipment_needed=True)
        workout = Workout(date=date(2026, 10, 1), duration_minutes=45, notes='Legs')
        db.session.add_all([
            squat, workout,
            WorkoutExercise(workout=workout, exercise=squat, sets=3, reps=10),
        ])
        db.session.commit()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
