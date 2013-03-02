import os, sys, re
import string, StringIO, base64
import yaml, pycurl, urllib
from types import DictType, ListType

from xml.dom.minidom import parseString, Node
from BeautifulSoup import BeautifulStoneSoup

from ebaysdk import ebaybase
from ebaysdk.utils import xml2dict, dict2xml, list2xml
from ebaysdk.utils import make_struct, object_dict

class Permissions(ebaybase):
    pass

class Invoicing(ebaybase):
    pass

class AdaptivePayments(ebaybase):
    pass

class AdaptiveAccounts(ebaybase):
    """
    Finding backend for ebaysdk.
    http://developer.ebay.com/products/finding/

    11:06 RiverCityBob: Paypal sandbox account:
    11:06 RiverCityBob: rbradley@ebay.com/C00lbowtie
    11:06 RiverCityBob: Paypal corporate account:
    11:06 RiverCityBob: eseparent1@gmail.com/noodle123

    >>> api = AdaptiveAccounts()
    >>> args = {
    ...    'requestEnvelope.errorLanguage': 'en_US',
    ...    'emailAddress': 'tkeefer@gmail.com',
    ...    'firstName': 'Tim',
    ...    'lastName': 'Keefer',
    ...    'matchCriteria': "NAME"
    ... }
    >>> retval = api.execute('GetVerifiedStatus', args)        
    >>> error = api.error()
    >>> print error
    <BLANKLINE>

    >>> if len( error ) <= 0:
    ...   #print api.response_obj().itemSearchURL != ''
    ...   #items = f.response_obj().searchResult.item
    ...   #print len(items)
    ...   print f.response_dict()
    True
    100
    Success

    """

    def __init__(self,
        domain='svcs.ebay.com',
        service='AdaptiveAccounts',
        uri='/AdaptiveAccounts',
        https=True,
        response_encoding='JSON',
        request_encoding='XML',
        proxy_host=None,
        proxy_port=None,
        appid=None,
        certid=None,
        config_file='ebay.yaml',
        **kwargs):

        ebaybase.__init__(self, method='POST', **kwargs)

        self.api_config = {
            'domain'    : domain,
            'service'   : service,
            'uri'       : uri,
            'https'     : https,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
            'proxy_host': proxy_host,
            'proxy_port': proxy_port,
            'appid'     : appid,
            'certid'    : certid,
        }

        self.load_yaml(config_file)

    def _build_request_headers(self):
        return {
            "X-PAYPAL-SECURITY-USERID": self.api_config.get('userid',''),
            "X-PAYPAL-SECURITY-PASSWORD": self.api_config.get('password',''),
            "X-PAYPAL-SECURITY-SIGNATURE": self.api_config.get('certid',''),
#            "X-PAYPAL-APPLICATION-ID": self.app.config.get('PAYPAL_APP_ID'),
            "X-PAYPAL-REQUEST-DATA-FORMAT": 'NV',
            "X-PAYPAL-RESPONSE-DATA-FORMAT": 'JSON',

            "X-EBAY-SOA-SERVICE-NAME" : self.api_config.get('service',''),
            "X-EBAY-SOA-SERVICE-VERSION" : self.api_config.get('version',''),
            "X-EBAY-SOA-SECURITY-APPNAME"  : self.api_config.get('appid',''),
            "X-EBAY-SOA-GLOBAL-ID"  : self.api_config.get('siteid',''),
            "X-EBAY-SOA-OPERATION-NAME" : self.verb,
            "X-EBAY-SOA-REQUEST-DATA-FORMAT"  : self.api_config.get('request_encoding',''),
            "X-EBAY-SOA-RESPONSE-DATA-FORMAT" : self.api_config.get('response_encoding',''),
            "Content-Type" : "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"http://www.ebay.com/marketplace/search/v1/services\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml