#!/bin/bash

VER=$(grep "VER = " ddnstoken_misc.py)
echo ${VER}
VER="${VER: -6}"
VER=$(echo "$VER" | tr -d '"')
echo ${VER}

rm -f ddnstoken.?.?.?.zip
rm -f ddnstoken.?.?.?.fwm
rm -f ddnstoken.?.?.?.fwm.zip
rm -rf ./build/*

../micropython/mpy-cross/build/mpy-cross ddnstoken_starter.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_misc.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_configuration.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_imdns.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_updater.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_cloudflare.py
../micropython/mpy-cross/build/mpy-cross ddnstoken_godaddy.py

python ddnstoken_mpy2fwm.py 

zip ddnstoken.${VER}.zip ddnstoken.py ddnstoken_asm.py ddnstoken_starter.fwm ddnstoken_misc.fwm ddnstoken_configuration.fwm ddnstoken_imdns.fwm ddnstoken_updater.fwm ddnstoken_cloudflare.fwm ddnstoken_godaddy.fwm 
mv ddnstoken.${VER}.zip ./build/.
python ddnstoken_zip2fwm.py 
cd ./build
rm -f ddnstoken.${VER}.zip
zip ddnstoken.${VER}.zip ddnstoken.${VER}.fwm 
cd ..

rm -f *.mpy
rm -f *.fwm
