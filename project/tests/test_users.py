import json
from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


class TestUserService(BaseTestCase):
    def test_ping(self):
        """确保ping服务正常"""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """确保能正确添加一个用户到数据库中"""

        with self.client:
            response = self.client.post(
                '/user',
                data=json.dumps(
                    dict(username='cnych', email='qikaqiak@gmail.com')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('qikaqiak@gmail.com was add', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """如果json对象为空, 确保抛出一个错误"""
        with self.client:
            response = self.client.post('/user',
                                        data=json.dumps(dict()),
                                        content_type='application/json')
            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """如果JSON对象中没有username或email，确保抛出一个错误。"""
        with self.client:
            response = self.client.post('/user',
                                        data=json.dumps(
                                            dict(email='qikqiak@gmail.com')),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

        with self.client:
            response = self.client.post('/user',
                                        data=json.dumps(
                                            dict(username='cnych')),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_duplicate_user(self):
        """如果邮件已经存在确保抛出一个错误。"""
        with self.client:
            self.client.post('/user',
                             data=json.dumps(
                                 dict(username='cnych',
                                      email='qikqiak@gmail.com')),
                             content_type='application/json')
            response = self.client.post('/user',
                                        data=json.dumps(
                                            dict(username='cnych',
                                                 email='qikqiak@gmail.com')),
                                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user(self):
        """确保能正确获取用户信息"""
        user = User(username='cnych', email='qikqiak@gmail.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get('/user/%d' % user.id)
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual('cnych', data['data']['username'])
            self.assertEqual('qikqiak@gmail.com', data['data']['email'])
            self.assertEqual('success', data['status'])

    def test_get_user_no_id(self):
        """如果没有id的时候抛出异常"""
        with self.client:
            response = self.client.get('/user/xxx')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Param id error', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_incorrect_id(self):
        """如果ID不存在则要抛出异常"""
        with self.client:
            response = self.client.get('/user/1111')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_list(self):
        """正确获得用户列表"""
        with self.client:
            response = self.client.get('/user/list')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('users', data['data'])
            self.assertTrue(isinstance(data['data']['users'], list))
            self.assertIn('success', data['status'])