"""Marshmallow schemas for serializing models to JSON and validating request bodies."""
from marshmallow import Schema, fields, validate

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='Name must be 1-100 characters.'),
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            EXERCISE_CATEGORIES,
            error=f'Category must be one of: {", ".join(EXERCISE_CATEGORIES)}.',
        ),
    )
    equipment_needed = fields.Bool(load_default=False)
    # Each link carries the workout plus the reps/sets/duration used in it.
    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema(exclude=('exercise',))),
        dump_only=True,
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1, max=1440, error='Duration must be 1-1440 minutes.'),
    )
    notes = fields.Str(
        allow_none=True,
        validate=validate.Length(max=1000, error='Notes must be 1000 characters or fewer.'),
    )
    # Each link carries the exercise plus the reps/sets/duration used in it.
    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema(exclude=('workout',))),
        dump_only=True,
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    workout = fields.Nested(
        lambda: WorkoutSchema(exclude=('workout_exercises',)), dump_only=True
    )
    exercise = fields.Nested(
        lambda: ExerciseSchema(exclude=('workout_exercises',)), dump_only=True
    )
