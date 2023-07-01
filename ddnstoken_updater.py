#  DDNSToken
#  ddnstoken_updater.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import ddnstoken_misc
import ddnstoken_asm
import ddnstoken_cloudflare
import ddnstoken_godaddy
# DYN connections can be deferred.
# import ddnstoken_dyndns

import machine
import network
import urequests
import ubinascii
import json
import utime
from machine import Pin

livesig = True

led = Pin("LED", Pin.OUT)

fatal_error_count = 0
soft_reset_button = False

configuration_contents = ""
configuration_file_path = "configuration.json"

DDNS_SERVICE = ddnstoken_misc.get_ddns_service()

MyIpV4Updated = None

ddns = None
ddnsName = None
domain = None
token = None
hostname = None
username = None
password = None
qstring = None
apikey = None
apisecret = None
record = None

if "ddns" in DDNS_SERVICE:
    ddns = DDNS_SERVICE["ddns"]
if "name" in DDNS_SERVICE:
    ddnsName = DDNS_SERVICE["name"]
if "domain" in DDNS_SERVICE:
    domain = DDNS_SERVICE["domain"].lower()
if "token" in DDNS_SERVICE:
    token = DDNS_SERVICE["token"]
if "hostname" in DDNS_SERVICE:
    hostname = DDNS_SERVICE["hostname"].lower()
if "username" in DDNS_SERVICE:
    username = DDNS_SERVICE["username"]
if "password" in DDNS_SERVICE:
    password = DDNS_SERVICE["password"]
if "qstring" in DDNS_SERVICE:
    qstring = DDNS_SERVICE["qstring"]
if "apikey" in DDNS_SERVICE:
    apikey = DDNS_SERVICE["apikey"]
if "apisecret" in DDNS_SERVICE:
    apisecret = DDNS_SERVICE["apisecret"]
if "record" in DDNS_SERVICE:
    record = DDNS_SERVICE["record"]

ip = ""
if "ip" in DDNS_SERVICE:
    if DDNS_SERVICE["ip"] is not None:
        ip = DDNS_SERVICE["ip"]

interval = DDNS_SERVICE["interval"] * 60
if interval < 5 * 60:
    interval = 5 * 60
if interval > 24 * 60 * 60:
    interval = 24 * 60 * 60

fatalError = False
connectionError = False
sInterval = interval    # Interval used in case of success (in seconds)
fInterval = 30  # Interval used in case of failure (in seconds)
fatalInterval = 60 * 10  # Interval used in case of serious failure (in seconds)

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


    # Wi-Fi mode setting
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config_wifi_ssid, config_wifi_pass)    

    utime.sleep(1.0)            

    connectionError = False
    fatalError = False

    myIpv4 = None

    # Check Wi-Fi connection
    if sta_if.isconnected():
        print("Wi-Fi Connected:", sta_if.ifconfig()[0])
        myIpv4 = ddnstoken_misc.get_myip_v4(ddns)
        if myIpv4 == None:
            # If an error occurs, it informs you that you must turn the power off and then turn it on again.
            print("!!!")
            print("Please turn off the power of the token device,")
            print("wait for a while,")
            print("and then turn it on again and try again.")
            print("!!!")

            utime.sleep(1)
            led.off()
            utime.sleep(0.5)

            connectionError = True
        else:                      
            # If the IP has changed compared to my IP and previously updated, proceed with the update
            if myIpv4 == MyIpV4Updated:
                print("No changed ipv4:", myIpv4)
            else:
                print("Try ipv4 update to :", ddnsName, myIpv4)
                try:
                    if ddns == "cloudflare":
                        ttl = 60
                        proxied = False                    
                        if ddnstoken_cloudflare.ddns_update(domain, token, myIpv4, ttl, proxied) == True:
                            MyIpV4Updated = myIpv4
                        else:
                            connectionError = True
                    elif ddns == "godaddy":
                        if ddnstoken_godaddy.ddns_update(apikey, apisecret, domain, record, "A", myIpv4) == True:
                            MyIpV4Updated = myIpv4
                        else:
                            connectionError = True
# DYN connections can be deferred.                          
#                    elif ddns == "dyndns":
#                        ## DYN 의 경우 별도의 업데이터 구현됨
#                        if ddnstoken_dyndns.ddns_update(apikey, apisecret, domain, record, "A", myIpv4) == True:
#                            MyIpV4Updated = myIpv4
#                        else:
                            connectionError = True
                    else:
                        updateURL = None

                        if ddns == "duckdns":
                            if domain != None and len(domain) > 0:
                                if domain.endswith(".duckdns.org"):
                                    updateURL = "https://www.duckdns.org/update?domains="+domain[:-12]+"&token="+token+"&ip="+myIpv4
                                else:
                                    updateURL = "https://www.duckdns.org/update?domains="+domain+"&token="+token+"&ip="+myIpv4
                        elif ddns == "google":
                            if hostname != None and len(hostname) > 0:
                                updateURL = "https://domains.google.com/nic/update?hostname="+hostname+"&myip="+myIpv4
                        elif ddns == "noip":
                            if hostname != None and len(hostname) > 0:
                                updateURL = "https://dynupdate.no-ip.com/nic/update?hostname="+hostname+"&myip="+myIpv4
                        elif ddns == "cloudns":
                            if qstring != None and len(qstring) > 0:
                                updateURL = "https://ipv4.cloudns.net/api/dynamicURL/?q="+qstring
                        elif ddns == "freemyip":
                            if token != None and len(token) > 0 and domain != None and len(domain) > 0:
                                if domain.endswith(".freemyip.com"):
                                    updateURL = "https://freemyip.com/update?token="+token+"&domain="+domain+"&myip="+myIpv4
                                else:
                                    updateURL = "https://freemyip.com/update?token="+token+"&domain="+domain+".freemyip.com&myip="+myIpv4
                        elif ddns == "freedns":
                            if token != None and len(token) > 0:
                                updateURL = "https://freedns.afraid.org/dynamic/update.php?"+token+"&address="+myIpv4
        
                        if updateURL != None:
                            print("DDNS Request URL:", updateURL)

                            headers = {
                                "User-Agent": ddnstoken_misc.USER_AGENT
                            }

                            if ddns == "google" or ddns == "noip":
                                response = urequests.get(updateURL, auth=(username, password), headers=headers, timeout=30)
                            else:
                                response = urequests.get(updateURL, headers=headers, timeout=30)

                            # Close connection
                            if response:
                                # Response code, check body
                                if response.status_code == 200:
                                    fatal_error_count = 0
                                    ddns_result = response.text.strip()
                                    # In the case of freedns, it is processed. Not an actual error.
                                    if ddns == "freedns":
                                        ddns_result2 = ddns_result.replace("ERROR:", "").strip()
                                        ddns_result = ddns_result2

                                    print("DDNS Response Result:", ddns_result)

                                    if ddns == "freedns":
                                        if ddns_result.startswith("Updated") or ddns_result.endswith("has not changed."):
                                            MyIpV4Updated = myIpv4
                                            connectionError = False
                                        else:
                                            connectionError = True                                                                    
                                    elif ddns == "google" or ddns == "noip":
                                        if ddns_result.startswith("nochg") or ddns_result.startswith("good"):
                                            MyIpV4Updated = myIpv4
                                            connectionError = False
                                        else:
                                            if ddns == "noip":
                                                if ddns_result.startswith("nohost") or ddns_result.startswith("badauth") or ddns_result.startswith("badagent") or ddns_result.startswith("abuse"):                                                
                                                    fatalError = True

                                            connectionError = True                                                                    
                                    elif ddns == "duckdns" or ddns == "cloudns" or ddns == "freemyip":
                                        if ddns_result == "OK":
                                            MyIpV4Updated = myIpv4
                                            connectionError = False
                                        else:
                                            connectionError = True
                                    else:
                                        connectionError = True
                                else:
                                    print("DDNS Response Statue Code:", response.status_code)
                                    print(response.text)
                                    
                                    connectionError = True

                                response.close()
                        else:
                            connectionError = True

                except Exception as e:
                    print("Request error:", str(e))

                    connectionError = True

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

        led.off() # led off

        if connectionError == False:
            utime.sleep(0.2)
            led.on()
            utime.sleep(0.2)
            led.off()
            utime.sleep(0.2)
            led.on()
            utime.sleep(0.2)
            led.off()
            interval = sInterval
        else:
            print("DDNS update error: Check your DDNS Service settings.")
            utime.sleep(0.2)
            led.on()
            utime.sleep(1.0)
            led.off()
            utime.sleep(0.5)
            led.on()
            utime.sleep(1.0)
            led.off()
            interval = fInterval

        if livesig:
            utime.sleep(0.5)
            led.on()
            if fatalError==True:
                # An error, but a serious error. Retry takes too long.
                interval = fatalInterval
                for t in range(1, interval * 2):
                    if t % 2 == 0:
                        print(".Fatal..."+str(int(t/2))+"/"+str(interval)+".")
                        led.on()
                    if t % 2 == 1:
                        led.off()
                    check_bootsel_pressed()
                    utime.sleep(0.5)
            elif connectionError==False:
                for t in range(1, interval):
                    print(".Next..."+str(t)+"/"+str(interval)+".")
                    if t % 2 == 0:
                        led.on()
                    if t % 2 == 1:
                        led.off()
                    check_bootsel_pressed()
                    utime.sleep(1.0)
            else:
                for t in range(1, interval):
                    print(".Try..."+str(t)+"/"+str(interval)+".")
                    if t % 6 == 0:
                        led.on()
                    if t % 6 == 3:
                        led.off()
                    if t % 6 == 4:
                        led.on()
                    if t % 6 == 5:
                        led.off()
                    check_bootsel_pressed()
                    utime.sleep(1.0)
        else:
            check_bootsel_pressed()
            utime.sleep(interval)
    else:
        # No wifi connection
        sta_if.active(False)
        fatal_error_count += 1

        print("Not connected")
        check_bootsel_pressed()
        utime.sleep(0.5)
        led.off()
        utime.sleep(0.5)
