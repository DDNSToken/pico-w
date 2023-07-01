#  DDNSToken
#  ddnstoken.py
#
#  Copyright  2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#
import ubinascii

def decode_fwm(filename):
    with open(filename + ".fwm", "rb") as fwm_file:
        encoded_data = fwm_file.read()
        decoded_data = ubinascii.a2b_base64(encoded_data)
        with open(filename + ".mpy", "wb") as mpy_file:
            mpy_file.write(decoded_data)

decode_fwm("ddnstoken_starter")
decode_fwm("ddnstoken_misc")
decode_fwm("ddnstoken_configuration")
decode_fwm("ddnstoken_updater")
decode_fwm("ddnstoken_cloudflare")
decode_fwm("ddnstoken_godaddy")
decode_fwm("ddnstoken_imdns")

import ddnstoken_starter