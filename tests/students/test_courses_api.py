import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_retrieve_course(client, courses_factory, students_factory):
    courses = courses_factory(_quantity=10)
    course_id = courses[0].id
    response = client.get(f'/api/v1/courses/{course_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == courses[0].name
    assert data['id'] == courses[0].id


@pytest.mark.django_db
def test_list_courses(client, courses_factory):
    courses = courses_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, c in enumerate(data):
        assert c['name'] == courses[i].name


@pytest.mark.django_db
def test_filter_courses_id(client, courses_factory):
    courses = courses_factory(_quantity=9)
    index = 5
    course_id = courses[index].id
    response = client.get(f'/api/v1/courses/?id={course_id}')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == courses[index].id
    assert data[0]['name'] == courses[index].name


@pytest.mark.django_db
def test_filter_courses_name(client, courses_factory):
    courses = courses_factory(_quantity=10)
    index = 3
    course_name = courses[index].name
    response = client.get(f'/api/v1/courses/?name={course_name}')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == courses[index].id
    assert data[0]['name'] == courses[index].name


@pytest.mark.django_db
def test_create_course(client, students_factory):
    course_name = 'Python'
    students = students_factory(_quantity=5)
    students_list = {}
    for obj in students:
        student_id = obj.id
        student_name = obj.name
        student_birth = obj.birth_date
        students_list[student_id] = {'name': student_name, 'birth_date': student_birth}
    data = {
        'name': course_name,
        'students': students_list
    }
    response = client.post('/api/v1/courses/', data=data)
    resp_data = response.json()
    assert response.status_code == 201
    assert resp_data['name'] == course_name
    student_ids = list(students_list.keys())
    assert resp_data['students'] == student_ids


@pytest.mark.django_db
def test_update_course(client, courses_factory, students_factory):
    courses = courses_factory(_quantity=10)
    students = students_factory(_quantity=5)
    index = 6
    course = courses[index]
    course.name = 'Django DB'
    student_ids = [obj.id for obj in students]
    data = {
        'name':  course.name,
        'students': student_ids
    }
    response = client.patch(f'/api/v1/courses/{course.id}/', data=data)
    resp_data = response.json()
    assert response.status_code == 200
    assert resp_data['name'] == course.name
    assert resp_data['students'] == student_ids


@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    courses = courses_factory(_quantity=10)
    index = 9
    course = courses[index]
    response = client.delete(f'/api/v1/courses/{course.id}/')
    assert response.status_code == 204
    get_req = client.get(f'/api/v1/courses/{course.id}/')
    assert get_req.status_code == 404
