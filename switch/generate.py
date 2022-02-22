import io

UNIX_AMD64_REGS = (
    'r12',
    'r13',
    'r14',
    'r15',
    'rbx',
    'rbp',
)
# Unix Exclusions:
# rdi, rsi, rdx, rcx, r8, r9 because they are used for arguments
# rax, r10, r11 because they are considered volatile

WIN_AMD64_REGS = (
    'xmm6',
    'xmm7',
    'xmm8',
    'xmm9',
    'xmm10',
    'xmm11',
    'xmm12',
    'xmm13',
    'xmm14',
    'xmm15',
    'rsi',
    'rdi',
    'rbp',
    'rbx',
    'r12',
    'r13',
    'r14',
    'r15',
)
# Windows Exclusions:
# rcx, rdx, r8, r9, xmm0L, xmm1L, xmm2L, xmm3L because they are used for arguments
# rax, r10, r11, xmm4, xmm5 because they are considered volatile


def generate_win_amd64(fp: io.TextIOBase) -> None:
    regs: list[str] = []
    fp_regs: list[str] = []

    for reg in WIN_AMD64_REGS:
        if reg.startswith('xmm'):
            fp_regs.append(reg)
        else:
            regs.append(reg)

    fp.write('; generated by cultio/switch/generate.py\n')
    fp.write('; Architecture: AMD64\n')
    fp.write('; Platform: Windows\n\n')

    fp.write('BITS 64\n\n')

    fp.write('global switch\n')
    fp.write('section .text\n\n')

    fp.write('switch:\n')

    reserve = (16 * len(fp_regs)) + (8 * (len(regs) + 1))
    fp.write(f'    sub rsp, {reserve}\n')

    stack_offset = 0

    for reg in fp_regs:
        fp.write(f'    movaps [rsp+{hex(stack_offset)}], {reg}\n')
        stack_offset += 16

    for reg in regs:
        fp.write(f'    mov [rsp+{hex(stack_offset)}], {reg}\n')
        stack_offset += 8

    fp.write('\n')
    fp.write('    mov [rcx], rsp\n')
    fp.write('    mov rsp, [rdx]\n\n')

    stack_offset = 0

    for reg in fp_regs:
        fp.write(f'    movaps {reg}, [rsp+{hex(stack_offset)}]\n')
        stack_offset += 16

    for reg in regs:
        fp.write(f'    mov {reg}, [rsp+{hex(stack_offset)}]\n')
        stack_offset += 8

    fp.write(f'    add rsp, {reserve}\n')

    fp.write('\n')
    fp.write('    pop rcx\n')
    fp.write('    jmp [rcx]\n')


def generate_unix_amd64(fp: io.TextIOBase) -> None:
    fp.write('// generated by cultio/switch/generate.py\n')
    fp.write('// Architecture: AMD64\n')
    fp.write('// Platform: Unix\n\n')

    fp.write('.code64\n')
    fp.write('.intel_syntax noprefix\n\n')

    fp.write('.global switch\n')
    fp.write('.text\n\n')

    fp.write('switch:\n')

    reserve = 8 * len(UNIX_AMD64_REGS)
    fp.write(f'    sub rsp, {reserve}\n')

    stack_offset = 0

    for reg in UNIX_AMD64_REGS:
        fp.write(f'    movq QWORD PTR [rsp+{hex(stack_offset)}], {reg}\n')
        stack_offset += 8

    fp.write('\n')
    fp.write('    movq QWORD PTR [rdi], rsp\n')
    fp.write('    movq rsp, QWORD PTR [rsi]\n\n')

    for reg in UNIX_AMD64_REGS:
        fp.write(f'    movq {reg}, QWORD PTR [rsp+{hex(stack_offset)}]\n')
        stack_offset += 8

    fp.write(f'    add rsp, {reserve}\n')

    fp.write('\n')
    fp.write('    popq rcx\n')
    fp.write('    jmpq QWORD PTR [rcx]\n')


if __name__ == '__main__':
    import os

    dirname = os.path.dirname(__file__)

    with open(os.path.join(dirname, 'win_amd64_switch.S'), 'w') as fp:
        generate_win_amd64(fp)

    with open(os.path.join(dirname, 'unix_amd64_switch.S'), 'w') as fp:
        generate_unix_amd64(fp)