#  DDNSToken
#  ddnstoken_cloudflare.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import ddnstoken_misc
import urequests
import json

TAG = "Cloudflare"
CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"

def make_headers(token):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "User-Agent": ddnstoken_misc.USER_AGENT
    }
    return headers

def make_update_url(domain, token):
    valid_token = is_valid_token(token)
    if valid_token == False:
        return None

    zone_id = get_zone_id(domain, token)
    if zone_id != None:
        record_id = get_record_id(domain, token, zone_id)
        if record_id != None:
            print(TAG, "zone_id:", zone_id)
            print(TAG, "record_id:", record_id)
            url = CLOUDFLARE_API + "/zones/"+zone_id+"/dns_records/"+record_id
            return url
        
    return None

def is_valid_token(token):
    url = CLOUDFLARE_API+ "/user/tokens/verify"
    print(TAG, "is_valid_token url:", url)

    headers = make_headers(token)    
    response = urequests.get(url, headers=headers)
    if response:
        if response.status_code == 200:
            json_res = json.loads(response.text)
            if json_res["success"] == True and json_res["result"]["status"] == "active":
                print(TAG, "is_valid_token >>> valid token")
                return True
            else:
                print(TAG, "is_valid_token >>> invalid token")
        else:
            print(TAG, "is_valid_token >>> response status_code:", response.status_code)
    else:
        print(TAG, "is_valid_token >>> response:", "None")

    return False

def get_zone_id(domain, token):
    url = CLOUDFLARE_API+ "/zones"
    print(TAG, "get_zone_id url:", url)

    headers = make_headers(token)    
    response = urequests.get(url, headers=headers)
    if response:
        if response.status_code == 200:
            json_res = json.loads(response.text)
            if json_res["success"] == True:
                result_list = json_res["result"]
                for result in result_list:
                    if domain == result["name"] or domain.endswith("." + result["name"]):
                        return result["id"]
            else:
                print(TAG, "get_zone_id >>> failed")
        else:
            print(TAG, "get_zone_id >>> response status_code:", response.status_code)
    else:
        print(TAG, "get_zone_id >>> response:", "None")

    return None

def get_record_id(domain, token, zone_id):
    url = CLOUDFLARE_API+ "/zones/" + zone_id + "/dns_records"
    print(TAG, "get_record_id url:", url)

    headers = make_headers(token)    
    response = urequests.get(url, headers=headers)
    if response:
        if response.status_code == 200:
            json_res = json.loads(response.text)
            if json_res["success"] == True:
                result_list = json_res["result"]
                for result in result_list:
                    if domain == result["name"]:
                        return result["id"]
            else:
                print(TAG, "get_record_id >>> failed")
        else:
            print(TAG, "get_record_id >>> response status_code:", response.status_code)
    else:
        print(TAG, "get_record_id >>> response:", "None")

    return None

def ddns_update(domain, token, ipv4, ttl, proxied):
    url = make_update_url(domain, token)
    if url == None:
        print(TAG, "ddns_update error: url is None")
        return False
    data = {"type":"A", "name":domain, "content":ipv4, "ttl":ttl, "proxied":proxied}
    headers = make_headers(token)    
    response = urequests.put(url, json=data, headers=headers)
    if response:
        if response.status_code == 200:
            json_res = json.loads(response.text)
            if json_res["success"] == True:
                print(TAG, "ddns_update response success:", response.text)            
                return True            
        print(TAG, "ddns_update response status_code:", response.status_code)            
        print(TAG, "ddns_update response text:", response.text)            
    return False
