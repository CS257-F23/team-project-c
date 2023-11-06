import unittest
from app import *


class TestHomepage(unittest.TestCase):
    """
    Tests for homepage()
    Author: Henry
    """
    def test_returns_correct_html(self):
        """homepage(): test that the route loads the expected page"""
        appTest = app.test_client() # get the client side of the app
        response = appTest.get("/").data # returns homepage
        self.assertIn(b"Introducing PySpill, an app designed for tracking pipeline spills", response)


class TestCompanyPage(unittest.TestCase):
    """
    Tests for company_page()
    """
    def test_invalid_company(self):
        """company_page(): Test correct response returned for non-existent company"""
        self.app = app.test_client()
        response = self.app.get('/search-by-company/results?company-name-search=dne', 
                                follow_redirects=True).get_data()
        self.assertIn(b'The company you entered was not found in our database.', response)


    def test_company_page_gives_correct_data(self):
        """company_page(): Requests data for conocophillips and checks that provides stats are correct. """
        self.app = app.test_client()
        response = self.app.get('/search-by-company/results?company-name-search=CONOCOPHILLIPS', 
                                follow_redirects=True).get_data()
        self.assertIn(b'4776.61', response)
    

class TestLocationPage(unittest.TestCase):
    """
    Tests for location_page()
    """
    def test_invalid_state(self):
        """location_page(): Askes the server to lookup a state not in the database. """
        self.app = app.test_client()
        response = self.app.get('/search-by-location/results?state-search=dne&county-search=&city-search=', 
                                follow_redirects=True).get_data()
        self.assertIn(b'The location you entered was not found in our database.', response)

    def test_state_stats_correct(self):
        """location_page(): Request state statistics and make sure correct stats displayed. """
        self.app = app.test_client()
        response = self.app.get('/search-by-location/results?state-search=tx&county-search=&city-search=', 
                                follow_redirects=True).get_data()
        self.assertIn(b'135579.99', response)


    def test_county_stats_correct(self):
        """location_page(): Request county statistics and make sure correct stats displayed. """
        self.app = app.test_client()
        response = self.app.get('/search-by-location/results?state-search=co&county-search=weld&city-search=', 
                                follow_redirects=True).get_data()
        self.assertIn(b'1302.06', response)


    def test_city_stats_correct(self):
        """location_page(): Request city statistics and make sure correct stats displayed. """
        self.app = app.test_client()
        response = self.app.get('/search-by-location/results?state-search=al&county-search=mobile&city-search=', 
                                follow_redirects=True).get_data()
        self.assertIn(b'3.0', response)
        

class TestPageNotFound(unittest.TestCase):
    """ Tests for error 404 page. """
    def test_404_page_returned_on_bad_url(self):
        """page_not_found(): Attempts to GET an unknown URL and expects a 404 error page to be returned. """
        self.app = app.test_client()
        response = self.app.get('/dne', follow_redirects=True).get_data()
        self.assertIn(b'Uh oh, the page you were looking for was not found.', response)


class TestGetLocationName(unittest.TestCase):
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
        result = get_location_name(self.state, "", self.city)
        self.assertEqual(result, "Faribault, MN")


    def test_return_state_county(self):
        """get_location_name(): test correct return for state/county input"""
        result = get_location_name(self.state, self.county, "")
        self.assertEqual(result, "Rice County, MN")


    def test_return_state(self):
        """get_location_name(): test correct return for state input"""
        result = get_location_name(self.state, "", "")
        self.assertEqual(result, "MN")
        
