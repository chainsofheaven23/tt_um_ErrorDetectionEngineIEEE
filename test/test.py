# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles

def calculate_expected_segments(data_in):
    """
    Calculates the three 8-bit segments expected from the mux.
    """
    # Extract bits from data_in (8 bits)
    d = [(data_in >> i) & 1 for i in range(8)]
    
    # Hamming (12,8) XOR Tree (h_bus)
    h = [0] * 12
    h[0]  = d[0]^d[1]^d[3]^d[4]^d[6]
    h[1]  = d[0]^d[2]^d[3]^d[5]^d[6]
    h[2]  = d[0]
    h[3]  = d[1]^d[2]^d[3]^d[7]
    h[4]  = d[1]
    h[5]  = d[2]
    h[6]  = d[3]
    h[7]  = d[4]^d[5]^d[6]^d[7]
    h[8]  = d[4]
    h[9]  = d[5]
    h[10] = d[6]
    h[11] = d[7]

    # CRC-8 XOR Tree (c_res)
    c = [0] * 8
    c[0] = h[11]^h[10]^h[8]^h[4]^h[3]^h[0]
    c[1] = h[11]^h[10]^h[9]^h[8]^h[5]^h[4]^h[1]^h[0]
    c[2] = h[11]^h[10]^h[9]^h[6]^h[5]^h[2]^h[1]^h[0]
    c[3] = h[11]^h[10]^h[7]^h[6]^h[3]^h[2]^h[1]
    c[4] = h[11]^h[8]^h[7]^h[4]^h[3]^h[2]
    c[5] = h[9]^h[8]^h[5]^h[4]^h[3]
    c[6] = h[10]^h[9]^h[6]^h[5]^h[4]
    c[7] = h[11]^h[10]^h[7]^h[6]^h[5]

    # Convert bit arrays to integers (MSB first logic)
    # Segment 0: {4'b0, h[11:8]} 
    seg0 = (h[11] << 3) | (h[10] << 2) | (h[9] << 1) | h[8]
    # Segment 1: h[7:0]
    seg1 = 0
    for i in range(8):
        seg1 |= (h[i] << i)
    # Segment 2: c[7:0]
    seg2 = 0
    for i in range(8):
        seg2 |= (c[i] << i)

    return seg0, seg1, seg2

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Multiplexed Error Engine Test")

    # 50 MHz Clock (Even if design is combinational, TT environment uses it)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # --- Reset ---
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # --- Test Data ---
    test_input = 0xAC 
    s0_exp, s1_exp, s2_exp = calculate_expected_segments(test_input)
    
    dut.ui_in.value = test_input
    dut._log.info(f"Testing input: {hex(test_input)}")

    # --- Verify Segment 0 (Select 00) ---
    dut.uio_in.value = 0 # Select = 00
    await Timer(1, units="ns") # Small delay for combinational logic to settle
    dut._log.info(f"Segment 0 (Hamming MSB): Expected {bin(s0_exp)}, Got {bin(int(dut.uo_out.value))}")
    assert int(dut.uo_out.value) == s0_exp

    # --- Verify Segment 1 (Select 01) ---
    dut.uio_in.value = 1 # Select = 01
    await Timer(1, units="ns")
    dut._log.info(f"Segment 1 (Hamming LSB): Expected {bin(s1_exp)}, Got {bin(int(dut.uo_out.value))}")
    assert int(dut.uo_out.value) == s1_exp

    # --- Verify Segment 2 (Select 10) ---
    dut.uio_in.value = 2 # Select = 10
    await Timer(1, units="ns")
    dut._log.info(f"Segment 2 (CRC-8):       Expected {bin(s2_exp)}, Got {bin(int(dut.uo_out.value))}")
    assert int(dut.uo_out.value) == s2_exp

    # --- Verify Bypass (Select 11) ---
    dut.uio_in.value = 3 # Select = 11
    await Timer(1, units="ns")
    dut._log.info(f"Bypass:                  Expected {hex(test_input)}, Got {hex(int(dut.uo_out.value))}")
    assert int(dut.uo_out.value) == test_input

    dut._log.info("SUCCESS: All Multiplexer segments match expected XOR output!")
