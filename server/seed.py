#!/usr/bin/env python3
"""Reset the database and load example data.

Safe to re-run: every table is cleared first, so data is never duplicated.
"""
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    # Delete the join table first so foreign keys are never left dangling.
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Seeding exercises...')
    squat = Exercise(name='Back Squat', category='strength', equipment_needed=True)
    pushup = Exercise(name='Push-Up', category='strength', equipment_needed=False)
    run = Exercise(name='Treadmill Run', category='cardio', equipment_needed=True)
    plank = Exercise(name='Plank', category='balance', equipment_needed=False)
    stretch = Exercise(name='Hamstring Stretch', category='flexibility', equipment_needed=False)
    db.session.add_all([squat, pushup, run, plank, stretch])

    print('Seeding workouts...')
    leg_day = Workout(date=date(2026, 10, 1), duration_minutes=60, notes='Heavy leg day')
    cardio_day = Workout(date=date(2026, 10, 3), duration_minutes=45, notes='Steady-state cardio')
    full_body = Workout(date=date(2026, 10, 5), duration_minutes=50, notes='Full body circuit')
    db.session.add_all([leg_day, cardio_day, full_body])
    db.session.commit()
