# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start Multiplexed Error Engine Test")

    # 50 MHz Clock
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # --- Reset ---
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    # Increase delay to allow GL netlist to stabilize after reset
    await ClockCycles(dut.clk, 5)

    # --- Test Data ---
    test_input = 0xAC 
    s0_exp, s1_exp, s2_exp = calculate_expected_segments(test_input)
    
    dut.ui_in.value = test_input
    dut._log.info(f"Testing input: {hex(test_input)}")

    # Helper function to read uo_out safely for GL tests
    def get_uo_out():
        try:
            return int(dut.uo_out.value)
        except ValueError:
            return None

    # --- Verify Segment 0 (Select 00) ---
    dut.uio_in.value = 0 
    await Timer(5, units="ns") # Increased timer for GL propagation delays
    val = get_uo_out()
    assert val is not None, "uo_out contains 'x' or 'z' during GL test!"
    dut._log.info(f"Segment 0: Expected {bin(s0_exp)}, Got {bin(val)}")
    assert val == s0_exp

    # --- Verify Segment 1 (Select 01) ---
    dut.uio_in.value = 1 
    await Timer(5, units="ns")
    val = get_uo_out()
    dut._log.info(f"Segment 1: Expected {bin(s1_exp)}, Got {bin(val)}")
    assert val == s1_exp

    # --- Verify Segment 2 (Select 10) ---
    dut.uio_in.value = 2 
    await Timer(5, units="ns")
    val = get_uo_out()
    dut._log.info(f"Segment 2: Expected {bin(s2_exp)}, Got {bin(val)}")
    assert val == s2_exp

    # --- Verify Bypass (Select 11) ---
    dut.uio_in.value = 3 
    await Timer(5, units="ns")
    val = get_uo_out()
    dut._log.info(f"Bypass: Expected {hex(test_input)}, Got {hex(val)}")
    assert val == test_input

    dut._log.info("SUCCESS: All Multiplexer segments match expected XOR output!")
