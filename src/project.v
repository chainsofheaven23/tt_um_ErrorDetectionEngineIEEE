/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs: [7:0] data_in
    output wire [7:0] uo_out,   // Dedicated outputs: [0] serial_out, [1] busy
    input  wire [7:0] uio_in,   // IOs: [0] load signal
    output wire [7:0] uio_out,  // IOs: Output path (unused)
    output wire [7:0] uio_oe,   // IOs: Enable path (0=input, 1=output)
    input  wire       ena,      // always 1 when powered
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // --- Signal Mapping ---
    wire [7:0] data_in = ui_in;
    wire       load    = uio_in[0]; // Using first IO pin as load trigger
    
    // --- Internal Registers ---
    reg [19:0] shift_reg;
    reg [4:0]  bit_cnt;
    reg        busy_reg;

    // --- Combinational XOR Trees (Synthesizable) ---
    wire [11:0] h_bus;
    wire [7:0]  c_res;

    // Hamming (12,8)
    assign h_bus[0]  = data_in[0]^data_in[1]^data_in[3]^data_in[4]^data_in[6];
    assign h_bus[1]  = data_in[0]^data_in[2]^data_in[3]^data_in[5]^data_in[6];
    assign h_bus[2]  = data_in[0];
    assign h_bus[3]  = data_in[1]^data_in[2]^data_in[3]^data_in[7];
    assign h_bus[4]  = data_in[1];
    assign h_bus[5]  = data_in[2];
    assign h_bus[6]  = data_in[3];
    assign h_bus[7]  = data_in[4]^data_in[5]^data_in[6]^data_in[7];
    assign h_bus[8]  = data_in[4];
    assign h_bus[9]  = data_in[5];
    assign h_bus[10] = data_in[6];
    assign h_bus[11] = data_in[7];

    // CRC-8 (Polynomial 0x07)
    assign c_res[0] = h_bus[11]^h_bus[10]^h_bus[8]^h_bus[4]^h_bus[3]^h_bus[0];
    assign c_res[1] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[1]^h_bus[0];
    assign c_res[2] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[2]^h_bus[1]^h_bus[0];
    assign c_res[3] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[3]^h_bus[2]^h_bus[1];
    assign c_res[4] = h_bus[11]^h_bus[8]^h_bus[7]^h_bus[4]^h_bus[3]^h_bus[2];
    assign c_res[5] = h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[3];
    assign c_res[6] = h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[4];
    assign c_res[7] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[5];

    // --- Sequential Logic ---
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= 20'b0;
            bit_cnt   <= 5'd0;
            busy_reg  <= 1'b0;
        end else if (load && !busy_reg) begin
            shift_reg <= {h_bus, c_res}; // Load the 20-bit hybrid codeword
            bit_cnt   <= 5'd20;
            busy_reg  <= 1'b1;
        end else if (busy_reg) begin
            if (bit_cnt > 5'd1) begin
                shift_reg <= {shift_reg[18:0], 1'b0};
                bit_cnt   <= bit_cnt - 5'd1;
            end else begin
                busy_reg  <= 1'b0;
            end
        end
    end

    // --- TT Output Assignments ---
    assign uo_out[0] = shift_reg[19]; // Serial data out
    assign uo_out[1] = busy_reg;      // Busy status indicator
    assign uo_out[7:2] = 4'b0;        // Tie unused outputs to 0

    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;            // All bidirectional pins set to input (load)

    // Prevent warnings for unused input bits
    wire _unused = &{ena, ui_in, uio_in[7:1], 1'b0};

endmodule
