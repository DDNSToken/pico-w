#  DDNSToken
#  ddnstoken.py
#
#  Copyright 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#
import base64

def get_value_from_line_with_string(file_path, search_string):
    with open(file_path, 'r') as file:
        for line in file:
            if search_string in line:
                # Returns the value of the line where a specific string was found.
                return line.strip()

    # You can return None if a particular string isn't found, or do whatever exception handling you want.
    return None

def get_VER():
    ver = get_value_from_line_with_string("ddnstoken_misc.py", "VER = ")
    ver = ver[6:]
    ver = ver.replace('"', '').strip()
    return ver

def encode_file_to_base64(file_path, output_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
        base64_data = base64.b64encode(binary_data).decode('utf-8')

    # Save with a limit of 72 characters per line
    lines = [base64_data[i:i+72] for i in range(0, len(base64_data), 72)]
    encoded_data = '\n'.join(lines)

    with open(output_path, 'w') as output_file:
        output_file.write(encoded_data)

VER = get_VER()

# example usage
file_path = './build/ddnstoken.'+VER+'.zip'  # input file path
output_path = './build/ddnstoken.'+VER+'.fwm'  # output file path
encode_file_to_base64(file_path, output_path)

print("VER: " + VER)