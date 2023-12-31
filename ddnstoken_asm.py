#  DDNSToken
#  ddnstoken_asm.py
#
#  Copyright © 2023 Certchip Corp. All rights reserved.
#  Created by GYUYOUNG KANG on 2023/04/15.
#

# I found this code on github and used it. There is a comment from the original author at the following link address.
# https://github.com/micropython/micropython/issues/6852

@micropython.asm_thumb
def read_bootsel():
    # disable interrupts
    cpsid(0x0)
    
    # set r2 = addr of GPIO_QSI_SS registers, at 0x40018000
    # GPIO_QSPI_SS_CTRL is at +0x0c
    # GPIO_QSPI_SS_STATUS is at +0x08
    # is there no easier way to load a 32-bit value?
    mov(r2, 0x40)
    lsl(r2, r2, 8)
    mov(r1, 0x01)
    orr(r2, r1)
    lsl(r2, r2, 8)
    mov(r1, 0x80)
    orr(r2, r1)
    lsl(r2, r2, 8)
    
    # set bit 13 (OEOVER[1]) to disable output
    mov(r1, 1)
    lsl(r1, r1, 13)
    str(r1, [r2, 0x0c])
    
    # delay about 3us
    # seems to work on the Pico - tune for your system
    mov(r0, 0x16)
    label(DELAY)
    sub(r0, 1)
    bpl(DELAY)
    
    # check GPIO_QSPI_SS_STATUS bit 17 - input value
    ldr(r0, [r2, 0x08])
    lsr(r0, r0, 17)
    mov(r1, 1)
    and_(r0, r1)
    
    # clear bit 13 to re-enable, or it crashes
    mov(r1, 0)
    str(r1, [r2, 0x0c])
    
    # re-enable interrupts
    cpsie(0x0)