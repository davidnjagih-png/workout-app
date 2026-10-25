"""Marshmallow schemas for serializing models to JSON and validating request bodies."""
from marshmallow import (
    Schema, ValidationError, fields, pre_load, validate, validates_schema,
)

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
    @pre_load
    def normalize(self, data, **kwargs):
        """Trim the name and lowercase the category so 'Cardio ' matches 'cardio'."""
        data = dict(data)
        if isinstance(data.get('name'), str):
            data['name'] = data['name'].strip()
        if isinstance(data.get('category'), str):
            data['category'] = data['category'].strip().lower()
        return data

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
    reps = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    sets = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    duration_seconds = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=0))
    workout = fields.Nested(
        lambda: WorkoutSchema(exclude=('workout_exercises',)), dump_only=True
    )
    exercise = fields.Nested(
        lambda: ExerciseSchema(exclude=('workout_exercises',)), dump_only=True
    )

    @validates_schema
    def validate_has_amount(self, data, **kwargs):
        """An exercise in a workout must record reps, sets or a duration."""
        if all(data.get(f) is None for f in ('reps', 'sets', 'duration_seconds')):
            raise ValidationError(
                'Provide at least one of reps, sets or duration_seconds.',
                field_name='_schema',
            )
