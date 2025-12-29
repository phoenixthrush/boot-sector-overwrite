BITS    16
ORG     0x7c00

start:
        ; MEMZ-style MBR with visual effects
        call clear_screen
        mov ax, cs
        mov ds, ax
        mov es, ax
        
        ; Initialize video mode
        mov ax, 0x0013
        int 0x10
        
        ; Display chaotic graphics
        call memz_effects
        
memz_effects:
        mov cx, 0x8000  ; Loop counter
effect_loop:
        ; Random color blocks
        mov ah, 0x0c
        mov al, cl       ; Use loop counter as color
        mov bh, 0
        mov dx, cx       ; Random position
        int 0x10
        
        ; Animate text
        push cx
        mov ah, 0x02
        mov bh, 0
        mov dh, cl       ; Row
        mov dl, cl       ; Column
        int 0x10
        
        mov ah, 0x0e
        mov al, 'M'      ; M character
        mov bh, 0
        mov bl, 0x04     ; Red color
        int 0x10
        
        mov al, 'E'      ; E character
        int 0x10
        
        mov al, 'M'      ; M character
        int 0x10
        
        mov al, 'Z'      ; Z character
        int 0x10
        
        pop cx
        loop effect_loop
        
        ; Display final message
        call text_mode
        mov si, memz_msg
        call print_string
        
        jmp $

clear_screen:
        mov ax, 0x0003
        int 0x10
        ret

text_mode:
        mov ax, 0x0003
        int 0x10
        ret

print_string:
        push ax
        cld
print_loop:
        lodsb
        cmp al, 0
        je print_done
        mov ah, 0x0e
        mov bh, 0
        mov bl, 0x04
        int 0x10
        jmp print_loop
print_done:
        pop ax
        ret

memz_msg:    db "MEMZ has infected your MBR!", 13, 10, "Just kidding... this is a test.", 13, 10, 13, 10, "Greetings Phoenixthrush :D", 0

times 510 - ($-$$) db 0
dw        0xaa55