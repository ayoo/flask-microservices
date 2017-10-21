import json

from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


#helper functions
def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data =  response.json #json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])


    def test_add_user(self):
        with self.client:
            response = self.client.post(
                '/users',
                data = json.dumps(dict(
                    username='tester',
                    email='tester@test.com'
                )),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('tester@test.com was added!', data['message'])
        self.assertIn('success', data['status'])


    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])


    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if the JSON object does not have a username key."""
        with self.client:
            response = self.client.post(
                '/users',
                data = json.dumps(dict(email='tester@test.com')),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('fail', data['status'])


    def test_add_user_duplicate_user(self):
        """Ensure error is thrown if the email already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='test',
                    email='tester@test.com'
                )),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='tester',
                    email='tester@test.com'
                )),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])


    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = add_user('tester', 'tester@test.com')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('tester', data['data']['username'])
            self.assertIn('tester@test.com', data['data']['email'])
            self.assertIn('success', data['status'])


    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])


    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])


    def test_all_users(self):
        """Ensure get all users behave correctly."""
        add_user('tester1', 'tester1@test.com')
        add_user('tester2', 'tester2@test.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])
            self.assertIn('tester1', data['data']['users'][0]['username'])
            self.assertIn(
                'tester1@test.com', data['data']['users'][0]['email'])
            self.assertIn('tester2', data['data']['users'][1]['username'])
            self.assertIn(
                'tester2@test.com', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])


    def test_main_no_users(self):
        """Ensure the main route behaves correctly when no users have been added yet"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)


    def test_main_with_users(self):
        """Ensure the main route behaves correctly when users have been already added"""
        add_user('tester1', 'tester1@test.com')
        add_user('tester2', 'tester2@test.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'<strong>tester1</strong>', response.data)
        self.assertIn(b'<strong>tester2</strong>', response.data)


    def test_main_add_new_user(self):
        """Ensure a new user can be added to the database"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='tester1', email='tester1@test.com'),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>All Users</h1>', response.data)
        self.assertNotIn(b'<p>No users!</p>', response.data)
        self.assertIn(b'<strong>tester1</strong>', response.data)