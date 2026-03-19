"""
Pre-built programs for the 8-bit computer simulator
Each program is a dictionary with 'name', 'description', and 'data' (list of 16 bytes)
"""

# Fibonacci Sequence Program - Calculates first 5 Fibonacci numbers
fibonacci_program = {
    'name': 'Fibonacci Sequence',
    'description': 'Calculates and displays the first 5 Fibonacci numbers (0,1,1,2,3)',
    'data': [
        0x00,  # 0x0: F0 = 0
        0x01,  # 0x1: F1 = 1  
        0x05,  # 0x2: N = 5 (counter)
        0x01,  # 0x3: CONST 1 (decrement value)
        0x10,  # 0x4: LDA 0x0 (load F0)
        0xE0,  # 0x5: OUT (display current Fibonacci number)
        0x91,  # 0x6: LDB 0x1 (load F1 into B)
        0xB0,  # 0x7: ADB (A = A + B, next Fibonacci)
        0x41,  # 0x8: STA 0x1 (store new F1)
        0xA0,  # 0x9: STB 0x0 (store old F0)
        0x12,  # 0xA: LDA 0x2 (load counter N)
        0x33,  # 0xB: SUB 0x3 (N = N - 1)
        0x42,  # 0xC: STA 0x2 (store new counter)
        0x8F,  # 0xD: JZ 0xF (jump to halt if N=0)
        0x64,  # 0xE: JMP 0x4 (loop back)
        0xF0   # 0xF: HLT (halt)
    ]
}

# Simple Counter Program - Counts from 0 to 10
counter_program = {
    'name': 'Counter 0-10',
    'description': 'Counts from 0 to 10 and displays each number',
    'data': [
        0x00,  # 0x0: counter = 0
        0x0A,  # 0x1: limit = 10
        0x01,  # 0x2: increment = 1
        0x00,  # 0x3: unused
        0x10,  # 0x4: LDA 0x0 (load counter)
        0xE0,  # 0x5: OUT (display counter)
        0x22,  # 0x6: ADD 0x2 (counter = counter + 1)
        0x40,  # 0x7: STA 0x0 (store new counter)
        0x31,  # 0x8: SUB 0x1 (compare with limit)
        0x8B,  # 0x9: JZ 0xB (jump to halt if equal)
        0x64,  # 0xA: JMP 0x4 (loop back)
        0xF0,  # 0xB: HLT (halt)
        0x00,  # 0xC: unused
        0x00,  # 0xD: unused
        0x00,  # 0xE: unused
        0x00   # 0xF: unused
    ]
}

# Addition Program - Adds two numbers
addition_program = {
    'name': 'Add Two Numbers',
    'description': 'Adds 7 + 5 = 12 and displays the result',
    'data': [
        0x07,  # 0x0: first number = 7
        0x05,  # 0x1: second number = 5
        0x00,  # 0x2: result (will be calculated)
        0x00,  # 0x3: unused
        0x10,  # 0x4: LDA 0x0 (load first number)
        0x21,  # 0x5: ADD 0x1 (add second number)
        0x42,  # 0x6: STA 0x2 (store result)
        0xE0,  # 0x7: OUT (display result)
        0xF0,  # 0x8: HLT (halt)
        0x00,  # 0x9: unused
        0x00,  # 0xA: unused
        0x00,  # 0xB: unused
        0x00,  # 0xC: unused
        0x00,  # 0xD: unused
        0x00,  # 0xE: unused
        0x00   # 0xF: unused
    ]
}

# Multiplication by Repeated Addition - Multiplies 4 * 3
multiplication_program = {
    'name': 'Multiply 4 × 3',
    'description': 'Multiplies 4 × 3 = 12 using repeated addition',
    'data': [
        0x04,  # 0x0: multiplicand = 4
        0x03,  # 0x1: multiplier = 3 (counter)
        0x00,  # 0x2: result = 0
        0x01,  # 0x3: decrement = 1
        0x12,  # 0x4: LDA 0x2 (load result)
        0x20,  # 0x5: ADD 0x0 (add multiplicand)
        0x42,  # 0x6: STA 0x2 (store new result)
        0x11,  # 0x7: LDA 0x1 (load counter)
        0x33,  # 0x8: SUB 0x3 (decrement counter)
        0x41,  # 0x9: STA 0x1 (store new counter)
        0x8C,  # 0xA: JZ 0xC (jump to output if done)
        0x64,  # 0xB: JMP 0x4 (loop back)
        0x12,  # 0xC: LDA 0x2 (load result)
        0xE0,  # 0xD: OUT (display result)
        0xF0,  # 0xE: HLT (halt)
        0x00   # 0xF: unused
    ]
}

# Simple Blink Pattern - Alternates between 0 and 255
blink_program = {
    'name': 'Blink Pattern',
    'description': 'Alternates between displaying 0 and 255 (all LEDs on/off)',
    'data': [
        0x00,  # 0x0: value 0 (LEDs off)
        0xFF,  # 0x1: value 255 (LEDs on)
        0x00,  # 0x2: unused
        0x00,  # 0x3: unused
        0x10,  # 0x4: LDA 0x0 (load 0)
        0xE0,  # 0x5: OUT (display 0)
        0x11,  # 0x6: LDA 0x1 (load 255)
        0xE0,  # 0x7: OUT (display 255)
        0x64,  # 0x8: JMP 0x4 (loop back)
        0x00,  # 0x9: unused
        0x00,  # 0xA: unused
        0x00,  # 0xB: unused
        0x00,  # 0xC: unused
        0x00,  # 0xD: unused
        0x00,  # 0xE: unused
        0x00   # 0xF: unused
    ]
}

# Collect all programs in a list
PROGRAMS = [
    fibonacci_program,
    counter_program,
    addition_program,
    multiplication_program,
    blink_program
]

def load_program_to_ram(computer, program_data):
    """Load a program (list of 16 bytes) into the computer's RAM"""
    for address, data in enumerate(program_data):
        if address < 16:  # Ensure we don't exceed RAM bounds
            computer.ram.write(address, data)

def get_program_by_name(name):
    """Get a program by its name"""
    for program in PROGRAMS:
        if program['name'] == name:
            return program
    return None