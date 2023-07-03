#  DDNSToken
#  ddnstoken_configuration.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import machine
import network
import os
import uos
import utime
import json
import ubinascii
from machine import Pin

import usocket as socket
import ddnstoken_misc

led = Pin("LED", Pin.OUT)

config_wifi_html = """<!DOCTYPE html>
<html>
<head>
    <title>DDNSToken Configuration</title>
</head>
<body>
    <h2>Hello, DDNSToken!</h2>
    <h3>Enter the settings for this device to connect to your WiFi router.</h3>
    <H3><font color="red">Note: This device only supports 2.4GHz WiFi.</font></h3>
    <form method="post">
        <label for="config_wifi_ssid">WiFi SSID:</label>
        <input type="text" id="config_wifi_ssid" name="config_wifi_ssid" value="{config_wifi_ssid}">
        <br><br>
        <label for="config_wifi_ssid">WiFi Password:</label>
        <input type="password" id="config_wifi_pass" name="config_wifi_pass" value="{config_wifi_pass}">
        <br><br>
        <input type="submit" value="Set">
    </form>
    <br><br>
    <h3>When this device is connected to your WiFi router, the current web connection will be blocked.</h3>
    <h3>The default domain mapped to this device is <font color="blue">{config_name}</font>.<font color="green">{config_domain}</font>. It is not case sensitive.</h3>
    <h3>For more information on domains, please visit <a href="https://www.ddnstoken.com" target=_blank>www.ddnstoken.com</a>.</h3>
    <br><br>
    <h3>You can reboot DDNSToken device.</h3>    
    <form method="post">
        <input id="config_reboot" name="config_reboot" value="1" style="display: none">
        <input type="submit" value="Reboot">
    </form>
</body>
</html>
"""

config_domain = "IMDNS.ORG"
config_wifi_ssid = ""
config_wifi_pass = ""

print("### AP Mode ###")

configuration_contents = ""
configuration_file_path = "configuration.json"
try:
    with open(configuration_file_path, "r") as configuration_file:
        configuration_contents = configuration_file.read()
        #print("Configuration contents:", configuration_contents)
        configuration_file.close()
except Exception as e:
    print("Not found configration.")

try:
    configuration_json_data = json.loads(configuration_contents)
    config_wifi_ssid = configuration_json_data["config_wifi_ssid"]
    config_wifi_pass = configuration_json_data["config_wifi_pass"]
    
    if config_wifi_ssid != None:
        config_wifi_ssid = ubinascii.a2b_base64(config_wifi_ssid).decode('utf-8')
    if config_wifi_pass != None:
        config_wifi_pass = ubinascii.a2b_base64(config_wifi_pass).decode('utf-8')

except KeyError:
    print("Your JSON data does not contain the key you want.")
except Exception as e:
    print("Not found configration data.")

print("Configuration WiFi SSID:", config_wifi_ssid)
print("Configuration WiFi PASS:", config_wifi_pass)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

ap = network.WLAN(network.AP_IF)

print("### MAC Address ###")        
config_device = ":".join("{:02X}".format(b) for b in ap.config("mac"))
print(config_device)

print("### Device ID ###")        
config_device = ddnstoken_misc.get_device_id()
print(config_device)

ssid = "DDNSToken_"+config_device
ssidpw = config_device
print("SSID:" + ssid)
print("PASS:" + ssidpw)
print("HOST:" + "http://192.168.4.1")
ap.config(essid=ssid, password=ssidpw)  # AP의 SSID와 비밀번호 설정
ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))
ap.active(True)


def handle_request(client_socket):
    global config_wifi_ssid # 전역 변수 설정
    global config_wifi_pass # 전역 변수 설정
            
    request = client_socket.recv(4096).decode("utf-8")
    
    if "POST /" in request: # POST 요청 처리
        if "config_reboot=" in request:
            config_wifi_reboot = request.split("config_reboot=")[1].split("&")[0]
            if config_wifi_reboot:
                machine.reset()
                
        if "config_wifi_ssid=" in request and "config_wifi_pass=" in request:
            config_wifi_ssid = request.split("config_wifi_ssid=")[1].split("&")[0]
            config_wifi_pass = request.split("config_wifi_pass=")[1].split("&")[0]
                        
            save_data = {"config_wifi_ssid": config_wifi_ssid, "config_wifi_pass": config_wifi_pass}
            save_data = json.dumps(save_data)
                    
            save_file = "configuration.json"
            save_file = open(save_file, "w")
            save_file.write(str(save_data))
            # file.flush()
            save_file.close()
            
            print(config_wifi_ssid)
            print(config_wifi_pass)

            print("### WiFi Settings OK ###")
        
    config_wifi_html2 = config_wifi_html.replace("{config_wifi_ssid}", config_wifi_ssid)    
    config_wifi_html = config_wifi_html2
    config_wifi_html2 = config_wifi_html.replace("{config_wifi_pass}", config_wifi_pass)
    config_wifi_html = config_wifi_html2
    config_wifi_html2 = config_wifi_html.replace("{config_name}", config_device)
    config_wifi_html = config_wifi_html2
    config_wifi_html2 = config_wifi_html.replace("{config_domain}", config_domain)
        
    client_socket.send(config_wifi_html2)
    client_socket.close()



# 웹 서버 실행
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 80)) # 웹 서버 포트 설정
server_socket.listen(5)

print("Web server started")
print(ap.ifconfig()[0])


print("##################################################")
print("Configuration WiFi")
print("--------------------------------------------------")
print("You can use the [WiFi] button at the top of")
print("this app to set the WiFi network your device")
print("will connect to.")
print("Or")
print("Follow the steps below to set up WiFi")
print("using a web browser.")
print("--------------------------------------------------")
print("Connect to the WiFi named", ssid)
print("on your PC using the password", ssidpw)
print("--------------------------------------------------")
print("You can configuration with web browser")
print("at", "http://192.168.4.1")

print("##################################################")
print("If you entered the WiFi SSID and password correctly,")
print("turn off the Raspberry Pi Pico W and turn it back on.")

while True:
    led.on() # led on    
    client_socket, addr = server_socket.accept()
    print("Client connected from", addr)
    handle_request(client_socket)    
    led.off() # led off
    utime.sleep(0.1)