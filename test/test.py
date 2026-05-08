# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

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
    Calculates the expected 8-bit outputs.
    """

    # Extract bits
    d = [(data_in >> i) & 1 for i in range(8)]

    # Hamming(12,8)
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

    # CRC-8
    c = [0] * 8
    c[0] = h[11]^h[10]^h[8]^h[4]^h[3]^h[0]
    c[1] = h[11]^h[10]^h[9]^h[8]^h[5]^h[4]^h[1]^h[0]
    c[2] = h[11]^h[10]^h[9]^h[6]^h[5]^h[2]^h[1]^h[0]
    c[3] = h[11]^h[10]^h[7]^h[6]^h[3]^h[2]^h[1]
    c[4] = h[11]^h[8]^h[7]^h[4]^h[3]^h[2]
    c[5] = h[9]^h[8]^h[5]^h[4]^h[3]
    c[6] = h[10]^h[9]^h[6]^h[5]^h[4]
    c[7] = h[11]^h[10]^h[7]^h[6]^h[5]

    # Segment 0 -> {4'b0, h[11:8]}
    seg0 = (
        (h[11] << 3) |
        (h[10] << 2) |
        (h[9]  << 1) |
        h[8]
    )

    # Segment 1 -> h[7:0]
    seg1 = 0
    for i in range(8):
        seg1 |= (h[i] << i)

    # Segment 2 -> c[7:0]
    seg2 = 0
    for i in range(8):
        seg2 |= (c[i] << i)

    return seg0, seg1, seg2


@cocotb.test()
async def test_project(dut):

    dut._log.info("Starting Multiplexed Error Engine Test")

    # Start clock
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # ---------------- RESET ----------------
    dut.ena.value = 1

    dut.ui_in.value = 0x00

    # IMPORTANT for GL simulation
    dut.uio_in.value = 0x00
    dut.uio_oe.value = 0x00

    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    await ClockCycles(dut.clk, 5)

    # ---------------- TEST INPUT ----------------
    test_input = 0xAC

    s0_exp, s1_exp, s2_exp = calculate_expected_segments(test_input)

    dut.ui_in.value = test_input

    await Timer(10, units="ns")

    dut._log.info(f"Testing input = 0x{test_input:02X}")

    # ---------------- SEGMENT 0 ----------------
    dut.uio_in.value = 0b00000000

    await Timer(10, units="ns")

    seg0_got = int(dut.uo_out.value)

    dut._log.info(
        f"SEG0 Expected = 0x{s0_exp:02X}, Got = 0x{seg0_got:02X}"
    )

    assert seg0_got == s0_exp

    # ---------------- SEGMENT 1 ----------------
    dut.uio_in.value = 0b00000001

    await Timer(10, units="ns")

    seg1_got = int(dut.uo_out.value)

    dut._log.info(
        f"SEG1 Expected = 0x{s1_exp:02X}, Got = 0x{seg1_got:02X}"
    )

    assert seg1_got == s1_exp

    # ---------------- SEGMENT 2 ----------------
    dut.uio_in.value = 0b00000010

    await Timer(10, units="ns")

    seg2_got = int(dut.uo_out.value)

    dut._log.info(
        f"SEG2 Expected = 0x{s2_exp:02X}, Got = 0x{seg2_got:02X}"
    )

    assert seg2_got == s2_exp

    # ---------------- BYPASS ----------------
    dut.uio_in.value = 0b00000011

    await Timer(10, units="ns")

    bypass_got = int(dut.uo_out.value)

    dut._log.info(
        f"BYPASS Expected = 0x{test_input:02X}, Got = 0x{bypass_got:02X}"
    )

    assert bypass_got == test_input

    dut._log.info("SUCCESS: All tests passed!")
