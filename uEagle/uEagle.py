import requests
import json
import time

MDNS_TEMPLATE = r'http://{0}:{1}@eagle-{0}.local/cgi-bin/post_manager'
ADDR_TEMPLATE = r'http://{0}:{1}@{2}/cgi-bin/post_manager'

CMD_TOP_TEMPLATE = r'''<Command>\n
                   <Name>{0!s}</Name>\n
                   <Format>JSON</Format>'''

#Options
SAFETY_ON = True

#Enumerations
if SAFETY_ON:
    PROTOCOL_VALS = ('ZigBee',)
    STATUS_VALS   = ('Initializing', 'Network', 'Discovery', 'Joining',
                     'Join: Fail', 'Join: Success', 'Authenticating',
                     'Authenticating: Success', 'Authenticating: Fail',
                     'Connected', 'Disconnected', 'Rejoining')
    YESNO_VALS    = ('Y', 'N')
    PRIORITY_VALS = ('Low', 'Medium', 'High', 'Critical')
    QUEUE_VALS    = ('Active', 'Cancel Pending')
    EVENT_VALS    = ('', 'time', 'message', 'price', 'summation', 'demand',
                     'scheduled_prices', 'profile_data', 'billing_period',
                     'block_period')
    TARGET_VALS   = ('Zigbee', 'Eagle', 'All')


from sys import platform
if platform in ('linux', 'unix'):
    EPOCH_DELTA = 946684800
else:
    EPOCH_DELTA = 0
del(platform)


class Eagle(object):
    def __init__(self, cloud_id, install_code, address=None):
        self._headers = {'Content-Type'  :'application/xml'}

        if address is not None:
            self.addr = ADDR_TEMPLATE.format(cloud_id, install_code, address)
        else:
            self.addr = MDNS_TEMPLATE.format(cloud_id, install_code)

    def make_cmd(self, command, **kws):
        cmd_str  = CMD_TOP_TEMPLATE.format(command)

        for k,v in kws.items():
            cmd_str += '<{0}>{1!s}</{0}>\n'.format(k, v)

        cmd_str += '</Command>\n'
        return cmd_str

    def post_cmd(self, command, **kws):
        post_data = self.make_cmd(command, **kws)
        response = requests.post(self.addr,
                                  headers=self._headers,
                                  data=post_data)

        response_text = TEMP_RESPONSE_FIX(response.text)
        data = json.loads(response_text)
        process_data(data)
        return data

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
        raise NotImplementedError('uEagle is read-only for now.')

    def get_current_summation(self):
        return self.post_cmd('get_current_summation')

    def get_history_data(self, start_time, end_time=None, frequency=None): #Need args
        kw = {'StartTime' : hex(int(start_time - EPOCH_DELTA))}

        if end_time is not None:
            kw['EndTime'] = hex(int(end_time - EPOCH_DELTA))

        if frequency is not None:
            if SAFETY_ON:
                if frequency > 0xffff or frequency < 0:
                    raise ValueError('frequency must be between 0 and 65535 seconds')
            kw['Frequency'] = hex(int(frequency))

        return self.post_cmd('get_history_data', **kw)

    def set_schedule(self): #Need args
        raise NotImplementedError('uEagle is read-only for now.')

    def get_schedule(self, event=None):
        if event is None:
            event = ''

        if SAFETY_ON and event not in EVENT_VALS:
            raise ValueError('\'{}\' is not a valid event'.format(event))
        return self.post_cmd('get_schedule', Event=event)

    def reboot(self): #Need args
        raise NotImplementedError('uEagle is read-only for now.')

    def get_demand_peaks(self):
        return self.post_cmd('get_demand_peaks')

#Courtesy of fschmi PR on micropython-lib
def encode_basic_auth(username, password):
    formated = b"{}:{}".format(username, password)
    formated = b2a_base64(formated)[:-1].decode("ascii")
    return 'Basic {}'.format(formated)

def process_data(d):
    '''
    Given a response dict from the EAGLE, interpret common data
    types / apply conversions.
    '''
    #Handle nested dictionaries
    for k,v in d.items():
        if isinstance(v,dict):
            process_data(v)
        elif isinstance(v,list):
            for vi in v:
                process_data(vi)

    #Summation and demand conversion
    if 'Multiplier' in d:
        convert_demand(d)

    if 'Price' in d:
        convert_price(d)

    if 'TimeStamp' in d:
        d['TimeStamp'] = time.localtime(int(d['TimeStamp'], 0) + EPOCH_DELTA)

def convert_demand(d):
    factor = max(int(d['Multiplier'], 0), 1) / max(int(d['Divisor'], 0), 1)

    if 'Demand' in d:
        d['Demand'] = int(d['Demand'], 0) * factor
    else:
        d['SummationDelivered'] = int(d['SummationDelivered'], 0) * factor
        d['SummationReceived'] = int(d['SummationReceived'], 0) * factor

    del(d['Multiplier'])
    del(d['Divisor'])
    del(d['DigitsRight'])
    del(d['DigitsLeft'])
    del(d['SuppressLeadingZero'])

def convert_price(d):
    d['Price'] = int(d['Price'], 0) / 10**int(d['TrailingDigits'], 0)
    d['Currency'] = int(d['Currency'], 0)

    del(d['TrailingDigits'])

def TEMP_RESPONSE_FIX(s):
    '''
    The EAGLE API provides malformed responses for some commands.  This
    function tries to fix them (until the firmware is patched).
    '''
    if s.startswith('\"HistoryData\"'):
        return '{' + s + '}'
    elif s.startswith('\"ScheduleList\"'):
        return '{' + s + '}'
    return s

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
