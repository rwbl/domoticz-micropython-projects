"""
File:	espserver.py
Date:	20230414
Author:	Robert W.B. Linn
:description
Class to manage the ESP8266 RESTful webserver.
Commands set via HTTP GET or POST requests with HTTP response JSON object.
:examples
***HTTP GET***
LED ON: http://esp-ip/led1/on with HTTP response: {"status": "OK", "title": "/led1/on", "message": "On"}
LED OFF: http://esp-ip/led1/off with HTTP response: {"status": "OK", "title": "/led1/off", "message": "Off"}
LED STATE: http://esp-ip/led1/state with HTTP response: {"status": "OK", "title": "/led1/state", "message": "On"}
In case of error, the HTTP response:
{"status": "ERROR", "title": "/led1/x", "message": "Unknown command."}
[Thonny Log]
LEDControl Network GET v20230310
Network connected OK
Network IP esp-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command /led1/on
HTTP Response {"title": "/led1/on", "message": "On", "status": "OK"}
Network connection closed
***HTTP POST***
LED ON: curl -v -H "Content-Type: application/json" -d "{\"state\":1}" http://esp-ip
{"status": "OK", "title": {"state": 1}, "message": 1}
LED OFF: curl -v -H "Content-Type: application/json" -d "{\"state\":0}" http://esp-ip
LED OFF: curl -v -H "Content-Type: application/json" -d "{\"state\":0}" http://esp-ip
{"status": "OK", "title": {"state": 0}, "message": 0}
In case of error (like JSON object not valid = can be be parsed), the HTTP response:
HTTP Response: {"status": "ERROR", "title": "{state:vvv}", "message": "Unknown command."}
with console log [ERROR] HTTP POST request not valid (ValueError).
:notes
When using curl ensure to escape the " to \" in the JSON object.
:log
esp8266-ledremotecontrol v20230413
#18 ets_task(4020f560, 28, 3fff9f40, 10)
Network waiting for connection...
Network connected OK
Network IP esp-ip
Network listening on ('0.0.0.0', 80)
Network client connected from client-ip
HTTP Command=/led1/off
HTTP Response={"title": "/led1/off", "message": "Off", "status": "OK"}
Network connection closed
"""
# Libraries
import network
import urequests
import socket
import time
from machine import Pin
import json
"""
Class Server
"""
class Server:
    # Constants
    NAME = 'ESPServer'
    VERSION = 'v20230414'
    CRLF = chr(13) + chr(10)
    SPACE = chr(32)
    # Domoticz
    # HTTP response JSON keys
    KEY_STATE	= 'status'
    KEY_TITLE	= 'title'
    KEY_MESSAGE	= 'message'
    # Messages used for HTTP response
    STATE_OK			= 'OK'
    STATE_ERR			= 'ERROR'
    MESSAGE_EMPTY		= ''
    MESSAGE_UNKNOWN		= 'Unknown'
    MESSAGE_CMD_UNKNOWN	= 'Unknown command.'
    MESSAGE_ON			= 'On'
    MESSAGE_OFF			= 'Off'
    def __init__(self, wifi_ssid, wifi_password, STATUS_PIN=16, DEBUG=True):
        """
        Init the network with defaults.
        
        :param string wifi_ssid
            SSID of the network to connect
            
        :param string wifi_password
            Passord of the network to connect
            
        :param string | int STATUS_PIN
            Pin number of the LED indicating network status connected
            For an NodeMCU this is GPIO16 (pin #D0)
            
        :param bool DEBUG
            Flag to set the log for debugging purposes
        """
        self.debug = DEBUG
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        # Create the onboard LED object to indicate controller is up and network connected
        self.ledstatus = Pin(STATUS_PIN, Pin.OUT)
        self.ledstatus.off()
    def log(self, msg):
        """
        Log to the console if debug flag is true.
        
        :param string msg
            Message to print
        """
        if self.debug:
            print(msg)
    def connect(self):
        """
        Connect to the network using the class SSID and password.
        :param None
        :return object server
            Server object.
        
        :example
            # Create network object
            network = Server(config.WIFI_SSID, config.WIFI_PASSWORD)
            # Connect to the network and get the server object
            server = network.connect()
        """
        try:
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                wlan.active(False)
            wlan.active(True)
            wlan.connect(self.wifi_ssid, self.wifi_password)
            # Network connection
            max_wait = 10
            self.log('Network waiting for connection...')
            while wlan.isconnected() == False:
                if wlan.status() < 0 or wlan.status() >= 3:
                    break
                max_wait -= 1
                pass
                max_wait -= 1
            if wlan.isconnected() == False:
                self.ledstatus.off()
                raise RuntimeError('[ERROR] Network connection failed!')
            else:
                self.ledstatus.on()
                self.log('Network connected OK')
                status = wlan.ifconfig()
                self.log('Network IP ' + status[0] )
            # Network Get address
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            # Network Create the server socket
            server = socket.socket()
            # Option to reuse addr to avoid error EADDRINUSE
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind the address befor starting to listen for icoming client connections
            server.bind(addr)
            server.listen(1)
            self.log('Network listening on ' + str(addr))
            # self.log(server)
            return server
        except OSError as e:
            self.ledstatus.off()
            cl.close()
            raise RuntimeError('[ERROR] Network connection closed')
    def parse_get_request(self, request):
        """
        Parse the command from the HTTP GET Request.
        The first line of the request contains the command.
        The first line is split and the 2nd item holds the command + data.
        Example first line with the command:
        GET /led1/on HTTP/1.1
        The command is /led1/on.
        
        :param string request
            HTTP GET request
        
        :return string command
            Command, i.e. /led1/on
            
        :return int status
            0 = Error, 1 = OK
        :example
            # Parse the get data. In case of error, the status is 0.
            cmd, status = network.parse_get_request(request)
        """
        status = 0
        cmd = self.MESSAGE_CMD_UNKNOWN
        
        # Split the decoded request string into a list
        data = str(request.decode()).split(self.CRLF)
        
        # Check if there is data to get the first item
        if (len(data) > 0):
            # print(data[0])
            # Split the first item which is the command string into a list with 3 items
            cmds = data[0].split(self.SPACE)
            # Check length and get the 2nd item, i.e. /led1/on
            if len(cmds) == 3:
                cmd = cmds[1]
                status = 1
            else:
                print('[ERROR] HTTP GET number of command items invalid. Expect 3, got ' + len(cmds))
        else:
            print('[ERROR] HTTP GET request not valid.')
        self.log('HTTP Command=' + cmd)
        
        # Return the command, i.e. /led1/on etc.
        return cmd, status
    
    def parse_post_request(self, request):
        """
        Parse the command from the HTTP POST Request.
        The last line of the HTTP request contains the command + data.
        The HTTP request is decoded and split as a string list.
        The last line is a JSON object with key:value pair(s).
        :param string request
            HTTP request
        :return string command
            Command as JSON key:value pair(s), i.e. {"led":1}
            
        :return int status
            0 = Error, 1 = OK
        :example
            # Parse the post data. In case of error, the status is 0.
            data, status = network.parse_get_request(request)
        """
        status = 0
        cmd = self.MESSAGE_CMD_UNKNOWN
        # Split the decoded request string into a list
        data = str(request.decode()).split(self.CRLF)
        
        # Check if there is data to get the last item
        # At least 8 items
        if (len(data) > 7):
            # JSON parse the last list item holding the command as JSON string
            # Convert the string to a JSON object
            try:
                cmd = json.loads(data[len(data) - 1])
                status = 1
            except ValueError:
                # In case the JSON data can not be parsed
                cmd = data[len(data) - 1]
                print('[ERROR] HTTP POST request not valid (ValueError).')            
        else:
            print('[ERROR] HTTP POST request not valid (Not enought items, must be 8 or more).')
        self.log('HTTP Command=' + cmd)
        
        # Return the command as JSON object, i.e. HTTP Command: {'state': 'on'}
        return cmd, status
    def get_client_connection(self, server):
        """
        Get the client connection.
        
        :param object server
            Server object which is listening
        
        :return object cl
        
        :return string data
            The requested data format depends on the request
        :example
            cl, request = network.get_client_connection(server)
        """
        # Get client connection
        cl, addr = server.accept()
        self.log('Network client connected from ' + addr[0])
        
        # Get the request data used to extract the command
        request = cl.recv(1024)
        # Return cl and the request data
        return cl, request
    def send_response(self, cl, response, close):
        """
        Send the response to the client, i.e. Domoticz, curl etc. as JSON object.
        
        :param object cl
        
        :param JSON response
        
        :param bool close
        """
        self.log('HTTP Response=' + json.dumps(response))
        # Important to have a blank line prior JSON response string
        # Note the use of json.dumps for the response
        cl.send('HTTP/1.1 200 OK'+self.CRLF+'content-type: application/json'+self.CRLF+self.CRLF+json.dumps(response))
        
        # If flag close is set, ensure to close the connection        
        if close == True:
            cl.close()
            self.log('Network connection closed')
    def send_get_request(self, url):
        """
        Network submit http get request to the domoticz server.
        :param string url
            URL of the HTTP request
        
        :return int status
            0 = Error, 1 = OK
            
        :return string content
            HTTP response content sent by Domoticz engine
        
        :example
            Update the Domoticz temp+hum device with IDX 15
            http://domoticz-ip:port/json.htm?type=command&param=udevice&idx=15&nvalue=0&svalue=16;55;1
        """
        status = 0
        content = ''
        self.log('Send GET request url=',url)
        try:
            # URL encode space
            url = url.replace(' ', '%20')
            r = urequests.get(url)
            j = json.loads(r.content)
            content = j
            self.log('Send GET request status=' + j['status'])
            r.close()
            status = 1
        except OSError as e:
            # print('[ERROR] Sending data', e)
            raise Exception('[ERROR] Sending data ' + e)
        except ValueError as e:
            # print('[ERROR]', e, r.content.decode()')
            raise Exception('[ERROR]', e, r.content.decode())
        return status, content 
    def send_post_request(self, url, postdata):
        """
        Network submit http post request to the domoticz server.
        :param string url
            URL of the HTTP request
            
        :param string postdata
            postdata as JSON object
        
        :return int status
            0 = Error, 1 = OK
        
        :example
            Trigger the Domoticz custom event named DHT22 with data JSON object
            http://domoticz-ip:port/json.htm?type=command&param=customevent&event=DHT22&data={"h": 58, "t": 16, "s": 0}
        """
        status = 0
        self.log('Send POST request url='+url+',postdata='+postdata)
        try:
            r = urequests.post(url, data=json.dumps(postdata))
            j = json.loads(r.content)
            self.log('Send POST request status='+j['status'])
            r.close()
            status = 1
        except OSError as e:
            print('[ERROR] Sending data', e)
            # raise Exception('Network Connection failed.')
        return status 
