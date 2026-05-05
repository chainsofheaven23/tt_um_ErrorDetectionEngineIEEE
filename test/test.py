# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 20ns (50 MHz as per your info.yaml)
    # Using 20ns matches your 50,000,000 Hz requirement
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # --- Reset Phase ---
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    # Wait 10 cycles for a clean reset
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

    # --- Test Case 1: Valid Data (No Error) ---
    dut._log.info("Test Case 1: Sending valid data 0xA5")
    
    # Assuming ui_in[0] is your serial input or ui_in[7:0] is a parallel byte
    test_data = 0xA5 
    dut.ui_in.value = test_data
    
    # Wait for the engine to process. 
    # If it's a serial engine, you might need 8+ cycles.
    await ClockCycles(dut.clk, 5) 

    # Log the output for debugging
    output_val = int(dut.uo_out.value)
    dut._log.info(f"Output received: {hex(output_val)}")

    # Replace 'expected_val' with what your hardware should actually return
    # assert output_val == expected_val 


    # --- Test Case 2: Data with Error ---
    dut._log.info("Test Case 2: Sending corrupted data")
    
    # Simulate a single bit flip error
    corrupted_data = 0xA4 
    dut.ui_in.value = corrupted_data
    
    await ClockCycles(dut.clk, 5)
    
    dut._log.info(f"Output after error: {hex(int(dut.uo_out.value))}")
    
    # Example assertion: checking if a "status bit" on uo_out[7] goes high
    # assert dut.uo_out.value & 0x80 == 0x80

    dut._log.info("All tests finished")
