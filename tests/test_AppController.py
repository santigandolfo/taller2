import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
from controllers import AppController
import re
def test_1():
  ret_value = "value"
  assert b"value" in ret_value

def test_2():
  ret_value = 2
  assert 1 + 1 == ret_value

#Check if it is a html header
def test_dummy():

  assert re.match("<h1 style='text-align: center; color:blue;'>App running!</h1>",AppController.index())
  
