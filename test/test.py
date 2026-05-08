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


@cocotb.test()
async def test_project(dut):

    # Start clock
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset + initialize signals
    dut.ena.value = 1
    dut.rst_n.value = 0

    dut.ui_in.value = 0

    # Important for GL sim
    dut.uio_in.value = 0
    dut.uio_oe.value = 0xFF

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    await ClockCycles(dut.clk, 5)

    # ---------------- TEST 1 ----------------
    dut.ui_in.value = 0xAC
    dut.uio_in.value = 0b00000000

    await Timer(20, units="ns")

    dut._log.info(f"TEST1 Output = {dut.uo_out.value}")

    assert "x" not in str(dut.uo_out.value).lower()
    assert "z" not in str(dut.uo_out.value).lower()

    # ---------------- TEST 2 ----------------
    dut.ui_in.value = 0x55
    dut.uio_in.value = 0b00000001

    await Timer(20, units="ns")

    dut._log.info(f"TEST2 Output = {dut.uo_out.value}")

    assert "x" not in str(dut.uo_out.value).lower()
    assert "z" not in str(dut.uo_out.value).lower()

    # ---------------- TEST 3 ----------------
    dut.ui_in.value = 0xF0
    dut.uio_in.value = 0b00000010

    await Timer(20, units="ns")

    dut._log.info(f"TEST3 Output = {dut.uo_out.value}")

    assert "x" not in str(dut.uo_out.value).lower()
    assert "z" not in str(dut.uo_out.value).lower()

    dut._log.info("Simple GL test passed")
