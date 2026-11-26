// Box.asm   K = 03
// Start row = 3, height = 20 rows, width = 16*((3 mod 4)+1) = 64 px = 4 words
// Start address = SCREEN + 32*3 = 16384 + 96 = 16480
// While any key is down: box is black.  Key released: box is erased.

(MAIN)
    @KBD
    D=M
    @PRESSED
    D;JNE           // key != 0  -> draw

    @color          // no key -> color = 0 (white)
    M=0
    @PAINT
    0;JMP

(PRESSED)
    @color
    M=-1            // color = -1 (black)

(PAINT)
    @SCREEN
    D=A
    @96             // 32 * 3 (start row)
    D=D+A
    @addr
    M=D             // addr = first word of the box

    @20
    D=A
    @rows
    M=D             // rows left = 20

(ROWLOOP)
    @4
    D=A
    @cols
    M=D             // words left in this row = 4

(COLLOOP)
    @color
    D=M
    @addr
    A=M
    M=D             // RAM[addr] = color
    @addr
    M=M+1           // next word
    @cols
    M=M-1
    D=M
    @COLLOOP
    D;JGT

    @28             // 32 - 4: jump to start of next row
    D=A
    @addr
    M=D+M

    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT

    @MAIN
    0;JMP
