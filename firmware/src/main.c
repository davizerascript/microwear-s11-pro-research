#include "board_port.h"

/*
 * Minimal application entry point. This is source scaffolding only.
 * board_early_init() and board_service() must be implemented from the
 * verified JL701N/BR28 SDK and the actual S11 Pro board schematic/BSP.
 */
int main(void)
{
    if (board_early_init() != 0) {
        for (;;) {
            /* Safe stop; a board-specific watchdog policy is still unknown. */
        }
    }

    for (;;) {
        board_service();
    }
}
