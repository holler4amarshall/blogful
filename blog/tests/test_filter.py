import os
import unittest
import datetime


# Configure app to use the testing configuration: 
if not "CONFIG_PATH" in os.environ:
    os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

import blog
from blog.filters import *

class FilterTests(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()