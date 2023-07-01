#  DDNSToken
#  ddnstoken_mpy2fwm.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

import base64

def encode_file_to_base64(file_path, output_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
        base64_data = base64.b64encode(binary_data).decode('utf-8')

    # 한 줄에 72자로 제한하여 저장
    lines = [base64_data[i:i+72] for i in range(0, len(base64_data), 72)]
    encoded_data = '\n'.join(lines)

    with open(output_path, 'w') as output_file:
        output_file.write(encoded_data)


MPY_LIST = ["ddnstoken_starter", "ddnstoken_misc", "ddnstoken_configuration", "ddnstoken_updater"]
MPY_LIST.append("ddnstoken_cloudflare")
MPY_LIST.append("ddnstoken_godaddy")
MPY_LIST.append("ddnstoken_imdns")
# DYN connections can be deferred.
# MPY_LIST.append("ddnstoken_dyndns")

for MPY in MPY_LIST:
    encode_file_to_base64(MPY+".mpy", MPY+".fwm")
