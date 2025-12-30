BITS    16
ORG     0x7c00

start:
        jmp $

times 510 - ($-$$) db 0
dw        0xaa55