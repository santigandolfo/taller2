import sys
sys.path.append('..')
from src.controllers import AppController
import re
def test_1():
  ret_value = "value"
  assert b"value" in ret_value

def test_2():
  ret_value = 2
  assert 1 + 1 == ret_value

#Check if it is a html header
def test_dummy():

  assert re.match("<h(\d)>[\s\w\d\s]*<\/h\1>",AppControler.index())
  
