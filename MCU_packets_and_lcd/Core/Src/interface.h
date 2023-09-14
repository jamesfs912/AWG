#include <stdint.h>
#ifndef SRC_INTERFACE_H_
#define SRC_INTERFACE_H_

#define AWG_SAMPLES (1024*4)
#define AWG_NUM_CHAN 2
#define MAGIC_NUM 0x42
#define HS_STRING_LEN 4
#define ACK_STRING_LEN 8

#define PACK __attribute__((packed))

extern uint8_t awg_lut[AWG_NUM_CHAN][AWG_SAMPLES];

typedef struct {
	uint8_t packet_type;
	union {
		struct { //packet_type = 0
			uint8_t handshake_string[HS_STRING_LEN];
		} PACK HandShake;
		struct { //packet_type = 1
			uint8_t channel;
			uint8_t freq;
			uint8_t offset;
			//... etc
			uint16_t LUT_SIZE;
		} PACK AWG_SET;
	} PACK Content;
} PACK RECV_Packet;

typedef struct PACK {
	uint8_t packet_type;
	uint8_t ack_string[ACK_STRING_LEN];
} TRANS_Packet;

void Got64BCDC(char *ptr);

#endif /* SRC_INTERFACE_H_ */
