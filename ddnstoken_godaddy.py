#  DDNSToken
#  ddnstoken_godaddy.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import ddnstoken_misc
import urequests

TAG = "GoDaddy"
GODADDY_API = "https://api.godaddy.com/v1/domains"

def make_headers(api_key, api_secret):
    headers = {
        'Authorization': f"sso-key {api_key}:{api_secret}",
        'Content-Type': 'application/json',
        "User-Agent": ddnstoken_misc.USER_AGENT
    }
    return headers

def make_update_url(domain, record_name, record_type):
    url = f"{GODADDY_API}/{domain}/records/{record_type}/{record_name}"
    return url

def ddns_update(api_key, api_secret, domain, record_name, record_type, myIpv4):
    url = make_update_url(domain, record_name, record_type)
    data = [{"data": myIpv4}]
    headers = make_headers(api_key, api_secret)    
    response = urequests.put(url, json=data, headers=headers)
    if response:
        if response.status_code == 200:
            print(TAG, "ddns_update response success")            
            return True            
        print(TAG, "ddns_update response status_code:", response.status_code)            
        print(TAG, "ddns_update response text:", response.text)            
    return False
