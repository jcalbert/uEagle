__author__ = 'Joseph Albert'
__copyright__ = ''
__license__ = ''
__version__ = ''


from ubinascii import b2a_base64
import urequests
import ujson
import utime

ADDR_TEMPLATE = r'http://eagle-{0}.local/cgi-bin/post_manager'

CMD_TOP_TEMPLATE = r'''<Command>\n
                   <Name>{0!s}</Name>\n
                   <Format>JSON</Format>'''

from sys import platform
if platform in ('linux', 'unix'):
    EPOCH_DELTA = 946684800
else:
    EPOCH_DELTA = 0
del(platform)

class Eagle(object):
    def __init__(self, cloud_id, install_code):
        self.addr = ADDR_TEMPLATE.format(cloud_id)
        self.auth = encode_basic_auth(cloud_id, install_code)

        self._headers = {'Authorization':self.auth,
                        'Content-Type'  :'application/xml'}

    def make_cmd(self, command, **kws):
        cmd_str  = CMD_TOP_TEMPLATE.format(command)

        for k,v in kws.items():
            cmd_str += '<{0}>{1!s}</{0}>\n'.format(k, v)

        cmd_str += '</Command>\n'
        return cmd_str

    def post_cmd(self, command, **kws):
        data = self.make_cmd(command, **kws)
        response =  urequests.post(self.addr,
                                   headers=self._headers,
                                   data=data)
        return ujson.loads(response.text)

    #No extra args
    def get_network_info(self):
        return self.post_cmd('get_network_info')

    def list_network(self): #Need XML interp
        raise NotImplementedError()

    def get_network_status(self):
        return self.post_cmd('get_network_status')

    def get_instantaneous_demand(self):
        return self.post_cmd('get_instantaneous_demand')

    def get_price(self):
        return self.post_cmd('get_price')

    def get_message(self):
        return self.post_cmd('get_message')

    def confirm_message(self): #Need args
        raise NotImplementedError()

    def get_current_summation(self):
        return self.post_cmd('get_current_summation')

    def get_history_data(self): #Need args
        raise NotImplementedError()

    def set_schedule(self): #Need args
        raise NotImplementedError()

    def get_schedule(self): #Need args
        raise NotImplementedError()

    def reboot(self): #Need args
        raise NotImplementedError()

    def get_demand_peaks(self):
        return self.post_cmd('get_demand_peaks')

#Courtesy of fschmi PR on micropython-lib
def encode_basic_auth(username, password):
    formated = b"{}:{}".format(username, password)
    formated = b2a_base64(formated)[:-1].decode("ascii")
    return 'Basic {}'.format(formated)

def convert_response(d):
    '''
    Given a response dict from the EAGLE, interpret common data
    types / apply conversions.
    '''
    #Handle nested dictionaries
    for k,v in d.items():
        if isinstance(v,dict):
            convert_response(v)
    #Summation and demand conversion
    if 'Multiplier' in d:
        convert_demand(d)

    if 'Price' in d:
        convert_price(d)

    if 'TimeStamp' in d:
        d['TimeStamp'] = utime.localtime(int(d['TimeStamp']) + EPOCH_DELTA)

def convert_demand(d):
    factor = max(int(d['Multiplier']), 1) / max(int(d['Divisor']), 1)

    if 'Demand' in d:
        d['Demand'] = int(d['Demand']) * factor
    else:
        d['SummationDelivered'] = int(d['SummationDelivered']) * factor
        d['SummationReceived'] = int(d['SummationReceived']) * factor

    del(d['Multiplier'])
    del(d['Divisor'])
    del(d['DigitsRight'])
    del(d['DigitsLeft'])
    del(d['SuppressLeadingZero'])

def convert_price(d):
    d['Price'] = int(d['Price']) / 10**int(d['TrailingDigits'])
    d['Currency'] = int(d['Currency'])

    del(d['TrailingDigits'])

#notes
#More recent API (1.1) supports command list_network
##list_network does not return JSON
##gets info on all network interfaces
#
#When running locally, API Commands to not actually require MAC address

#Since this is python3 compatible, we assumme int / int = float

#the EAGLE's Epoch is 01-01-2000, rather than unix's 1970.
#Each command needs:
# POST with
## headers: auth
## body: xml
#<Command>
# 	<Name>COMMAND</Name>
# 	<Format>JSON</Format>
#   <MAYBE OTHER OPTIONS>
#</Command>
