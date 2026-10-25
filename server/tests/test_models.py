from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise


def test_relationships(app):
    workout = Workout.query.first()
    exercise = Exercise.query.first()
    assert exercise in workout.exercises
    assert workout in exercise.workouts


def test_exercise_rejects_blank_name(app):
    with pytest.raises(ValueError):
        Exercise(name='   ', category='cardio')


def test_exercise_rejects_unknown_category(app):
    with pytest.raises(ValueError):
        Exercise(name='Salsa', category='dance')


def test_workout_rejects_non_positive_duration(app):
    with pytest.raises(ValueError):
        Workout(date=date(2026, 10, 2), duration_minutes=0)


def test_workout_exercise_rejects_negative_reps(app):
    with pytest.raises(ValueError):
        WorkoutExercise(reps=-1)


def test_unique_exercise_name_constraint(app):
    db.session.add(Exercise(name='Squat', category='strength'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_unique_workout_exercise_pair_constraint(app):
    workout = Workout.query.first()
    exercise = Exercise.query.first()
    db.session.add(WorkoutExercise(workout=workout, exercise=exercise, sets=1))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_deleting_workout_cascades(app):
    db.session.delete(Workout.query.first())
    db.session.commit()
    assert WorkoutExercise.query.count() == 0
