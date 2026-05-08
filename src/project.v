/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_unified_error_detection (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // TEMPORARY DEBUG CONNECTION
    // Directly connect input to output
    assign uo_out = ui_in;

    // Unused bidirectional pins
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Prevent unused warnings
    wire _unused = &{ena, clk, rst_n, uio_in, 1'b0};

endmodule

`default_nettype wire
