/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
module tt_um_unified_error_detection (
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
        .clk        (clk),      // You can still pass them in case you 
        .rst_n      (rst_n),    // decide to add registers later.
        .data_in    (ui_in),
        .select     (uio_in[1:0]), // Using IO pins for the mux select
        .serial_out (uo_out)       // The 8-bit muxed result
    );

    // Tie off unused TT signals
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0; // All uio pins are inputs

    // Prevent "Unused Input" warnings during synthesis
    wire _unused = &{ena, clk, rst_n, uio_in[7:2], 1'b0};

endmodule
