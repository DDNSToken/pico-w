#  DDNSToken
#  ddnstoken_misc.py
#
#  Copyright  2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/05/05.
#

import os
import uos
import machine
import json
import network
import binascii, hashlib, ubinascii
import urequests
import utime
import random

from machine import Pin

VER = "1.2.4"

# No-IP 기준
# H/W Clients
# User-Agent: Company DeviceName-Model/FirmwareVersionNumber maintainer-contact@example.com
# S/W Clients
# User-Agent: Company NameOfProgram/OSVersion-ReleaseVersion maintainer-contact@example.com
USER_AGENT = "Certchip DDNSToken/" + VER + " ddnstoken@certchip.com"

DDNS_SERVICE_NONE = {"ddns": "none",
     "name":"None",
     "interval": 15}
DDNS_SERVICE_LIST = [
    {"ddns": "google",
     "name":"Google",
     "hostname": "",
     "username": "",
     "password": "",
     "interval": 15}, 
    {"ddns": "godaddy",
     "name":"GoDaddy",
     "domain": "",
     "record": "",
     "apikey": "",
     "apisecret": "",
     "interval": 15}, 
# DYN connections can be deferred.   
#    {"ddns": "dyndns",
#     "name":"DYN",
#     "domain": "",
#     "record": "",
#     "apikey": "",
#     "apisecret": "",
#     "interval": 15}, 
    {"ddns": "cloudflare",
     "name":"Cloudflare",
     "domain": "",
     "token": "",
     "interval": 15}, 
    {"ddns": "duckdns",
     "name": "Duck DNS", 
     "domain": "",
     "token": "",
     "interval": 15}, 
    {"ddns": "noip",
     "name": "No-IP", 
     "hostname": "",
     "username": "",
     "password": "",
     "interval": 15}, 
    {"ddns": "cloudns",
     "name": "ClouDNS", 
     "qstring": "",
     "interval": 15},
    {"ddns": "freemyip",
     "name": "Freemyip", 
     "domain": "",
     "token": "",
     "interval": 15}, 
    {"ddns": "freedns",
     "name": "FreeDNS", 
     "token": "",
     "interval": 15}, 
    {"ddns": "imdns",
     "name":"ImDNS",
     "domain": "",
     "token": "",
     "interval": 15}]

DDNS_UPDATERS = []
for ddns_service in DDNS_SERVICE_LIST:
    DDNS_UPDATERS.append(ddns_service["ddns"])


configuration_file_path = "configuration.json"
DDNS_JSON_FILE = "ddns.json"

def is_ddns(ddns):
    if get_ddns_service() == ddns:
        return True
    return False

def is_file_exists(file_path):
    try:
        uos.stat(file_path)
        return True
    except OSError:
        return False


def get_all_ddns_service():
    return DDNS_SERVICE_LIST

def get_ddns_service_info():
    data = {"DDNS": get_ddns_service(), "DDNS_LIST": get_all_ddns_service()} 
    json_dat = json.dumps(data)
    json_obj = json.loads(json_dat)
    print(json_obj)


def set_ddns_service(ddns, name, domain, token, interval):
    data = {} 
    service = {}
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
    service["ddns"] = ddns
    service["name"] = name
    service["domain"] = domain
    service["token"] = token
    service["interval"] = interval

    data["service"] = service

    with open(DDNS_JSON_FILE, "w") as json_file:
        json.dump(data, json_file)    
        print(data)

def set_ddns_service_1(ddns, name, token, interval):
    data = {} 
    service = {}
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
    service["ddns"] = ddns
    service["name"] = name
    service["token"] = token
    service["interval"] = interval

    data["service"] = service

    with open(DDNS_JSON_FILE, "w") as json_file:
        json.dump(data, json_file)    
        print(data)

def set_ddns_service_2(ddns, name, hostname, username, password, interval):
    data = {} 
    service = {}
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
    service["ddns"] = ddns
    service["name"] = name
    service["hostname"] = hostname
    service["username"] = username
    service["password"] = password
    service["interval"] = interval

    data["service"] = service

    with open(DDNS_JSON_FILE, "w") as json_file:
        json.dump(data, json_file)    
        print(data)

def set_ddns_service_3(ddns, name, qstring, interval):
    print("set_ddns_service_3", ddns, name, qstring, interval)

    data = {} 
    service = {}
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
    service["ddns"] = ddns
    service["name"] = name
    service["qstring"] = qstring
    service["interval"] = interval

    data["service"] = service

    with open(DDNS_JSON_FILE, "w") as json_file:
        json.dump(data, json_file)    
        print(data)

def set_ddns_service_4(ddns, name, domain, record, apikey, apisecret, interval):
    print("set_ddns_service_4", ddns, name, domain, record, apikey, apisecret, interval)

    data = {} 
    service = {}
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
    service["ddns"] = ddns
    service["name"] = name
    service["domain"] = domain
    service["record"] = record
    service["apikey"] = apikey
    service["apisecret"] = apisecret
    service["interval"] = interval

    data["service"] = service

    with open(DDNS_JSON_FILE, "w") as json_file:
        json.dump(data, json_file)    
        print(data)

def get_ddns_service():
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
            return data["service"]
    return DDNS_SERVICE_NONE

def get_ddns_service_name():
    if is_file_exists(DDNS_JSON_FILE):
        with open(DDNS_JSON_FILE, "r") as file:
            data = json.load(file)
            return data["service"]["name"]
    return DDNS_SERVICE_NONE["name"]

def make_star_string(s):
    return "*" * len(s)

def get_secret_256(secret):
    sha256 = hashlib.sha256()
    sha256.update(secret.encode("utf-8"))
    secret = sha256.digest()
    secret = binascii.hexlify(secret)
    return secret
def get_secret_1(secret):
    sha1 = hashlib.sha1()
    sha1.update(secret.encode("utf-8"))
    secret = sha1.digest()
    secret = binascii.hexlify(secret)
    return secret


def get_device_id():
    ap = network.WLAN(network.AP_IF)
    config_device = ":".join("{:02X}".format(b) for b in ap.config("mac"))
    
    # SHA-1 해시
    sha1 = hashlib.sha1()
    sha1.update(config_device.encode("utf-8"))
    config_device = sha1.digest()
    config_device = binascii.hexlify(config_device)
    # SHA-256 해시
    sha256 = hashlib.sha256()
    sha256.update(config_device)
    config_device = sha256.digest()
    config_device = binascii.hexlify(config_device)
    # SHA-1 해시
    sha1_1 = hashlib.sha1()
    sha1_1.update(config_device)
    config_device = sha1_1.digest()
    config_device = binascii.hexlify(config_device)
    # 바이너리 데이터를 16진수로 표현
    hex_data = config_device.hex()
    # 16진수 값을 36진수로 변환하여 알파벳 소문자와 숫자로만 표현
    base36_data = int(hex_data, 16)
    config_device = ""
    while base36_data:
        base36_data, rem = divmod(base36_data, 36)
        config_device = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[rem] + config_device
    config_device2 = config_device.replace("0", "").replace("O", "")
    config_device = config_device2
    device = config_device[3] + config_device[10] + config_device[5] + config_device[1] + config_device[6] + config_device[13] + config_device[9] + config_device[7]
    return device


def get_version():
    return "DDNSToken v%s Device ID %s" %(VER, get_device_id())

def soft_reset():
    print("### Reboot ###")
    machine.reset()

def factory_clear():
    print("### Delete Configuration Files ###")
    try:
        with open(configuration_file_path, "r") as configuration_file:
            os.remove(configuration_file_path)
            print(f"Deleted {configuration_file_path}")
    except Exception as e:
        print("Not Configuration")
                        
    try:
        with open(configuration_file_path, "r") as configuration_file:
            os.remove(DDNS_JSON_FILE)
            print(f"Deleted {DDNS_JSON_FILE}")
    except Exception as e:
        print("Not Configuration")

def set_wifi(wifissid, wifipass):
    save_data = {"config_wifi_ssid": wifissid, "config_wifi_pass": wifipass}
    save_data = json.dumps(save_data)
            
    save_file = "configuration.json"
    save_file = open(save_file, "w")
    save_file.write(str(save_data))
    # file.flush()
    save_file.close()
    
    print(wifissid)
    print(wifipass)

    print("### WiFi Settings OK ###")

def read_configuration_contents():
    contents = ""
    try:
        with open(configuration_file_path, "r") as configuration_file:
            contents = configuration_file.read()
            configuration_file.close()
    except Exception as e:
        print("Not found configration.")
    return contents

def read_configuration_contents_value(key):
    contents = read_configuration_contents()
    value = ""
    try:
        json_data = json.loads(contents)
        value = json_data[key]
    except KeyError:
        print("Your JSON data does not contain the key you want.")
    except Exception as e:
        print("Not found configration data.")
    return value


def get_wifi():
    config_wifi_ssid = read_configuration_contents_value("config_wifi_ssid")
    config_wifi_pass = read_configuration_contents_value("config_wifi_pass")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    utime.sleep(0.3)
    wlan.active(True)
    utime.sleep(0.5)
    
    wifi_list = []
    nets = wlan.scan()
    for net in nets:
        netname = net[0].decode("utf-8")
        if len(netname) > 2:
            netname = ubinascii.b2a_base64(netname)
            if not netname.startswith("AAA"):
                wifi_list.append(netname[:-1])

    data = {"WIFISSID": config_wifi_ssid, "WIFIPASS":config_wifi_pass, "SSIDLIST": wifi_list} 

    json_dat = json.dumps(data)
    json_obj = json.loads(json_dat)

    wlan.active(False)

    print(json_obj)

def req_chkip_v4(url):
    myipv4 = None

    # 나의 IP 를 확인함. IP_QUERY_URL 을 이용함.
    try:
        # GET 요청 보내기
        print("Check IP Request URL:", url)

        headers = {
	        "User-Agent": USER_AGENT
        }

        response = urequests.get(url, headers=headers, timeout=30)

        # 연결 닫기
        if response:
            # 응답 코드, 본문 확인
            if response.status_code == 200:
                if ": " in response.text:
                    myipv4 = response.text.strip().split(": ")[-1]
                else:
                    myipv4 = response.text.strip()
                print("Check IP Response Result:", myipv4)
            else:
                print("Check IP Response Statue Code:", response.status_code)
            response.close()
    except Exception as e:
        print("Check IP Request Error:", str(e))

    return myipv4


CHECK_IP_SERVICE_LIST = ["https://api.imdns.org", 
                         "http://ip1.dynupdate.no-ip.com", 
                         "http://ip2.dynupdate.no-ip.com",
                         "https://domains.google.com/checkip",
                         "https://freemyip.com/checkip",
                         "https://checkip.amazonaws.com",
                         "https://ddns.io/ip",
                         "https://api.ipify.org",
                         "https://ip.42.pl/raw"
# DYN connections can be deferred.
#                        "http://checkip.dyndns.com"
                         ]
def get_myip_v4(ddns):
    # 기본은 imdns 를 이용 (속도 빠름)
    queryURL = "https://api.imdns.org"

    # 우선 각 DDNS 서비스가 제공하는 IP 체크 URL 을 이용
    if ddns == "noip":
        queryURL = "http://ip1.dynupdate.no-ip.com"
    elif ddns == "google":
        queryURL = "https://domains.google.com/checkip"
    elif ddns == "freemyip":
        queryURL = "https://freemyip.com/checkip"
    elif ddns == "aws":
        queryURL = "https://checkip.amazonaws.com"
# DYN connections can be deferred.
#    elif ddns == "dyndns":
#        queryURL = "http://checkip.dyndns.com"

    # 위에서 정해진 URL 을 이용하여 IP 를 확인
    myipv4 = req_chkip_v4(queryURL)
    
    # 앞에서 ip 를 확인하지 못하면 다음 랜덤으로 한번 더 확인
    if myipv4 == None:
        rnum = random.randrange(len(CHECK_IP_SERVICE_LIST))
        myipv4 = req_chkip_v4(CHECK_IP_SERVICE_LIST[rnum])

    # 그래도 체크에 실패 한다면 한번더 시도한다.
    if myipv4 == None:
        rnum = random.randrange(len(CHECK_IP_SERVICE_LIST))
        myipv4 = req_chkip_v4(CHECK_IP_SERVICE_LIST[rnum])

    # 그래도 체크에 실패 한다면 한번더 시도한다.
    if myipv4 == None:
        rnum = random.randrange(len(CHECK_IP_SERVICE_LIST))
        myipv4 = req_chkip_v4(CHECK_IP_SERVICE_LIST[rnum])

    # 그래도 체크에 실패 한다면 한번더 시도한다.
    if myipv4 == None:
        rnum = random.randrange(len(CHECK_IP_SERVICE_LIST))
        myipv4 = req_chkip_v4(CHECK_IP_SERVICE_LIST[rnum])

    return myipv4