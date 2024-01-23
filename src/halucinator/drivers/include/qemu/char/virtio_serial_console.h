#ifndef _VIRTIO_CONSOLE_H
#define _VIRTIO_CONSOLE_H

#include "virtio.h"
#include "virtio_queue.h"
#include <stddef.h>
#include <stdint.h>
/*5.3 Console Device
The virtio console device is a simple device for data input and output.
A device MAY have one or more ports. Each port has a pair of input and
output virtqueues. Moreover, a device has a pair of control IO virtqueues.
The control virtqueues are used to communicate information between the
device and the driver about ports being opened and closed on either side
of the connection, indication from the device about whether a particular
port is a console port, adding new ports, port hot-plug/unplug, etc.,
and indication from the driver about whether a port or a device was
successfully added, port open/close, etc. For data IO, one or more empty
buffers are placed in the receive queue for incoming data and outgoing
characters are placed in the transmit queue.*/

/*5.3.1 Device ID
3/*

/*5.3.2 Virtqueues
0
receiveq(port0)
1
transmitq(port0)
2
control receiveq
3
control transmitq
4
receiveq(port1)
5
transmitq(port1)
…
The port 0 receive and transmit queues always exist: other queues only exist if VIRTIO_CONSOLE_F_MULTIPORT is set.*/

#define VIRTIO_SERIAL_QSZ 1024

#define VIRTIO_CONSOLE_DEVICE_READY (0)
/*Sent by the driver at initialization to
        indicate that it is ready to receive control
        messages. A value of 1 indicates success,
        and 0 indicates failure. The port number id is unused.*/
#define VIRTIO_CONSOLE_DEVICE_ADD (1)
/*Sent by the device, to create a new port.
        value is unused.*/
#define VIRTIO_CONSOLE_DEVICE_REMOVE (2)
/*Sent by the device, to remove an existing port.
        value is unused.*/
#define VIRTIO_CONSOLE_PORT_READY (3)
/*Sent by the driver in response to the device’s
        VIRTIO_CONSOLE_PORT_ADD message, to indicate that
        the port is ready to be used. A value of 1 indicates
        success, and 0 indicates failure.*/
#define VIRTIO_CONSOLE_CONSOLE_PORT (4)
/*Sent by the device to nominate a port as a console port.
        There MAY be more than one console port.*/
#define VIRTIO_CONSOLE_RESIZE (5)
/*Sent by the device to indicate a console size change.
        value is unused. The buffer is followed by the number
        of columns and rows:*/
#define VIRTIO_CONSOLE_PORT_OPEN (6)
/*This message is sent by both the device and the driver.
        value indicates the state: 0 (port closed) or 1 (port open).
        This allows for ports to be used directly by guest and host
        processes to communicate in an application-defined manner.*/
#define VIRTIO_CONSOLE_PORT_NAME (7)
/*Sent by the device to give a tag to the port.
        This control command is immediately followed by the UTF-8
        name of the port for identification within the guest
        (without a NUL terminator).*/

#define VIRTIO_CONSOLE_F_SIZE (1 << 0)
/*Configuration cols and rows are valid.*/
#define VIRTIO_CONSOLE_F_MULTIPORT (1 << 1)
/*Device has support for multiple ports; max_nr_ports is
        valid and control virtqueues will be used.*/
#define VIRTIO_CONSOLE_F_EMERG_WRITE (1 << 2)
/*Device has support for emergency write.
        Configuration field emerg_wr is valid.*/

struct virtio_console_resize {
    uint16_t cols;
    uint16_t rows;
};

struct virtio_console_config {
    uint16_t cols;
    uint16_t rows;
    uint32_t max_nr_ports;
    uint32_t emerg_wr;
};

struct virtio_console_control {
    uint32_t id; /* Port number */
    uint16_t event; /* The kind of control event */
    uint16_t value; /* Extra information for the event */
};

typedef struct virtio_serial_device {
    __a4k uint8_t _rx_data[VIRTIO_QUEUE_SZ_WITH_PADDING(VIRTIO_SERIAL_QSZ + 1)];
    __a4k uint8_t _tx_data[VIRTIO_QUEUE_SZ_WITH_PADDING(VIRTIO_SERIAL_QSZ + 1)];
    __a4k uint8_t _ctrl_rx_data[VIRTIO_QUEUE_SZ_WITH_PADDING(VIRTIO_SERIAL_QSZ + 1)];
    __a4k uint8_t _ctrl_tx_data[VIRTIO_QUEUE_SZ_WITH_PADDING(VIRTIO_SERIAL_QSZ + 1)];
    volatile virtio_device* dev;
    struct virtio_console_config* config;
    struct virtq rx;
    struct virtq tx;
    struct virtq ctrl_rx;
    struct virtq ctrl_tx;
} virtio_serial_device;

int virtio_serial_init(volatile virtio_serial_device* d);
int virtio_serial_write(volatile virtio_serial_device* d, void* buf,
    size_t len);
int virtio_serial_read(volatile virtio_serial_device* d, void* buf,
    size_t len);
int virtio_open_rx_port(volatile virtio_serial_device* d, uint32_t port_num);
int virtio_open_tx_port(volatile virtio_serial_device* d, uint32_t port_num);
/*5.3.6.2.1 Device Requirements: Multiport Device Operation
The device MUST NOT specify a port which exists in a
VIRTIO_CONSOLE_DEVICE_ADD message, nor a port which is equal or greater than max_nr_ports.
The device MUST NOT specify a port in VIRTIO_CONSOLE_DEVICE_REMOVE
which has not been created with a previous VIRTIO_CONSOLE_DEVICE_ADD.*/

/*5.3.6.2.2 Driver Requirements: Multiport Device Operation
The driver MUST send a VIRTIO_CONSOLE_DEVICE_READY message if VIRTIO_CONSOLE_F_MULTIPORT is negotiated.
Upon receipt of a VIRTIO_CONSOLE_CONSOLE_PORT message, the driver SHOULD treat the port
in a manner suitable for text console access and MUST respond with a VIRTIO_CONSOLE_PORT_OPEN
message, which MUST have value set to 1.*/

/*5.3.6.3 Legacy Interface: Device Operation
When using the legacy interface, transitional devices and drivers MUST format the fields in
struct virtio_console_control according to the native endian of the guest rather than
(necessarily when not using the legacy interface) little-endian.
When using the legacy interface, the driver SHOULD ignore the len value in used ring entries for the transmit queues and the control transmitq. Note: Historically, some devices put the
total descriptor length there, even though no data was actually written.*/

/*5.3.6.4 Legacy Interface: Framing Requirements
When using legacy interfaces, transitional drivers which have not negotiated
VIRTIO_F_ANY_LAYOUT MUST use only a single descriptor for all buffers in the
control receiveq and control transmitq.*/

#endif /* _VIRTIO_CONSOLE_H */