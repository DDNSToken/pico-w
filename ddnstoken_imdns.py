#  DDNSToken
#  ddnstoken_imdns.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import ddnstoken_misc
import ddnstoken_asm

import machine
import network
import urequests
import ubinascii
import json
import os
import uos
import utime
from machine import Pin
import time

DEBUG = False

domain = "api.imdns.org"
sinterval = 60
finterval = 15
einterval = 5
qinterval = 300
qlasttime = 0

if DEBUG:
    domain = "dev.imdns.org"
    sinterval = 10
    finterval = 5
    qinterval = 30
    

interval = sinterval
livesig = True


led = Pin("LED", Pin.OUT)

fatal_error_count = 0
soft_reset_button = False

configuration_contents = ""
configuration_file_path = "configuration.json"

def is_bootsel_pressed():
    return ddnstoken_asm.read_bootsel() == 0

def check_bootsel_pressed():
    soft_reset_button = False
    if is_bootsel_pressed():
        led.on()
        print("### Pressed BOOTSEL Pin (1/6) ###")
        utime.sleep(1)
        soft_reset_button = True
        if is_bootsel_pressed():
            print("### Pressed BOOTSEL Pin (2/6) ###")
            utime.sleep(1)
            if is_bootsel_pressed():
                print("### Pressed BOOTSEL Pin (3/6) ###")
                utime.sleep(1)
                if is_bootsel_pressed():
                    print("### Pressed BOOTSEL Pin (4/6) ###")
                    utime.sleep(1)
                    if is_bootsel_pressed():
                        print("### Pressed BOOTSEL Pin (5/6) ###")
                        utime.sleep(1)
                        if is_bootsel_pressed():
                            print("### Pressed BOOTSEL Pin (6/6) ###")
                            soft_reset_button = False
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            led.off()
                            utime.sleep(0.2)
                            led.on()
                            utime.sleep(0.2)
                            print("### Factory Reset ###")
                            
                            ddnstoken_misc.factory_clear()

                            print("### Reboot ###")
                            machine.reset()    
    led.off()

    if soft_reset_button:
        print("### Reboot ###")
        machine.reset()


secret = "No Secret"
try:
    with open(".secret", "r") as secret_file:
        secret = secret_file.read()
        secret_file.close()
except Exception as e:
    print(secret)
    

try:
    with open(configuration_file_path, "r") as configuration_file:
        configuration_contents = configuration_file.read()
        #print("Configuration contents:", configuration_contents)
        configuration_file.close()
except Exception as e:
    print("Configuration error:", str(e))

try:
    configuration_json_data = json.loads(configuration_contents)
    config_wifi_ssid = configuration_json_data["config_wifi_ssid"]
    config_wifi_pass = configuration_json_data["config_wifi_pass"]

    if config_wifi_ssid != None:
        config_wifi_ssid = ubinascii.a2b_base64(config_wifi_ssid).decode('utf-8')
    if config_wifi_pass != None:
        config_wifi_pass = ubinascii.a2b_base64(config_wifi_pass).decode('utf-8')
except KeyError:
    config_wifi_ssid = ""
    config_wifi_pass = ""
    print("Your JSON data does not contain the key you want.")
except Exception as e:
    config_wifi_ssid = ""
    config_wifi_pass = ""
    print("An error occurred while parsing JSON data.")
    print("Error message: ", str(e))
    print(configuration_contents)

print("Configuration WiFi SSID:", config_wifi_ssid)
print("Configuration WiFi PASS:", ddnstoken_misc.make_star_string(config_wifi_pass))



device = ""
deviceIp = ""
deviceMac = ""

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

ap = network.WLAN(network.AP_IF)
ap.active(False)

while True:
    led.on() # led on
    
    print("### Wi-Fi Connection ###")

    if fatal_error_count > 10:
        print(fatal_error_count)    
        print("### Reboot ###")
        machine.reset()


    # Setting for Wi-Fi
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config_wifi_ssid, config_wifi_pass)    

    # Check connection for Wi-Fi
    if sta_if.isconnected():
        print("Wi-Fi Connected:", sta_if.ifconfig()[0])
        
        print("### MAC Address ###")        
        deviceMac = ":".join("{:02X}".format(b) for b in sta_if.config("mac"))
        print(deviceMac)
        
        device = ddnstoken_misc.get_device_id()
                
        print("### IP ###")
    
        deviceIpChk = ""
        connectionError = True
        
        qtime = time.time() - qlasttime
        if qtime >= qinterval:
            try:
                # Request query
                url = "https://" + domain + "/query"
                query = {"device":device}
                query = json.dumps(query)

                print("Device:", device)
                print("Query to " + url)

                response = urequests.post(url, data=query, headers={"Content-Type": "application/json", "User-Agent": ddnstoken_misc.USER_AGENT})
                print(json.dumps(response, indent=4))

                # Check to response code and text.
                if response.status_code == 200:
                    fatal_error_count = 0
                    try:
                        # Parsing string data into JSON
                        json_data = json.loads(response.text)
                
                        # Access and use JSON data
                        r_device = json_data["device"]
                        r_result = json_data["result"]
                
                        # Output parsed data
                        if device == r_device:
                            deviceIpChk = r_result
                            
                        print("Current:", r_device + " => " + deviceIpChk)
                        
                        qlasttime = time.time()
                        
                        connectionError = False
                            
                    except KeyError:
                        # Exception handling: if the JSON data does not contain the desired key
                        print("Your JSON data does not contain the key you want.")
                
                    except Exception as e:
                        # Exception Handling: Other Exception Handling
                        print("An error occurred while parsing JSON data.")
                        print("Error message: ", str(e))
                        print(response.text)
                else:
                    print(response.status_code)
                    
                # Close connection
                response.close()
                
            except Exception as e:
                print("Request error:", str(e))

                if sta_if.isconnected():
                    sta_if.disconnect()

                sta_if.active(False)
                fatal_error_count += 1

                # If an error occurs, it informs you that you must turn the power off and then turn it on again.
                print("!!!")
                print("Please turn off the power of the token device,")
                print("wait for a while,")
                print("and then turn it on again and try again.")
                print("!!!")

                utime.sleep(1)
                led.off()
                utime.sleep(0.5)            
        else:
            try:
                # Send a GET request
                url = "http://" + domain
                print("DDNS Request URL:", url)

                headers = {
                    "User-Agent": ddnstoken_misc.USER_AGENT
                }
                response = urequests.get(url, headers=headers, timeout=30)

                # Close connection
                if response:
                    # Response code, check body
                    if response.status_code == 200:
                        fatal_error_count = 0
                        deviceIpChk = response.text
                        print("DDNS Response Result:", deviceIpChk)

                        connectionError = False
                        print(deviceIpChk)
                    else:
                        print("DDNS Response Statue Code:", response.status_code)
                        connectionError = True

                    response.close()
            except Exception as e:
                print("Request error:", str(e))

                if sta_if.isconnected():
                    sta_if.disconnect()

                sta_if.active(False)
                fatal_error_count += 1


                # If an error occurs, it informs you that you must turn the power off and then turn it on again.
                print("!!!")
                print("Please turn off the power of the token device,")
                print("wait for a while,")
                print("and then turn it on again and try again.")
                print("!!!")

                utime.sleep(1)
                led.off()
                utime.sleep(0.5)
            
        
        if not deviceIpChk or deviceIpChk != deviceIp:
            # After updating, a query request is made to the server again unconditionally.
            qlasttime = 0
            
            # Send POST
            url = "https://" + domain + "/update"
            ipup = {"device":device, "secret":ddnstoken_misc.get_secret_256(secret+deviceMac)}
            ipup = json.dumps(ipup)

            print("Post to " + url)

            try:
                response = urequests.post(url, data=ipup, headers={"Content-Type": "application/json", "User-Agent": ddnstoken_misc.USER_AGENT})

                # Response code, check body
                if response.status_code == 200:
                    fatal_error_count = 0
                    try:
                        # Parsing string data into JSON
                        json_data = json.loads(response.text)
                
                        if json_data["result"] == True:
                            # Access and use JSON data
                            r_device = json_data["device"]
                            r_ip = json_data["ip"]
                    
                            # Output parsed data
                            if device == r_device:
                                deviceIp = r_ip
                                
                            connectionError = False
                        else:
                            print("An error occurred while post update.")
                            connectionError = True
                    except KeyError:
                        # Exception handling: if the JSON data does not contain the desired key
                        print("Your JSON data does not contain the key you want.")
                        print(response.text)
                
                    except Exception as e:
                        # Exception Handling: Other Exception Handling
                        print("An error occurred while parsing JSON data.")
                        print("Error message: ", str(e))
                        print(response.text)
                else:
                    print(response.status_code)
                    
                # Close connection
                response.close()
                
            except Exception as e:
                print("Error message: ", str(e))

                if sta_if.isconnected():
                    sta_if.disconnect()

                sta_if.active(False)
                fatal_error_count += 1
                utime.sleep(1)

                # If an error occurs, it informs you that you must turn the power off and then turn it on again.
                print("!!!")
                print("Please turn off the power of the token device,")
                print("wait for a while,")
                print("and then turn it on again and try again.")
                print("!!!")
            
            if device != "" and deviceIp != "":
                print("Update Device:", device)
                print("Update IP:", deviceIp)
                
                save_data = {"ip": deviceIp, "device": device, "query": "http://ip.imdns.org", "update": "https://ip.imdns.org/update", "interval": 60}
                save_data = json.dumps(save_data)
                        
                save_file = ddnstoken_misc.DDNS_JSON_FILE
                save_file = open(save_file, "w") # creation and opening of a CSV file in Write mode
                # Type Program Logic Here
                save_file.write(str(save_data)) # Writing data in the opened file
                # file.flush() # Internal buffer is flushed (not necessary if close() function is used)
                save_file.close() # The file is closed
                print("### Result OK ###")
                
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                interval = sinterval
            else:
                print("No device or ip")
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                interval = finterval
        else:
            if connectionError:
                print("Connection error")
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                interval = einterval                    
            else:
                print("No changes")
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                utime.sleep(0.2)
                led.on()
                utime.sleep(0.2)
                led.off()
                interval = sinterval        

        led.off() # led off
        if livesig:
            utime.sleep(0.5)
            if connectionError==False:
                for t in range(1, interval):
                    print("."+str(t)+"/"+str(interval)+".")
                    led.on()
                    check_bootsel_pressed()
                    utime.sleep(0.005)
                    led.off()
                    utime.sleep(1)
        else:
            check_bootsel_pressed()
            utime.sleep(interval)
    else:
        # 와이파이 연결 안됨
        sta_if.active(False)
        fatal_error_count += 1

        print("Not connected")
        check_bootsel_pressed()
        utime.sleep(0.5)
        led.off()
        utime.sleep(0.5)
