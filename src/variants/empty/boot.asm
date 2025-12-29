BITS    16
ORG     0x7c00

start:
        ; Infinite loop - empty MBR
        jmp $

times 510 - ($-$$) db 0
dw        0xaa55