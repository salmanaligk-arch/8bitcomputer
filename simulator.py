"""
Backend for 8-Bit Computer Simulator
Provides Computer class using tiny8 CPU for app.py frontend
"""

from tiny8 import CPU, assemble

class Computer:
    """8-bit computer simulation backend using tiny8 CPU"""
    
    def __init__(self):
        self.cpu = CPU()
        self.running = False
        
        # RAM simulation (16 bytes for 8-bit computer)
        self.ram = RAM()
        
        # Simulated 8-bit computer state
        self.reg_a_value = 0
        self.reg_b_value = 0
        self.pc_value = 0
        self.mar_value = 0
        self.ir_value = 0
        self.out_value = 0
        self.bus_value = 0
        self.flags = {'Z': False, 'C': False}
        
        # Control signals simulation
        self.active_signals = []
        
        # Simulation state for visual effects
        self.step_counter = 0
        self.fetch_phase = 0  # 0=fetch addr, 1=fetch instr, 2=decode, 3=execute
        self.running = True  # Add running state
        
        # Control signal bit patterns
        self.CO = 0x001   # PC Out
        self.MI = 0x002   # MAR In  
        self.RO = 0x004   # RAM Out
        self.II = 0x008   # IR In
        self.IO = 0x010   # IR Out
        self.AI = 0x020   # A Reg In
        self.AO = 0x040   # A Reg Out
        self.EO = 0x080   # ALU Out
        self.SU = 0x100   # ALU Subtract
        self.RI = 0x200   # RAM In
        self.BI = 0x400   # B Reg In
        self.BO = 0x800   # B Reg Out
        self.OI = 0x1000  # OUT Reg In
        self.J = 0x2000   # Jump (PC In)
        self.HLT = 0x4000 # Halt
        
        self.control_word = 0
        
    def get_control_signal_names(self):
        """Return list of control signal names for UI"""
        return ["CO", "MI", "RO", "II", "IO", "AI", "AO", "EO", 
                "SU", "RI", "BI", "BO", "OI", "J", "HLT"]
    
    def get_active_control_signals(self):
        """Return currently active control signals"""
        return self.active_signals.copy()
        
    def step(self):
        """Execute one instruction step with visual simulation"""
        try:
            # Always increment step counter for visual effects
            self.step_counter += 1
            self.fetch_phase = self.step_counter % 4
            
            # Simulate fetch-decode-execute cycle
            if self.fetch_phase == 0:
                # Fetch phase 1: PC -> MAR
                self.active_signals = ["CO", "MI"]
                self.mar_value = self.pc_value
                self.bus_value = self.pc_value
                
            elif self.fetch_phase == 1:
                # Fetch phase 2: RAM -> IR
                self.active_signals = ["RO", "II"]
                self.ir_value = self.ram.read(self.mar_value)
                self.bus_value = self.ir_value
                
            elif self.fetch_phase == 2:
                # Decode phase: IR -> Control Unit
                self.active_signals = ["IO"]
                # Extract opcode and operand
                opcode = (self.ir_value >> 4) & 0xF
                operand = self.ir_value & 0xF
                
            else:
                # Execute phase: depends on instruction
                opcode = (self.ir_value >> 4) & 0xF
                operand = self.ir_value & 0xF
                
                if opcode == 0x0:  # NOP
                    self.active_signals = []
                    # No operation, just continue
                    
                elif opcode == 0x1:  # LDA
                    self.active_signals = ["RO", "AI"]
                    self.mar_value = operand
                    self.reg_a_value = self.ram.read(operand)
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0x2:  # ADD
                    self.active_signals = ["RO", "EO", "AI"]
                    self.mar_value = operand
                    result = self.reg_a_value + self.ram.read(operand)
                    self.flags['C'] = result > 255
                    self.reg_a_value = result & 0xFF
                    self.flags['Z'] = self.reg_a_value == 0
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0x3:  # SUB
                    self.active_signals = ["RO", "EO", "SU", "AI"]
                    self.mar_value = operand
                    result = self.reg_a_value - self.ram.read(operand)
                    self.flags['C'] = result < 0
                    self.reg_a_value = result & 0xFF
                    self.flags['Z'] = self.reg_a_value == 0
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0x4:  # STA
                    self.active_signals = ["AO", "RI"]
                    self.mar_value = operand
                    self.ram.write(operand, self.reg_a_value)
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0x5:  # LDI
                    self.active_signals = ["AI"]
                    self.reg_a_value = operand
                    self.bus_value = operand
                    
                elif opcode == 0x6:  # JMP
                    self.active_signals = ["J"]
                    self.pc_value = operand
                    self.bus_value = operand
                    return True  # Skip PC increment
                    
                elif opcode == 0x7:  # JC (Jump if Carry)
                    if self.flags['C']:
                        self.active_signals = ["J"]
                        self.pc_value = operand
                        self.bus_value = operand
                        return True  # Skip PC increment
                    else:
                        self.active_signals = []
                        
                elif opcode == 0x8:  # JZ (Jump if Zero)
                    if self.flags['Z']:
                        self.active_signals = ["J"]
                        self.pc_value = operand
                        self.bus_value = operand
                        return True  # Skip PC increment
                    else:
                        self.active_signals = []
                        
                elif opcode == 0x9:  # LDB
                    self.active_signals = ["RO", "BI"]
                    self.mar_value = operand
                    self.reg_b_value = self.ram.read(operand)
                    self.bus_value = self.reg_b_value
                    
                elif opcode == 0xA:  # STB
                    self.active_signals = ["BO", "RI"]
                    self.mar_value = operand
                    self.ram.write(operand, self.reg_b_value)
                    self.bus_value = self.reg_b_value
                    
                elif opcode == 0xB:  # ADB (Add B to A)
                    self.active_signals = ["BO", "EO", "AI"]
                    result = self.reg_a_value + self.reg_b_value
                    self.flags['C'] = result > 255
                    self.reg_a_value = result & 0xFF
                    self.flags['Z'] = self.reg_a_value == 0
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0xC:  # SBB (Subtract B from A)
                    self.active_signals = ["BO", "EO", "SU", "AI"]
                    result = self.reg_a_value - self.reg_b_value
                    self.flags['C'] = result < 0
                    self.reg_a_value = result & 0xFF
                    self.flags['Z'] = self.reg_a_value == 0
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0xD:  # CMP (Compare A with RAM)
                    self.active_signals = ["RO", "EO", "SU"]
                    self.mar_value = operand
                    result = self.reg_a_value - self.ram.read(operand)
                    self.flags['C'] = result < 0
                    self.flags['Z'] = result == 0
                    # Don't store result in A for compare
                    
                elif opcode == 0xE:  # OUT
                    self.active_signals = ["AO", "OI"]
                    self.out_value = self.reg_a_value
                    self.bus_value = self.reg_a_value
                    
                elif opcode == 0xF:  # HLT
                    self.active_signals = ["HLT"]
                    self.running = False
                    print("HALT instruction executed - CPU stopped")
                    return False  # Signal halt to stop execution
                    
                else:
                    # Unknown instruction - treat as NOP
                    self.active_signals = []
                
                # Only increment PC if not a jump instruction that was taken
                if opcode not in [0x6] and not (opcode == 0x7 and self.flags['C']) and not (opcode == 0x8 and self.flags['Z']) and opcode != 0xF:
                    self.pc_value = (self.pc_value + 1) % 16
                
            return True
        except Exception as e:
            print(f"Step error: {e}")
            return False
    
    def update_state_from_cpu(self):
        """Update 8-bit computer state from tiny8 CPU state"""
        # Map tiny8 registers to our 8-bit computer registers
        if hasattr(self.cpu, 'regs') and len(self.cpu.regs) > 1:
            self.reg_a_value = self.cpu.read_reg(0)  # R0 as A register
            self.reg_b_value = self.cpu.read_reg(1)  # R1 as B register
            
        self.pc_value = self.cpu.pc & 0xF  # 4-bit PC for 16-byte memory
        
        # Update memory from tiny8 to our 16-byte simulation
        if hasattr(self.cpu, 'mem') and hasattr(self.cpu.mem, 'ram'):
            for i in range(min(16, len(self.cpu.mem.ram))):
                value = self.cpu.read_ram(i) if hasattr(self.cpu, 'read_ram') else self.cpu.mem.ram[i]
                self.ram.write(i, value)
        
        # Update flags from CPU
        if hasattr(self.cpu, 'get_flag'):
            self.flags['Z'] = self.cpu.get_flag(1)  # Z flag bit
            self.flags['C'] = self.cpu.get_flag(0)  # C flag bit
        elif hasattr(self.cpu, 'sreg'):
            self.flags['Z'] = bool(self.cpu.sreg & 0x02)  # Z flag
            self.flags['C'] = bool(self.cpu.sreg & 0x01)  # C flag
            
        # Simulate control signals
        self.simulate_control_signals()
        
    def simulate_control_signals(self):
        """Simulate control signals for visualization"""
        self.active_signals = []
        
        # Simple simulation - show fetch cycle signals
        if hasattr(self.cpu, 'step_count'):
            step = self.cpu.step_count % 4
            if step == 0:
                self.active_signals = ["CO", "MI"]  # PC out, MAR in
            elif step == 1:
                self.active_signals = ["RO", "II"]  # RAM out, IR in
            elif step == 2:
                # Decode phase - show IR output
                self.active_signals = ["IO"]
            else:
                # Execute phase - varies by instruction
                self.active_signals = ["AI"]  # Example: A register in
                
    def reset(self):
        """Reset the computer CPU progress only (not RAM)"""
        self.cpu = CPU()
        self.running = True
        self.reg_a_value = 0
        self.reg_b_value = 0 
        self.pc_value = 0
        self.mar_value = 0
        self.ir_value = 0
        self.out_value = 0
        self.bus_value = 0
        self.flags = {'Z': False, 'C': False}
        self.active_signals = []
        self.step_counter = 0
        self.fetch_phase = 0
        
        # Don't reset RAM - keep user programs intact
    
    def load_program(self, program):
        """Load a program into the CPU"""
        if hasattr(self.cpu, 'load_program'):
            self.cpu.load_program(program)
            self.update_state_from_cpu()
            
    def assemble_and_load(self, assembly_code): 
        """Assemble code and load into CPU"""
        try:
            result = assemble(assembly_code)
            self.load_program(result)
            return True
        except Exception as e:
            print(f"Assembly error: {e}")
            return False

class RAM:
    """16-byte RAM for 8-bit computer simulation"""
    def __init__(self, size=16):
        self.size = size
        self._memory = [0] * size
        
    def read(self, address):
        if 0 <= address < self.size:
            return self._memory[address]
        return 0
        
    def write(self, address, value):
        if 0 <= address < self.size:
            self._memory[address] = value & 0xFF