from nicegui import ui
from simulator import Computer
from programs import PROGRAMS, load_program_to_ram

computer = Computer()

def binary_to_decimal(binary_value):
    """Convert binary value to decimal"""
    return int(binary_value)

def create_bit_display(label: str, size: int):
    with ui.column().classes('gap-0 items-center'):
        ui.label(label).classes('text-xs font-mono')
        with ui.row().classes('gap-1'):
            bits = [ui.label().classes('w-3 h-6 bg-gray-700 rounded') for _ in range(size)]
    return bits

def update_bit_display(bits, value):
    for i, bit_label in enumerate(bits):
        if (value >> (len(bits) - 1 - i)) & 1:
            bit_label.classes(add='bg-green-500 shadow-glow', remove='bg-gray-700')
        else:
            bit_label.classes(remove='bg-green-500 shadow-glow', add='bg-gray-700')

def create_bus_display():
    with ui.card().classes('p-2 bg-gray-900'):
        with ui.column().classes('items-center gap-1'):
            ui.label('BUS').classes('text-md font-bold')
            with ui.row().classes('gap-2 items-center'):
                bus_strips = []
                for i in reversed(range(8)):
                    with ui.column().classes('gap-0 items-center'):
                        ui.label(f'{i}').classes('text-xs')
                        strip = ui.label().classes('w-4 h-24 bg-gray-800 rounded')
                        bus_strips.append(strip)
            bus_value_label = ui.label('00 (0x00)').classes('font-mono text-sm')
    return bus_strips, bus_value_label

def update_bus_display(strips, value_label, value):
    for i, strip in enumerate(reversed(strips)):
        if (value >> i) & 1:
            strip.classes(add='bg-green-700 shadow-glow-bus', remove='bg-gray-800')
        else:
            strip.classes(remove='bg-green-700 shadow-glow-bus', add='bg-gray-800')
    value_label.set_text(f'{value:02d} (0x{value:02X})')

@ui.page('/')
def main_page():
    ui.add_head_html('<style>.shadow-glow { box-shadow: 0 0 8px 1px #00ff00; } .shadow-glow-bus { box-shadow: 0 0 12px 3px #00ff00; } .active-source { background-color: #2d3748 !important; border: 1px solid #4a5568; } .control-on { background-color: #f59e0b !important; color: black !important; }</style>')
    ui.query('body').style('background-color: #1a1a1a; color: white;')

    with ui.header().classes('bg-gray-900 p-4'):
        ui.label('8-Bit Computer Simulator').classes('text-2xl font-bold')

    # --- State Management ---
    app_state = {'current_address': 0}
    
    def step_and_update():
        if computer.running == False and computer.step_counter > 0:
            print("CPU is halted - use RESET to restart")
            return
        result = computer.step()
        if not result:  # Halted
            run_timer.deactivate()
            ui.notify("CPU HALTED")
        
    run_timer = ui.timer(0.5, step_and_update, active=False)

    with ui.row().classes('w-full p-4 gap-4 flex-nowrap'):
        # Left Column: Memory
        with ui.card().classes('flex-shrink-0 w-80 bg-gray-800'):
            ui.label('Memory Unit').classes('text-lg font-bold')
            mem_cards = []
            with ui.grid(columns=1).classes('gap-2 mt-2'):
                for i in range(16):
                    card = ui.card().classes('p-2 bg-gray-900')
                    with card:
                        with ui.row().classes('items-center gap-2 no-wrap'):
                            ui.label(f'{i:X}').classes('font-mono text-xs')
                            bits = create_bit_display('', 8)
                            mem_cards.append({'card': card, 'bits': bits})

        # Center Column: CPU Core
        with ui.card().classes('flex-grow bg-gray-800 items-center'):
            ui.label('CPU Core').classes('text-lg font-bold')
            
            with ui.row().classes('w-full justify-around mt-4'):
                reg_a_card = ui.card().classes('p-2 bg-gray-900')
                with reg_a_card:
                    reg_a_bits = create_bit_display('A Reg', 8)
                
                reg_b_card = ui.card().classes('p-2 bg-gray-900')
                with reg_b_card:
                    reg_b_bits = create_bit_display('B Reg', 8)

                pc_card = ui.card().classes('p-2 bg-gray-900')
                with pc_card:
                    pc_bits = create_bit_display('PC', 4)

                mar_card = ui.card().classes('p-2 bg-gray-900')
                with mar_card:
                    mar_bits = create_bit_display('MAR', 4)

                ir_card = ui.card().classes('p-2 bg-gray-900')
                with ir_card:
                    ir_bits = create_bit_display('IR', 8)
                
                out_card = ui.card().classes('p-2 bg-gray-900')
                with out_card:
                    out_bits = create_bit_display('OUT', 8)

            # Bus and ALU in the same row
            with ui.row().classes('items-center justify-center gap-8 mt-4'):
                bus_strips, bus_value_label = create_bus_display()
                
                alu_card = ui.card().classes('p-2 bg-gray-900')
                with alu_card:
                    ui.label('ALU').classes('font-bold')
                    with ui.row():
                        z_flag = ui.label('Z').classes('px-2 py-1 rounded bg-gray-700')
                        c_flag = ui.label('C').classes('px-2 py-1 rounded bg-gray-700')
                
                # Output Display Window - shows decimal value
                output_card = ui.card().classes('p-4 bg-gray-900')
                with output_card:
                    ui.label('Output Display').classes('font-bold text-center')
                    output_decimal_label = ui.label('0').classes('text-4xl font-mono text-green-400 text-center mt-2')
                    ui.label('(decimal)').classes('text-xs text-gray-400 text-center')
            
            # Control Signals
            with ui.card().classes('w-full bg-gray-900 mt-4'):
                ui.label("Control Unit").classes('text-md font-bold')
                cpu_control_labels = {}
                with ui.grid(columns=15).classes('gap-2 mt-2'):
                    for signal_name in computer.get_control_signal_names():
                        cpu_control_labels[signal_name] = ui.label(signal_name).classes('px-2 py-1 rounded bg-gray-700 text-xs text-center')

            # Instruction Input Section
            with ui.card().classes('w-full bg-gray-800 mt-4 items-center'):
                ui.label('Instruction Input').classes('text-lg font-bold mb-2')
                with ui.column().classes('gap-4'):
                    with ui.row().classes('items-center justify-center gap-6'):
                        with ui.row(wrap=False).classes('items-center gap-2'):
                            ui.label('Address:').classes('text-sm')
                            address_label = ui.label(f"{app_state['current_address']:02X}").classes('font-mono')

                        with ui.row(wrap=False).classes('items-center gap-2'):
                            ui.label('Opcode:').classes('text-sm')
                            opcode_switches = [ui.switch(value=False) for _ in range(4)]
                        
                        with ui.row(wrap=False).classes('items-center gap-2'):
                            ui.label('Operand:').classes('text-sm')
                            operand_switches = [ui.switch(value=False) for _ in range(4)]

                        instruction_preview = ui.label('=> 0000 0000 (0x00)').classes('font-mono text-lg')

                    def get_instruction_from_switches():
                        opcode = sum(1 << (3-i) for i, s in enumerate(opcode_switches) if s.value)
                        operand = sum(1 << (3-i) for i, s in enumerate(operand_switches) if s.value)
                        return (opcode << 4) | operand

                    def update_preview():
                        instruction = get_instruction_from_switches()
                        opcode = instruction >> 4
                        operand = instruction & 0x0F
                        instruction_preview.set_text(f'=> {opcode:04b} {operand:04b} (0x{instruction:02X})')

                    for switch in opcode_switches + operand_switches:
                        switch.on('update:model-value', update_preview)
                    
                    def load_instruction():
                        instruction = get_instruction_from_switches()
                        computer.ram.write(app_state['current_address'], instruction)
                        ui.notify(f"Loaded 0x{instruction:02X} into RAM address 0x{app_state['current_address']:02X}")
                        app_state['current_address'] = (app_state['current_address'] + 1) % 16
                        address_label.set_text(f"{app_state['current_address']:02X}")

                    def next_address():
                        app_state['current_address'] = (app_state['current_address'] + 1) % 16
                        address_label.set_text(f"{app_state['current_address']:02X}")

                    def prev_address():
                        app_state['current_address'] = (app_state['current_address'] - 1) % 16
                        address_label.set_text(f"{app_state['current_address']:02X}")

                    with ui.row().classes('items-center justify-center gap-4'):
                        ui.button('PREV ADDR', on_click=prev_address)
                        ui.button('LOAD', on_click=load_instruction)
                        ui.button('NEXT ADDR', on_click=next_address)
                        
            # Program Loading Section
            with ui.card().classes('w-full bg-gray-800 mt-4'):
                ui.label('Pre-built Programs').classes('text-lg font-bold mb-2')
                ui.label('Load complete programs into RAM with one click:').classes('text-sm text-gray-300 mb-3')
                
                def load_program(program):
                    load_program_to_ram(computer, program['data'])
                    computer.reset()  # Reset CPU state but keep RAM
                    app_state['current_address'] = 0
                    address_label.set_text(f"{app_state['current_address']:02X}")
                    ui.notify(f"Loaded '{program['name']}' - {program['description']}")
                
                with ui.grid(columns=2).classes('gap-2'):
                    for program in PROGRAMS:
                        with ui.card().classes('p-3 bg-gray-900 cursor-pointer hover:bg-gray-800'):
                            ui.label(program['name']).classes('font-bold text-sm')
                            ui.label(program['description']).classes('text-xs text-gray-400 mt-1')
                            ui.button('LOAD', on_click=lambda p=program: load_program(p)).classes('mt-2 w-full')

        # Right Column: Opcode Reference  
        with ui.card().classes('flex-shrink-0 w-80 bg-gray-800'):
            ui.label('Opcode Reference').classes('text-lg font-bold mb-2')
            with ui.column().classes('gap-1'):
                opcodes = {
                    "NOP": 0x0, "LDA": 0x1, "ADD": 0x2, "SUB": 0x3,
                    "STA": 0x4, "LDI": 0x5, "JMP": 0x6, "JC": 0x7,
                    "JZ": 0x8, "LDB": 0x9, "STB": 0xA, "ADB": 0xB,
                    "SBB": 0xC, "CMP": 0xD, "OUT": 0xE, "HLT": 0xF,
                }
                descriptions = {
                    "NOP": "No operation", "LDA": "Load A from RAM", "ADD": "Add RAM to A",
                    "SUB": "Subtract RAM from A", "STA": "Store A to RAM", "LDI": "Load immediate to A",
                    "JMP": "Jump to address", "JC": "Jump if Carry", "JZ": "Jump if Zero",
                    "LDB": "Load B from RAM", "STB": "Store B to RAM", "ADB": "Add B to A",
                    "SBB": "Subtract B from A", "CMP": "Compare A with RAM",
                    "OUT": "Output A to display", "HLT": "Halt execution",
                }

                for mnemonic, code in opcodes.items():
                    with ui.row().classes('gap-2 items-center text-sm'):
                        ui.label(mnemonic).classes('font-mono w-8 text-green-400')
                        ui.label(f'{code:04b}').classes('font-mono w-10')
                        ui.label(f'0x{code:X}').classes('font-mono w-6')
                        ui.label(descriptions.get(mnemonic, '')).classes('text-xs text-gray-300')
            
            # Control Signals Reference
            ui.label('Control Signals').classes('text-lg font-bold mb-2 mt-4')
            with ui.column().classes('gap-1'):
                control_signals = {
                    "CO": "PC Out", "MI": "MAR In", "RO": "RAM Out", "II": "IR In",
                    "IO": "IR Out", "AI": "A Reg In", "AO": "A Reg Out", "EO": "ALU Out",
                    "SU": "ALU Subtract", "RI": "RAM In", "BI": "B Reg In", "BO": "B Reg Out",
                    "OI": "OUT Reg In", "J": "Jump (PC In)", "HLT": "Halt"
                }

                reference_control_labels = {}
                for signal, description in control_signals.items():
                    with ui.row().classes('gap-2 items-center text-sm'):
                        reference_control_labels[signal] = ui.label(signal).classes('font-mono w-8 text-yellow-400 bg-gray-700 p-1 rounded')
                        ui.label(description).classes('text-xs text-gray-300')

    with ui.footer().classes('bg-gray-900 p-4'):
        with ui.row().classes('w-full items-center justify-center gap-4'):
            ui.label('Clock Control').classes('text-lg font-bold')
            ui.button('STEP', on_click=step_and_update)
            ui.button('RUN', on_click=run_timer.activate)
            ui.button('STOP', on_click=run_timer.deactivate)
            
            def reset_all():
                run_timer.deactivate()
                computer.reset()
                app_state['current_address'] = 0
                ui.notify("CPU reset - registers cleared, RAM preserved")
            
            def reset_ram():
                for i in range(16):
                    computer.ram.write(i, 0)
                ui.notify("RAM cleared - all addresses set to 0x00")
            
            ui.button('RESET', on_click=reset_all)
            ui.button('RESET RAM', on_click=reset_ram)
            
            speed_slider = ui.slider(min=0.1, max=2.0, step=0.1, value=0.5).classes('w-64')
            speed_slider.on('update:model-value', lambda e: setattr(run_timer, 'interval', e.args))

    def update_ui():
        # Update registers and CPU state
        update_bit_display(reg_a_bits, computer.reg_a_value)
        update_bit_display(reg_b_bits, computer.reg_b_value)
        update_bit_display(pc_bits, computer.pc_value)
        update_bit_display(mar_bits, computer.mar_value)
        update_bit_display(ir_bits, computer.ir_value)
        update_bit_display(out_bits, computer.out_value)
        update_bus_display(bus_strips, bus_value_label, computer.bus_value)
        
        # Update output decimal display
        output_decimal_label.set_text(str(binary_to_decimal(computer.out_value)))
        
        # Update flags
        z_flag.classes(add='bg-yellow-500', remove='bg-gray-700') if computer.flags['Z'] else z_flag.classes(remove='bg-yellow-500', add='bg-gray-700')
        c_flag.classes(add='bg-yellow-500', remove='bg-gray-700') if computer.flags['C'] else c_flag.classes(remove='bg-yellow-500', add='bg-gray-700')

        # Update memory displays
        for i, mem_ui in enumerate(mem_cards):
            update_bit_display(mem_ui['bits'], computer.ram.read(i))
            # Highlight current MAR address in memory
            if i == computer.mar_value:
                 mem_ui['card'].classes(add='active-source')
            else:
                 mem_ui['card'].classes(remove='active-source')


        # Update control signals (CPU indicators, not reference)
        active_signals = computer.get_active_control_signals()
        for name, label in cpu_control_labels.items():
            if name in active_signals:
                label.classes(add='control-on', remove='bg-gray-700')
            else:
                label.classes(remove='control-on', add='bg-gray-700')

        # Update active source highlighting  
        source_map = {
            'CO': pc_card, 'RO': mem_cards[computer.mar_value]['card'], 'IO': ir_card,
            'AO': reg_a_card, 'EO': alu_card
        }
        # Clear all highlights first
        all_cards = [reg_a_card, reg_b_card, pc_card, mar_card, ir_card, out_card, alu_card]
        for card in all_cards:
            card.classes(remove='active-source')
        
        # Apply highlight to the active source
        for signal in active_signals:
            if signal in source_map:
                source_map[signal].classes(add='active-source')
            
    ui.timer(0.05, update_ui)

ui.run(port=8080, reload=False, dark=True, title="8-bit Computer Simulator")
