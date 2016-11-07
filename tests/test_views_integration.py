import flask_login
import os
import unittest
import urllib
from urllib.parse import urlparse
import parse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True

    def test_add_entry(self):
        self.simulate_login()

        response = self.client.post("/entry/add", data={
            "title": "Test Entry",
            "content": "Test content"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)

    def test_delete_entry(self): 
        self.simulate_login()
        self.test_add_entry()
        entries = session.query(Entry).all()
        entry = entries[0].id
        response = self.client.post("/entry/{0}/delete".format(entry))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 0)
        
    def test_edit_entry(self):
        self.simulate_login()
        self.test_add_entry()
        entries = session.query(Entry).all()
        entry = entries[0].id
        response = self.client.post("/entry/{0}/edit".format(entry), data={
            "title": "Edited Entry",
            "content": "Edited Content"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        entry = entries[0]
        print(entry.title, entry.content, entry.author)
        self.assertEqual(entry.title, "Edited Entry")
        self.assertEqual(entry.content, "Edited Content")
        self.assertEqual(entry.author, self.user)
        
        
if __name__ == "__main__":
    unittest.main()