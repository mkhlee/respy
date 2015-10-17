""" This script is used to generate some messages on QUANTIFIEDCODE 
to include an interesting dashboard in the presentation.
"""
#-------------------------------------------------------------------------------
# Minor Issue: Avoid untyped exception handlers
#-------------------------------------------------------------------------------
def divide(a, b):
    try:
      result = a / b
    except:
      result = None

    return result

#-------------------------------------------------------------------------------
# Critical: Import naming collision
#-------------------------------------------------------------------------------
from numpy import floor
from numpy import array
from math import floor # Overwrites already imported floor function

values = array([2.3, 8.7, 9.1])
  
#-------------------------------------------------------------------------------
# Potential Bug: Avoid nested loop joins
#-------------------------------------------------------------------------------
def get_number():
    while True:
        try:
            return int(input('Please enter a number: '))
        except ValueError:
            pass
            
#-------------------------------------------------------------------------------
# Recommendation: Comma-separated imports
#-------------------------------------------------------------------------------
from multiprocessing import Array, Pool
