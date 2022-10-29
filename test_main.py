import time

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

example_oob_interval = '?interval_id=PEPTIDE&charge=1&min_mass=1002&max_mass=1001&min_rt=1000&max_rt=1001&' \
                       'min_ook0=1000&max_ook0=1001&min_intensity=1000&max_intensity=1001'
example_interval = '?interval_id=PEPTIDE&charge=1&min_mass=1000&max_mass=1001&min_rt=1000&max_rt=1001&min_ook0=1000' \
                   '&max_ook0=1001&min_intensity=1000&max_intensity=1001'
example_interval_dict = \
    {
        "id": "PEPTIDE",
        "charge": 1,
        "min_mass": 1000,
        "max_mass": 1001,
        "min_rt": 1000,
        "max_rt": 1001,
        "min_ook0": 1000,
        "max_ook0": 1001,
        "min_intensity": 1000,
        "max_intensity": 1001
    }

example_point = '?charge=1&mass=1000.5&rt=1000.5&ook0=1000.5&intensity=1000.5'
example_points = '?charge=1&mass=1000.5&rt=1000.5&ook0=1000.5&intensity=1000.5&charge=1&mass=1000.5&rt=1000.5' \
                 '&ook0=1000.5&intensity=1000.5'


def test_post_exclusion():
    response = client.delete("/exclusion")
    assert response.status_code == 200


def test_post_exclusion_save():
    client.delete("/exclusion")

    response = client.post("/exclusion?save=True&exclusion_list_name=testing")
    assert response.status_code == 204

    response = client.delete("/exclusion/file?exclusion_list_name=testing")
    assert response.status_code == 200


def test_post_exclusion_load():
    client.delete("/exclusion")

    response = client.post("/exclusion?save=True&exclusion_list_name=testing")
    assert response.status_code == 204

    response = client.post("/exclusion?save=False&exclusion_list_name=testing")
    assert response.status_code == 204

    response = client.delete("/exclusion/file?exclusion_list_name=testing")
    assert response.status_code == 200


def test_post_exclusion_load_fail():
    client.delete("/exclusion")

    response = client.post("/exclusion?save=False&exclusion_list_name=testing")
    assert response.status_code == 404


def test_delete_exclusion_save_fail():
    client.delete("/exclusion")

    response = client.delete("/exclusion/file?exclusion_list_name=testing")
    assert response.status_code == 404


def test_save_load():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")  # add interval
    assert response.status_code == 204

    response = client.post("/exclusion?save=True&exclusion_list_name=testing")  # save
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")  # get intervals
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.post(f"/exclusion/interval{example_interval}")  # add interval
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")  # get intervals
    assert response.status_code == 200
    assert response.json() == [example_interval_dict, example_interval_dict]

    response = client.post("/exclusion?save=False&exclusion_list_name=testing")  # load
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")  # get intervals (should only be 1)
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]


def test_post_exclusion_interval():
    client.delete("/exclusion")

    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.post(f"/exclusion/interval{example_oob_interval}")
    assert response.status_code == 400


def test_get_exclusion_interval():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]


def test_get_exclusion_interval_by_id():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval?interval_id=PEPTIDE")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/interval?interval_id=PEPTIDE2")
    assert response.status_code == 404


def test_get_exclusion_interval_by_mass():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval?min_mass=1000&max_mass=1001")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/interval?max_mass=1001")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/interval?min_mass=1000")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/interval?min_mass=1001&max_mass=1000")
    assert response.status_code == 400

    response = client.get(f"/exclusion/interval?min_mass=1001")
    assert response.status_code == 404

    response = client.get(f"/exclusion/interval?max_mass=1000")
    assert response.status_code == 404


def test_delete_exclusion_interval():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.delete(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    # Test if interval was deleted, plus add the interval back in
    response = client.get(f"/exclusion/interval{example_interval}")
    assert response.status_code == 404
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204
    response = client.get(f"/exclusion/interval{example_interval}")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.delete(f"/exclusion/interval{example_oob_interval}")
    assert response.status_code == 400


def test_get_multiple_exclusion_interval():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict, example_interval_dict]


def test_delete_multiple_exclusion_interval():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.delete(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/interval{example_interval}")
    assert response.status_code == 404

    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204


def test_get_point():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/point{example_point}")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?charge=1")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?mass=1000")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?mass=1001")
    assert response.status_code == 404

    response = client.get(f"/exclusion/point?rt=1000")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?rt=1001")
    assert response.status_code == 404

    response = client.get(f"/exclusion/point?ook0=1000")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?ook0=1001")
    assert response.status_code == 404

    response = client.get(f"/exclusion/point?intensity=1000")
    assert response.status_code == 200
    assert response.json() == [example_interval_dict]

    response = client.get(f"/exclusion/point?intensity=1001")
    assert response.status_code == 404


def test_get_points():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    response = client.get(f"/exclusion/points{example_points}")
    assert response.status_code == 200
    assert response.json() == [True, True]


def test_add_interval_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    start_time = time.time()
    for i in range(100):
        client.post(f"/exclusion/interval{example_interval}")

    total_time = time.time() - start_time
    print(f'Interval Add time: {total_time}')
    assert total_time < 1


def test_get_interval_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    start_time = time.time()
    for i in range(100):
        client.get(f"/exclusion/interval{example_interval}")

    total_time = time.time() - start_time
    print(f'Interval Get time: {total_time}')
    assert total_time < 1


def test_head_interval_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    start_time = time.time()
    for i in range(100):
        client.head(f"/exclusion/interval{example_interval}")

    total_time = time.time() - start_time
    print(f'Interval Head time: {total_time}')
    assert total_time < 1


def test_get_point_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    start_time = time.time()
    for i in range(100):
        client.get(f"/exclusion/point{example_point}")

    total_time = time.time() - start_time
    print(f'Point Get time: {total_time}')
    assert total_time < 1


def test_head_point_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    start_time = time.time()
    for i in range(100):
        client.head(f"/exclusion/point{example_point}")

    total_time = time.time() - start_time
    print(f'Point Head time: {total_time}')
    assert total_time < 1


def test_get_points_performance():
    client.delete("/exclusion")
    response = client.post(f"/exclusion/interval{example_interval}")
    assert response.status_code == 204

    sub_str = '&charge=1&mass=1000.5&rt=1000.5&ook0=1000.5&intensity=1000.5'

    sub_strs = [sub_str] * 100
    sub_strs[0] = example_point
    points_query = ''.join(sub_strs)

    start_time = time.time()
    client.get(f"/exclusion/points{points_query}")

    total_time = time.time() - start_time
    print(f'Point Heads time: {total_time}')
    assert total_time < 1
