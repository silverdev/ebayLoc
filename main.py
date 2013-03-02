#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from ebaysdk import finding
from collections import Counter
from geopy import geocoders
import logging

cache_zip = {}

class ebaySearcher :
    def __init__(self) :
        self.api = finding(appid="corbinso-0418-4f1f-9512-0758cbf2744c")
        self.zip_counter=0 #counts the number of buyers from this zipcode
        self.avg_price=0
        self.zip_price=0
        self.num_items =0 #the number of results
    def search(self,term) :
        self.api.execute('findItemsByKeywords', {'keywords': term,
                                                 'paginationInput' :
                                                     {'entriesPerPage' : '100', 'pageNumber' : '1'},
                                                 'itemFilter' : {'name' : 'ListingType',
                                                                 'value' : ["FixedPrice", "AuctionWithBIN"]}
                                                 })


        find_output = self.api.response_dict()
        items= find_output['searchResult']['item']
        pages_to_scan=find_output['paginationOutput']['totalPages']['value']
        if pages_to_scan > 15:
            pages_to_scan = 14
            for x in xrange(2,pages_to_scan) :
                self.api.execute('findItemsByKeywords', {'keywords': term,
                                                         'paginationInput' :  {'entriesPerPage' : '100',
                                                                               'pageNumber' : str(x)},
                                                         'itemFilter' : {'name' : 'ListingType',
                                                                         'value' : ["FixedPrice", "AuctionWithBIN"]}
                                                         })

        find_output = self.api.response_dict()
        items.extend(find_output['searchResult']['item'])

        self.avg_price=0
        self.zip_counter=Counter()
        self.zip_price=Counter()
        self.num_items= len (items)
        for i in  items :
            try :
                self.zip_counter[i['postalCode']['value']]+=1;
                if i['listingInfo']['buyItNowAvailable']['value'] =="true" :
                    price = float(i['listingInfo']['buyItNowPrice']['value'])
                else :
                    price = float(i['sellingStatus']['convertedCurrentPrice']['value'])
                    self.avg_price+=price
                    self.zip_price[i['postalCode']['value']]+=price;

            except KeyError :
                self.num_items -=1
        self.avg_price/=self.num_items






front_html_b = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>Ebay Tracker</title>

    <style type="text/css">
    #map {
    width: 960px;
    height: 690px;
    }
    </style>

    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>

    <script type="text/javascript">
    /**
    * Called on the intiial page load.
    */
    function init() {
    var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 5,
    center: new google.maps.LatLng(44, -80),
    mapTypeId: google.maps.MapTypeId.ROADMAP

    });

"""

front_html_m = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>Ebay Tracker</title>

    <style type="text/css">
    #map {
    width: 320px;
    height: 480px;
    }
    </style>

    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>

    <script type="text/javascript">
    /**
    * Called on the intiial page load.
    */
    function init() {
    var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 5,
    center: new google.maps.LatLng(44, -80),
    mapTypeId: google.maps.MapTypeId.ROADMAP

    });

    """

center_html = """
    function circle(x,y,r,c) {
    var populationOptions = {
    strokeColor: "#FFFF00",
    strokeOpacity: 0.1,
    strokeWeight: 2,
    fillColor: c,
    fillOpacity: 0.12,
    map: map,
    center: new google.maps.LatLng(x, y),
    radius: r
    };


    cityCircle = new google.maps.Circle(populationOptions);
    }

    }

    // Register an event listener to fire once when the page finishes loading.
    google.maps.event.addDomListener(window, 'load', init);
    </script>


    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load("visualization", "1", {packages:["corechart"]});
    google.setOnLoadCallback(drawChart);
    function drawChart() {
    var data = google.visualization.arrayToDataTable([

    """
back_html_b = """
    ]);
    var options = {
    title: '"""


super_back_b = """',
    backgroundColor: '#EBF5F6',
    colors: ['#D94F36','#ABBC6B','#87B8BB'],
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
    }
    </script>
    </head>
    <body>
    <div id="map"></div>
    <div id="chart_div" style="width: 400; height: 200px; position:absolute; bottom: 0; right: 0;"></div>
    </body>
    </html>
"""

back_html_m = """
    ]);
    var options = {
    title: '"""



super_back_m = """'
    };

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
    }
    </script>
    </head>
    <body>
    <div id="map"></div>
    <div id="chart_div" style="width: 330px; height: 100px; position:absolute; bottom: 0; left: 0;"></div>
    </body>
    </html>
    """

cache_graph = {}
cache_data = {}


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello')


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        test = self.request.get('q')
        if test == None:
            test = 'iPad'
        
        if test in cache_data.keys():
            self.response.write(front_html_b+cache_graph[test]+center_html+cache_data[test]+back_html_b+test+super_back_b)
            return
        
        (additions,data) = getDataForSearch(test)
                
        map_string = ''
        for s in additions:
            map_string += s

        data_string = ''
        for d in data:
            data_string += d

        
        cache_graph[test] = map_string
        cache_data[test] = data_string
        
        self.response.write(front_html_b+map_string+center_html+data_string+back_html_b+test+super_back_b)

class MobileSearchHandler(webapp2.RequestHandler):
    def get(self):
        test = self.request.get('q')
        
        if test in cache_data.keys():
            self.response.write(front_html_m+cache_graph[test]+center_html+cache_data[test]+back_html_m+test+super_back_m)
            return
        
        (additions,data) = getDataForSearch(test)

        map_string = ''
        for s in additions:
            map_string += s

        data_string = ''
        for d in data:
            data_string += d

        cache_graph[test] = map_string
        cache_data[test] = data_string
        
        self.response.write(front_html_m+map_string+center_html+data_string+back_html_m+test+super_back_m)

app = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/hack/', SearchHandler),
        ('/hackm/', MobileSearchHandler),
        ], debug=True)


def getCircleString(long,lat,radius,color="FF0F0F"):
    string = 'circle('+str(long)+','+str(lat)+','+str(30000*radius)+',"%s");' % color
    return string

def getDataString(x,y):
    return "['%s',%i]," % (x,y)

searcher=ebaySearcher()

def getDataForSearch(search):

    gd = geocoders.GeoNames()
    searcher.search(search)
    cites=searcher.zip_counter

    additions = []
    for city in cites :
        try:
            coords= gd.geocode("US  "+str(city),exactly_one=False)[0][1]
            additions.append(getCircleString(coords[0] ,coords[1], cites[city]))
        except TypeError : pass


    city_prices=searcher.zip_price
    avg_price=searcher.avg_price
    num_items = searcher.num_items

    data = ["['City', 'P'],"]
            
    
    for i, city in enumerate(city_prices.most_common(10)):
        if i < 7:
            data.append(getDataString(str(city[0]),city[1]/cites[city[0]]))
        



    """data = [   "['Year', 'Sales'],",
               getDataString(2004,1000),
               "['2005',  1170],",
               "['2006',  660],",
               "['2007',  830],",
               "['2008',  1230],",
               "['2009',  830],",
               "['2010',  1230],"]"""


    return (additions,data)
