#include "interface.h"
#define printLine(...) ScrollDisplay();  sprintf(&charBuff[15], __VA_ARGS__); DrawDisplay();

//the waveform table
uint8_t awg_lut[AWG_NUM_CHAN][AWG_SAMPLES];

//how many bytes of the buffer we still need
uint16_t BULK_BUFF_RECV = 0;
//where to copy the incoming buffer
uint8_t *BULK_BUFF;

uint8_t temp_debug; //for debug
uint16_t temp_debug2; //for debug
extern char charBuff[16][20]; //for debug

const uint8_t ACK_STRING[ACK_STRING_LEN] = {'S', 'T', 'M', 'A', 'W', 'G', '2', '3'};
const uint8_t HS_STRING[HS_STRING_LEN] = {'I', 'N', 'I', 'T'};

void SendAck(){
	TRANS_Packet pack;
	pack.packet_type = 0;
	memcpy(pack.ack_string, ACK_STRING, ACK_STRING_LEN);
	if(	CDC_Transmit_FS(&pack, sizeof(TRANS_Packet)) ){
		//shouldn't happen if PC side always waits for ACK before next packet
		printLine("BUSY");
	}
}

void GotCDC_64B_Packet(char *ptr) {
	if (!BULK_BUFF_RECV) { // "new" packet
		RECV_Packet *packet = (RECV_Packet*) ptr;
		if (packet->packet_type == 0) {
			uint8_t *magic = &(packet->Content.HandShake.handshake_string);
			printLine("HS %02X%02X%02X%02X", magic[0], magic[1], //write debug to LCD
					magic[2], magic[3]);

			//check if hanshake_string matches some string
			int match = 1;
			for(int i = 0; i < HS_STRING_LEN; i++){
				if (magic[i] != HS_STRING[i]) match = 0;
			}
			if(match){
				//send ACK here?
				SendAck();
			}
		} else if (packet->packet_type == 1) {
			uint8_t chan = packet->Content.AWG_SET.channel;
			printLine("C %d %d %d %d", chan, //write debug to LCD
					packet->Content.AWG_SET.freq,
					packet->Content.AWG_SET.offset,
					packet->Content.AWG_SET.LUT_SIZE);

			//apply settings here

			//prepare for bulk transfer to awg lut
			BULK_BUFF_RECV = packet->Content.AWG_SET.LUT_SIZE;
			BULK_BUFF = &awg_lut[chan][0];

			//send ACK here?
			SendAck();

			temp_debug = chan; //for debug
			temp_debug2 = packet->Content.AWG_SET.LUT_SIZE; //for debug
		}
	} else { //bytes to buffer
		memcpy(BULK_BUFF, ptr, 64);
		BULK_BUFF += 64;
		BULK_BUFF_RECV -= 64;

		//for debug
		if (!BULK_BUFF_RECV) {
			uint16_t checksum;
			uint8_t *buff = awg_lut[temp_debug];
			for (int i = 0; i < temp_debug2; i++) {
				checksum = (checksum + *(buff++)) & 0xFF;
			}
			printLine("bulk %d", checksum);
		}
	}
}
