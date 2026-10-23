#ifndef S11PRO_BOARD_PORT_H
#define S11PRO_BOARD_PORT_H

/*
 * Board abstraction boundary for a future Microwear S11 Pro port.
 * Intentionally declarations only: pin mapping and controllers are unverified.
 */

int board_early_init(void);
void board_service(void);

#endif
