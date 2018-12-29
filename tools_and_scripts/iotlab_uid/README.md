# IoT-LAB node UID generator

This RIOT application can be used to generate the 16bit (4hex) unique
identifier for IoT-LAB node.

Thanks to RIOT portability, this same application can be used for all nodes
provided by IoT-LAB.

## Usage

1. Setup RIOT:

    $ make -C ../.. setup-riot

2. Build the application for your node:

    $ make BOARD=<board_type>

3. Copy the application to the `iot-lab.wiki` repository:

    $ cp bin/<board_type>/<board_type>-mdk_print_uids.elf ../../parts/iot-lab.wiki/firmwares/uids_firmwares/<board_type>_print_uids.elf

*Note:* Take care of the mapping between the board name in the RIOT build
    system and the name used by IoT-LAB (example: `samr21-xpro` in RIOT is
    `samr21` in IoT-LAB)
