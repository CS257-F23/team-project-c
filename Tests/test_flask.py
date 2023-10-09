import unittest
from app import *


"""
Functions to test: 

homepage()

company()

location()

empty_string_to_none() - Henry

get_location_name() - Henry

"""
class Test_homepage(unittest.TestCase):
    """
    Tests for homepage()
    Author:
    """
    def test_returns_correct_html(self):
        """homepage(): test that the route loads the expected page"""
        appTest = app.test_client() # get the client side of the app
        response = appTest.get("/").data # returns homepage
        self.assertTrue(b"Welcome to PySpill" in bytes(response)) # check that an expected part of the page is in the page

class Test_company_page(unittest.TestCase):
    """
    Tests for company_page()
    Author:
    """
    
class Test_location_page(unittest.TestCase):
    """
    Tests for location_page()
    Author:
    """

class Test_empty_string_to_none(unittest.TestCase):
    """
    Tests for empty_string_to_none()
    Author: Henry
    """

    def test_return(self):
        """empty_string_to_none(): test correct return for None, empty string, and non-empty string inputs"""
        result = empty_string_to_none(" ")
        self.assertTrue(result is None)

        result = empty_string_to_none(None)
        self.assertTrue(result is None)

        result = empty_string_to_none("non empty")
        self.assertEqual(result, "non empty")
        
        

class Test_get_location_name(unittest.TestCase):
    """
    Tests for get_location_name()
    Author: Henry
    """
    state, county, city = "MN", "Rice", "Faribault"

    def test_return_full(self):
        """get_location_name(): test correct return for full input"""
        result = get_location_name(self.state, self.county, self.city)
        self.assertEqual(result, "Faribault, Rice County, MN")


    def test_return_state_city(self):
        """get_location_name(): test correct return for state/city input"""
        result = get_location_name(self.state, None, self.city)
        self.assertEqual(result, "Faribault, MN")


    def test_return_state_county(self):
        """get_location_name(): test correct return for state/county input"""
        result = get_location_name(self.state, self.county, None)
        self.assertEqual(result, "Rice County, MN")


    def test_return_state(self):
        """get_location_name(): test correct return for state input"""
        result = get_location_name(self.state, None, None)
        self.assertEqual(result, "MN")
        
