import os
import unittest
import multiprocessing
import time
import urllib
from urllib.parse import urlparse
import werkzeug
from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)
        
    def test_login_correct(self):
        #self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        print(self.browser.is_text_present('Login'))
        print(self.browser.is_text_present('Logout', wait_time=2))
        print(self.browser.is_text_not_present('Logout'))
        
    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
        self.browser.is_text_present('Login')
        self.browser.is_text_not_present('Logout')
        
    def test_logout(self):
        self.test_login_correct()
        print('Logged in')
        logout_link = self.browser.find_link_by_text('Logout')
        print(self.browser.is_text_present('Logout'))
        print('Logout link found')
        logout_link.click()
        print('Logout link clicked')
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        self.browser.is_text_present('Login')
        self.browser.is_text_not_present('Logout')
        print('Login link displayed, Logout link not displayed')


    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()