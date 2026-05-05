/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs: [7:0] data_in
    output wire [7:0] uo_out,   // Dedicated outputs: [0] serial, [1] busy
    input  wire [7:0] uio_in,   // IOs: [0] load
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path
    input  wire       ena,      // always 1
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n
);

    // --- Instantiate the Error Detection Engine ---
    serial_error_engine err_engine_inst (
        .clk        (clk),
        .rst_n      (rst_n),
        .data_in    (ui_in),        // Connect ui_in to data input
        .load       (uio_in[0]),    // Connect first IO to load signal
        .serial_out (uo_out[0]),    // Output bit on uo_out[0]
        .busy       (uo_out[1])     // Output busy status on uo_out[1]
    );

    // --- Tie off unused outputs ---
    assign uo_out[7:2] = 6'b0;      // Pins 2 through 7 are unused
    assign uio_out     = 8'b0;      // Bidirectional outputs not used
    assign uio_oe      = 8'b0;      // All bidirectional pins are inputs

    // Prevent warnings for unused input bits
    wire _unused = &{ena, ui_in, uio_in[7:1], 1'b0};

endmodule
