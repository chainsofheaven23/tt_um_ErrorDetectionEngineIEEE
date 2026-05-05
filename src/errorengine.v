module serial_error_engine (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,
    input  wire       load,       // Pulse high for 1 cycle to capture data_in
    output wire       serial_out, // The single bit output
    output reg        busy        // High while shifting
);

    reg [19:0] shift_reg;
    reg [4:0]  bit_cnt;
    
    // --- Internal Combinational Logic ---
    wire [11:0] h_bus;
    wire [7:0]  c_res;

    // Hamming (12,8) XOR Tree
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

    // CRC-8 XOR Tree (Inputting h_bus for 20-bit hybrid protection)
    assign c_res[0] = h_bus[11]^h_bus[10]^h_bus[8]^h_bus[4]^h_bus[3]^h_bus[0];
    assign c_res[1] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[1]^h_bus[0];
    assign c_res[2] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[2]^h_bus[1]^h_bus[0];
    assign c_res[3] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[3]^h_bus[2]^h_bus[1];
    assign c_res[4] = h_bus[11]^h_bus[8]^h_bus[7]^h_bus[4]^h_bus[3]^h_bus[2];
    assign c_res[5] = h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[3];
    assign c_res[6] = h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[4];
    assign c_res[7] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[5];

    // --- Control Logic ---
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= 20'b0;
            bit_cnt   <= 5'd0;
            busy      <= 1'b0;
        end else if (load && !busy) begin
            shift_reg <= {h_bus, c_res}; // Load the 20-bit hybrid codeword
            bit_cnt   <= 5'd20;
            busy      <= 1'b1;
        end else if (busy) begin
            if (bit_cnt > 5'd1) begin
                shift_reg <= {shift_reg[18:0], 1'b0};
                bit_cnt   <= bit_cnt - 5'd1;
            end else begin
                busy <= 1'b0;
            end
        end
    end

    assign serial_out = shift_reg[19];

endmodule
