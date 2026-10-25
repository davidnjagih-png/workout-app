def test_list_workouts(client):
    res = client.get('/workouts')
    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_show_workout_includes_exercise_amounts(client):
    body = client.get('/workouts/1').get_json()
    link = body['workout_exercises'][0]
    assert link['exercise']['name'] == 'Squat'
    assert (link['sets'], link['reps']) == (3, 10)


def test_missing_workout_returns_404(client):
    assert client.get('/workouts/99').status_code == 404


def test_create_workout(client):
    res = client.post('/workouts', json={'date': '2026-10-10', 'duration_minutes': 30})
    assert res.status_code == 201
    assert res.get_json()['id'] == 2


def test_create_workout_schema_validation(client):
    res = client.post('/workouts', json={'date': '2026-10-10', 'duration_minutes': 0})
    assert res.status_code == 400
    assert 'duration_minutes' in res.get_json()['errors']


def test_delete_workout(client):
    assert client.delete('/workouts/1').status_code == 204
    assert client.get('/workouts/1').status_code == 404


def test_list_and_show_exercises(client):
    assert len(client.get('/exercises').get_json()) == 1
    body = client.get('/exercises/1').get_json()
    assert body['workout_exercises'][0]['workout']['notes'] == 'Legs'


def test_create_exercise_normalizes_category(client):
    res = client.post('/exercises', json={'name': 'Row', 'category': 'Cardio'})
    assert res.status_code == 201
    assert res.get_json()['category'] == 'cardio'


def test_create_exercise_schema_validation(client):
    res = client.post('/exercises', json={'name': '', 'category': 'dance'})
    assert res.status_code == 400
    assert set(res.get_json()['errors']) == {'name', 'category'}


def test_duplicate_exercise_returns_409(client):
    res = client.post('/exercises', json={'name': 'Squat', 'category': 'strength'})
    assert res.status_code == 409


def test_delete_exercise(client):
    assert client.delete('/exercises/1').status_code == 204
    assert client.get('/workouts/1').get_json()['workout_exercises'] == []


def test_add_exercise_to_workout(client):
    client.post('/exercises', json={'name': 'Plank', 'category': 'balance'})
    res = client.post('/workouts/1/exercises/2/workout_exercises',
                      json={'duration_seconds': 60})
    assert res.status_code == 201
    assert res.get_json()['duration_seconds'] == 60


def test_add_exercise_requires_an_amount(client):
    client.post('/exercises', json={'name': 'Plank', 'category': 'balance'})
    res = client.post('/workouts/1/exercises/2/workout_exercises', json={})
    assert res.status_code == 400


def test_add_exercise_to_missing_workout(client):
    res = client.post('/workouts/99/exercises/1/workout_exercises', json={'sets': 1})
    assert res.status_code == 404
