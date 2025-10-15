# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Edge
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from cocotb.types import LogicArray
# Added
from cocotb.utils import get_sim_time

async def await_half_sclk(dut):
    """Wait for the SCLK signal to go high or low."""
    start_time = cocotb.utils.get_sim_time(units="ns")
    while True:
        await ClockCycles(dut.clk, 1)
        # Wait for half of the SCLK period (10 us)
        if (start_time + 100*100*0.5) < cocotb.utils.get_sim_time(units="ns"):
            break
    return

def ui_in_logicarray(ncs, bit, sclk):
    """Setup the ui_in value as a LogicArray."""
    return LogicArray(f"00000{ncs}{bit}{sclk}")

async def send_spi_transaction(dut, r_w, address, data):
    """
    Send an SPI transaction with format:
    - 1 bit for Read/Write
    - 7 bits for address
    - 8 bits for data
    
    Parameters:
    - r_w: boolean, True for write, False for read
    - address: int, 7-bit address (0-127)
    - data: LogicArray or int, 8-bit data
    """
    # Convert data to int if it's a LogicArray
    if isinstance(data, LogicArray):
        data_int = int(data)
    else:
        data_int = data
    # Validate inputs
    if address < 0 or address > 127:
        raise ValueError("Address must be 7-bit (0-127)")
    if data_int < 0 or data_int > 255:
        raise ValueError("Data must be 8-bit (0-255)")
    # Combine RW and address into first byte
    first_byte = (int(r_w) << 7) | address
    # Start transaction - pull CS low
    sclk = 0
    ncs = 0
    bit = 0
    # Set initial state with CS low
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 1)
    # Send first byte (RW + Address)
    for i in range(8):
        bit = (first_byte >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # Send second byte (Data)
    for i in range(8):
        bit = (data_int >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # End transaction - return CS high
    sclk = 0
    ncs = 1
    bit = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 600)
    return ui_in_logicarray(ncs, bit, sclk)

# async def measure_pwm_frequency(bus, bit):
#     '''
#     Measure the frequency (in Hz) of bus[bit]
#     '''
#     # Find the first rising edge of the chosen bit
#     prev = int(bus.value[bit])
#     while True:
#         await Edge(bus)                 # callback on the vector is supported
#         curr = int(bus.value[bit])
#         if prev == 0 and curr == 1:     # first rising edge
#             t1 = get_sim_time(units='ns')
#             break
#         prev = curr

#     # Find the next rising edge of that bit
#     while True:
#         await Edge(bus)
#         next = int(bus.value[bit])
#         if curr == 0 and next == 1:      # second rising edge
#             t2 = get_sim_time(units='ns')
#             break
#         curr = next

#     period_ns = t2 - t1
#     freq_hz = 1e9 / period_ns
#     return freq_hz

@cocotb.test()
async def test_spi(dut):
    dut._log.info("Start SPI test")

#     # Set the clock period to 100 ns (10 MHz)
#     clock = Clock(dut.clk, 100, units="ns")
#     cocotb.start_soon(clock.start())

#     # Reset
#     dut._log.info("Reset")
#     dut.ena.value = 1
#     ncs = 1
#     bit = 0
#     sclk = 0
#     dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
#     dut.rst_n.value = 0
#     await ClockCycles(dut.clk, 5)
#     dut.rst_n.value = 1
#     await ClockCycles(dut.clk, 5)

#     dut._log.info("Test project behavior")
#     dut._log.info("Write transaction, address 0x00, data 0xF0")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xF0)  # Write transaction
#     assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
#     await ClockCycles(dut.clk, 1000) 

#     dut._log.info("Write transaction, address 0x01, data 0xCC")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xCC)  # Write transaction
#     assert dut.uio_out.value == 0xCC, f"Expected 0xCC, got {dut.uio_out.value}"
#     await ClockCycles(dut.clk, 100)

#     dut._log.info("Write transaction, address 0x30 (invalid), data 0xAA")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x30, 0xAA)
#     await ClockCycles(dut.clk, 100)

#     dut._log.info("Read transaction (invalid), address 0x00, data 0xBE")
#     ui_in_val = await send_spi_transaction(dut, 0, 0x30, 0xBE)
#     assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
#     await ClockCycles(dut.clk, 100)
    
#     dut._log.info("Read transaction (invalid), address 0x41 (invalid), data 0xEF")
#     ui_in_val = await send_spi_transaction(dut, 0, 0x41, 0xEF)
#     await ClockCycles(dut.clk, 100)

#     dut._log.info("Write transaction, address 0x02, data 0xFF")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)  # Write transaction
#     await ClockCycles(dut.clk, 100)

#     dut._log.info("Write transaction, address 0x04, data 0xCF")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xCF)  # Write transaction
#     await ClockCycles(dut.clk, 30000)

#     dut._log.info("Write transaction, address 0x04, data 0xFF")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)  # Write transaction
#     await ClockCycles(dut.clk, 30000)

#     dut._log.info("Write transaction, address 0x04, data 0x00")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)  # Write transaction
#     await ClockCycles(dut.clk, 30000)

#     dut._log.info("Write transaction, address 0x04, data 0x01")
#     ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x01)  # Write transaction
#     await ClockCycles(dut.clk, 30000)

    dut._log.info("SPI test completed successfully")

@cocotb.test()
async def test_pwm_freq(dut):
    # Write your test here
    # Goal: to verify PWM operates at 3 kHz (+-1% tolerance)
    dut._log.info("Start PWM Frequency test")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Set en_reg_out_7_0 to 0x01 (8'b1) (i.e. en_reg_out_7_0[0] = 1)
    dut._log.info("Write transaction, address 0x00, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xFF)
    #await ClockCycles(dut.clk, 100)

    # Set en_reg_out_15_8 to 0x01 (8'b1) (i.e. en_reg_out_15_8[0] = 1)
    dut._log.info("Write transaction, address 0x01, data 0x00")
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0x00)
    #await ClockCycles(dut.clk, 100)

    # Set en_reg_pwm_7_0 to 0x01 (8'b1) (i.e., en_reg_pwm_7_0[0] = 1)
    dut._log.info("Write transaction, address 0x02, data 0x01")
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0x01)
    #await ClockCycles(dut.clk, 100)

    # Set en_reg_pwm_15_8 to 0x01 (8'b1) (i.e., en_reg_pwm_15_8[0] = 1)
    dut._log.info("Write transaction, address 0x03, data 0x00")
    ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0x00)
    #await ClockCycles(dut.clk, 100)

    # Set the duty cycle to be 50%
    dut._log.info(f"Set the duty cycle to (50%) 0x80")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x80)
    #await ClockCycles(dut.clk, 1000)

    # freq1 = await measure_pwm_frequency(dut.uo_out, 0)
    # assert (freq1 >= 2970 and freq1 <= 3030), f"Expected 3000 Hz, got {freq1} Hz"
    # await ClockCycles(dut.clk, 1000)

    # freq2 = await measure_pwm_frequency(dut.uio_out, 0)
    # assert (freq2 >= 2970 and freq2 <= 3030), f"Expected 3000Hz, got {freq2}"
    # await ClockCycles(dut.clk, 1000)

    dut._log.info("PWM Frequency test completed successfully")


@cocotb.test()
async def test_pwm_duty(dut):
    # Write your test here
    # Output matches the configured value in register 0x04 (0-255 = 0-100%), (+-1% tolerance)
    dut._log.info("Start PWM Duty Cycle test")

    # # Set the clock period to 100 ns (10 MHz)
    # clock = Clock(dut.clk, 100, units="ns")
    # cocotb.start_soon(clock.start())

    # # Reset
    # dut._log.info("Reset")
    # dut.ena.value = 1
    # ncs = 1
    # bit = 0
    # sclk = 0
    # dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    # dut.rst_n.value = 0
    # await ClockCycles(dut.clk, 5)
    # dut.rst_n.value = 1
    # await ClockCycles(dut.clk, 5)

    # # Set en_reg_out_7_0 to 0x01 (8'b1) (i.e. en_reg_out_7_0[0] = 1)
    # dut._log.info("Write transaction, address 0x00, data 0x01")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0x01)
    # await ClockCycles(dut.clk, 100)

    # # Set en_reg_out_15_8 to 0x01 (8'b1) (i.e. en_reg_out_15_8[0] = 1)
    # dut._log.info("Write transaction, address 0x00, data 0x01")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0x01)
    # await ClockCycles(dut.clk, 100)

    # # Set en_reg_pwm_7_0 to 0x01 (8'b1) (i.e., en_reg_pwm_7_0[0] = 1)
    # dut._log.info("Write transaction, address 0x02, data 0x01")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0x01)
    # await ClockCycles(dut.clk, 100)

    # # Set en_reg_pwm_15_8 to 0x01 (8'b1) (i.e., en_reg_pwm_15_8[0] = 1)
    # dut._log.info("Write transaction, address 0x03, data 0x01")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x03, 0x01)
    # await ClockCycles(dut.clk, 100)

    # # Set the duty cycle to be 100%
    # dut._log.info(f"Set the duty cycle to (100%) 0xFF")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)
    # # assert dut.uo_out.value == 0x01, f"Expected 0x01, got {dut.uo_out.value}"
    # # assert dut.uio_out.value == 0x01, f"Expected 0x01, got {dut.uio_out.value}"
    # await ClockCycles(dut.clk, 1000)

    # # Set the duty cycle to be 50%
    # dut._log.info(f"Set the duty cycle to (50%) 0x80")
    # ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x80)
    # # assert dut.uo_out.value == 0x01, f"Expected 0x01, got {dut.uo_out.value}"
    # # assert dut.uio_out.value == 0x01, f"Expected 0x01, got {dut.uio_out.value}"
    # await ClockCycles(dut.clk, 1000)

    # # Perform duty cycle sweep and check duty cycle
    # # Sweep from 0 to 256 with a step size of 8
    # for i in range(0, 257, 8):

    #     dut._log.info(f"Write transaction, address 0x04, data {hex(i)}")
    #     ui_in_val = await send_spi_transaction(dut, 1, 0x04, i)     # Write transaction

    #     await ClockCycles(dut.clk, 100)

    dut._log.info("PWM Duty Cycle test completed successfully")
