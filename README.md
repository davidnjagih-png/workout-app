# Workout Tracker API

A Flask + SQLAlchemy backend for a workout tracking application used by personal trainers. Trainers can create workouts and reusable exercises, then attach any exercise to any workout with the sets, reps and/or duration used.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate and Marshmallow.

## Data model

| Model | Fields |
|---|---|
| **Exercise** | `id`, `name`, `category`, `equipment_needed` |
| **Workout** | `id`, `date`, `duration_minutes`, `notes` |
| **WorkoutExercise** (join table) | `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds` |

A `Workout` has many `Exercises` through `WorkoutExercises`, and an `Exercise` has many `Workouts` through `WorkoutExercises`. Deleting a workout or an exercise also deletes its `WorkoutExercise` rows.

## Validations

**Table constraints**
- `exercises.name` is NOT NULL, UNIQUE and must be non-empty (CHECK)
- `exercises.category` and `exercises.equipment_needed` are NOT NULL
- `workouts.date` and `workouts.duration_minutes` are NOT NULL; `duration_minutes > 0` (CHECK)
- `workout_exercises` has a UNIQUE (`workout_id`, `exercise_id`) pair and CHECKs that `reps`, `sets` and `duration_seconds` are non-negative

**Model validations** (`@validates`)
- Exercise `name` must be a non-empty string
- Exercise `category` must be one of `strength`, `cardio`, `flexibility`, `balance`, `mobility`
- Workout `duration_minutes` must be a positive integer and `date` must be a date
- WorkoutExercise `reps`, `sets` and `duration_seconds` must be non-negative integers when present

**Schema validations** (Marshmallow)
- Exercise `name` is 1–100 characters; `category` must be one of the allowed values (case-insensitive)
- Workout `duration_minutes` is required and between 1 and 1440; `notes` is at most 1000 characters
- WorkoutExercise amounts must be `>= 0`, and at least one of `reps`, `sets` or `duration_seconds` is required

## Installation

Requires Python 3.8+ and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone https://github.com/davidnjagih-png/workout-app.git
cd workout-app
pipenv install
pipenv shell
```

Create the database and load example data:

```bash
cd server
export FLASK_APP=app.py
flask db upgrade head
python seed.py
```

`seed.py` clears every table before inserting, so you can re-run it at any time to reset the data.

## Running

From the `server/` directory:

```bash
flask run --port 5555
# or
python app.py
```

The API is served at `http://localhost:5555`.

## Testing

From the repo root:

```bash
pipenv install --dev
pytest
```

The suite uses an in-memory SQLite database, so it never touches `app.db`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps/sets/duration |

### Request bodies

`POST /workouts`
```json
{ "date": "2026-10-20", "duration_minutes": 45, "notes": "Upper body" }
```

`POST /exercises`
```json
{ "name": "Push-Up", "category": "strength", "equipment_needed": false }
```

`POST /workouts/1/exercises/2/workout_exercises`
```json
{ "sets": 3, "reps": 12, "duration_seconds": null }
```

### Status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Record created |
| 204 | Record deleted (empty body) |
| 400 | Request failed a schema or model validation; `errors` explains which fields |
| 404 | Workout or exercise not found |
| 409 | Request violates a database constraint (e.g. duplicate exercise name, or the exercise is already in that workout) |
