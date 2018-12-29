/*
 * Copyright (C) 2018 Inria
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

#include <stdint.h>
#include <stdio.h>

#include "xtimer.h"

#include "periph/cpuid.h"

static uint8_t id[CPUID_LEN];

static inline uint16_t iotlab_uid(void) {
#if defined(BOARD_B_L072Z_LRWAN1)
    return ((uint16_t)(id[CPUID_LEN - 4] << 8)) | id[CPUID_LEN - 2];
#elif defined(BOARD_B_L475E_IOT01A)
    return ((uint16_t)(id[0] << 8)) | id[2];
#elif defined(BOARD_FRDM_KW41Z)
    return ((uint16_t)(id[0] << 8)) | id[4];
#else
	return (id[CPUID_LEN - 4] | (id[CPUID_LEN - 2] << 7)) << 8 | id[CPUID_LEN - 3];
#endif
}

int main(void)
{
    /* read the CPUID */
    cpuid_get(id);

    while (1) {
        puts("-----------------------------------");
        /* print the cpu id */
        printf("cpuid: ");
        for (size_t i = 0; i < CPUID_LEN; ++i) {
            printf("%02X", id[i]);
        }
        puts("");

        /* print the computed iotlab uid */
        printf("iotlab_uid: %04X\n", iotlab_uid());
        puts("-----------------------------------\n\n");
        xtimer_sleep(1);
    }

    return 0;
}
