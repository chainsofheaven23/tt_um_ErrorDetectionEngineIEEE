# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

def calculate_expected_codeword(data_in):
    """
    Python implementation of the Verilog XOR trees for Hamming(12,8) and CRC-8.
    Matches the logic in serial_error_engine exactly.
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

    # Combine into 20-bit string (MSB of h_bus is shift_reg[19])
    full_codeword = h[::-1] + c[::-1]
    return "".join(map(str, full_codeword))

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # 50 MHz Clock
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # --- Reset ---
    dut._log.info("Resetting...")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # --- Configuration ---
    # You can change this value to test any 8-bit input!
    test_input = 0xAC 
    expected_bin_string = calculate_expected_codeword(test_input)
    
    dut._log.info(f"Testing input {hex(test_input)}")
    dut._log.info(f"Expected 20-bit sequence: {expected_bin_string}")

    # --- Load Data ---
    dut.ui_in.value = test_input
    dut.uio_in.value = 0x01  # Pulse Load (uio_in[0])
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    
    # Wait for the design to capture and start shifting
    await RisingEdge(dut.clk)
    
    # --- Capture and Verify ---
    captured_bits = ""
    for i in range(20):
        # Read bits from the unified ports
        bit = str(int(dut.uo_out.value[0]))
        busy = int(dut.uo_out.value[1])
        
        captured_bits += bit
        
        # Validation checks
        assert busy == 1, f"Busy signal dropped at bit {i}"
        await ClockCycles(dut.clk, 1)

    # --- Final Assertions ---
    dut._log.info(f"Captured: {captured_bits}")
    assert captured_bits == expected_bin_string, f"Mismatch! Expected {expected_bin_string}, got {captured_bits}"
    
    # Check that busy goes low after 20 bits
    await ClockCycles(dut.clk, 1)
    assert int(dut.uo_out.value[1]) == 0, "Busy signal should be low now"
    
    dut._log.info("SUCCESS: Hybrid Codeword matches expected XOR tree output!")
