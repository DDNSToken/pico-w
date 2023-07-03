#  DDNSToken
#  ddnstoken_starter.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import ddnstoken_misc

import machine
import network
import utime
import ubinascii

from machine import Pin

led = Pin("LED", Pin.OUT)
led.on()

ddns = ddnstoken_misc.get_ddns_service()["ddns"]
ddnsName = ddnstoken_misc.get_ddns_service_name()

print("### VERSION: " + ddnstoken_misc.get_version())
print("### DDNS: " + ddnsName)

config_wifi_ssid = ddnstoken_misc.read_configuration_contents_value("config_wifi_ssid")
config_wifi_pass = ddnstoken_misc.read_configuration_contents_value("config_wifi_pass")

if config_wifi_ssid != None:
    config_wifi_ssid = ubinascii.a2b_base64(config_wifi_ssid).decode('utf-8')
if config_wifi_pass != None:
    config_wifi_pass = ubinascii.a2b_base64(config_wifi_pass).decode('utf-8')

print("Configuration WiFi SSID:", config_wifi_ssid)
print("Configuration WiFi PASS:", ddnstoken_misc.make_star_string(config_wifi_pass))

wiFiConnedted = False


ap = network.WLAN(network.AP_IF)
ap.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)


led.on() # led on
if config_wifi_ssid != "" and config_wifi_pass != "":
    # Wi-Fi 모드 설정
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config_wifi_ssid, config_wifi_pass)
    #sta_if.ifconfig(("192.168.0.112", "255.255.255.0", "192.168.0.1", "8.8.8.8"))
    utime.sleep(0.5)
    
    for i in range(20):
        # Wi-Fi 연결 확인
        if sta_if.isconnected():
            print(sta_if.ifconfig())
            
            wiFiConnedted = True
            print("Connected WiFi network")
            utime.sleep(1)
            break
        else:
            print("Try connect WiFi network")
            print(config_wifi_ssid + "/" + ddnstoken_misc.make_star_string(config_wifi_pass))
            utime.sleep(0.5)
            led.off()
            utime.sleep(1)
            led.on()
            if i > 10:
                print("### Failed to connect to WiFi network.")
                print("### If you entered the WiFi SSID and password correctly,")
                print("### turn off the Raspberry Pi Pico W and turn it back on.")

else:
    print("Need to configration for WiFi network")
    
led.off()

if wiFiConnedted == True:
    print("### Updater ###")
    print("DDNS:", ddnsName)
    if ddns == "none":
        print("Please set up the DDNS service.")
    elif ddns == "imdns":
        import ddnstoken_imdns
    elif ddns in ddnstoken_misc.DDNS_UPDATERS:
        import ddnstoken_updater
    else:
        print("Not supported for ", ddnsName)
else:
    print("### Configuration ###")
    import ddnstoken_configuration
