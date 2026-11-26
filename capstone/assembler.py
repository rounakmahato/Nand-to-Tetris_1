#!/usr/bin/env python3
"""Hack assembler (two-pass).  Usage: python assembler.py Prog.asm
Writes Prog.hack and (K mod 3 == 0 feature) symbols.txt.
K = 03  ->  K mod 3 = 0  ->  save all labels and variables with addresses."""
import sys

COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
    'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
    '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
    'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
    'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
    'D&M': '1000000', 'D|M': '1010101',
}
DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011',
        'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}


def predefined():
    t = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
         'SCREEN': 16384, 'KBD': 24576}
    for i in range(16):
        t['R%d' % i] = i
    return t


def clean(line):
    return line.split('//')[0].replace(' ', '').replace('\t', '').strip()


def assemble(lines):
    table = predefined()
    labels, variables = {}, {}

    # ---------- First pass: labels ----------
    code = []                      # (source line number, instruction)
    for n, raw in enumerate(lines, 1):
        s = clean(raw)
        if not s:
            continue
        if s.startswith('('):
            name = s[1:s.index(')')]
            labels[name] = len(code)      # address of NEXT instruction
            table[name] = len(code)
        else:
            code.append((n, s))

    # ---------- Second pass: translate ----------
    out, next_var = [], 16
    for n, s in code:
        if s.startswith('@'):
            sym = s[1:]
            if sym.isdigit():
                val = int(sym)
            else:
                if sym not in table:           # new variable
                    table[sym] = next_var
                    variables[sym] = next_var
                    next_var += 1
                val = table[sym]
            out.append(format(val, '016b'))
        else:
            dest, jump = '', ''
            body = s
            if '=' in body:
                dest, body = body.split('=', 1)
            if ';' in body:
                body, jump = body.split(';', 1)
            if body not in COMP or dest not in DEST or jump not in JUMP:
                raise ValueError('Line %d: invalid instruction "%s"' % (n, s))
            out.append('111' + COMP[body] + DEST[dest] + JUMP[jump])
    return out, labels, variables


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.asm'):
        sys.exit('Usage: python assembler.py Prog.asm')
    path = sys.argv[1]
    with open(path) as f:
        lines = f.read().splitlines()
    try:
        out, labels, variables = assemble(lines)
    except ValueError as e:
        sys.exit(str(e))

    with open(path[:-4] + '.hack', 'w') as f:
        f.write('\n'.join(out) + '\n')

    # Additional feature (K mod 3 == 0): symbols.txt
    with open('symbols.txt', 'w') as f:
        f.write('LABELS\n')
        for k, v in labels.items():
            f.write('%s = %d\n' % (k, v))
        f.write('\nVARIABLES\n')
        for k, v in variables.items():
            f.write('%s = %d\n' % (k, v))
    print('Wrote %s.hack (%d instructions) and symbols.txt'
          % (path[:-4], len(out)))


if __name__ == '__main__':
    main()
