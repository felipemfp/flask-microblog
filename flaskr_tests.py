import os
import flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_file = tempfile.mkstemp()
        flaskr.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_file
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_file)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
                username=username,
                password=password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in str(rv.data)

    def test_login_logout(self):
        rv = self.login('admin', 'admin')
        assert 'You were logged in' in str(rv.data)
        rv = self.logout()
        assert 'You were logged out' in str(rv.data)
        rv = self.login('adminx', 'admin')
        assert 'Invalid username' in str(rv.data)
        rv = self.login('admin', 'adminx')
        assert 'Invalid password' in str(rv.data)

    def test_messages(self):
        self.login('admin', 'admin')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in str(rv.data)
        assert '&lt;Hello&gt;' in str(rv.data)
        assert '<strong>HTML</strong> allowed here' in str(rv.data)


if __name__ == '__main__':
    unittest.main()
