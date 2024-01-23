#include <qemu/char/virtio_serial_console.h>

#include <stdio.h>

struct virtio_features console_features[] = {
    //Feature bits 0 to 23 are for the specific device type (this case for console)
    { "VIRTIO_CONSOLE_F_SIZE", 1 << 0, true,
        "Configuration cols and rows are valid." },
    { "VIRTIO_CONSOLE_F_MULTIPORT", 1 << 1, false,
        "Device has support for multiple ports; max_nr_ports is valid and control virtqueues will be used." },
    { "VIRTIO_CONSOLE_F_EMERG_WRITE", 1 << 2, false,
        "Device has support for emergency write. Configuration field emerg_wr is valid." },
};

int virtio_serial_init(volatile virtio_serial_device* d)
{
    if (virtio_mmio_init(d->dev) != VIRT_OK) {
        printf("Error on mmio init, returning error\n");
        return -VIRT_ERROR;
    }
    printf("virtio_mmio_init successful\n");
    printf("Device Status after generic mmio init: %#010x\n", volatile_read32(STATUS(d->dev->regs)));

    // Read device feature bits, and write the subset of feature bits understood by
    // the OS and driver to the device. During this step the driver MAY read
    // (but MUST NOT write) the device-specific configuration fields to check that
    // it can support the device before accepting it.
    volatile_write32(DEVICEFEATURESSEL(d->dev->regs), 0); //Get Low value
    uint32_t dev_features = volatile_read32(DEVICEFEATURES(d->dev->regs));

    printf("Device Features: 0x%08x\n", dev_features);
    uint32_t request_features = VIRTIO_CONSOLE_F_MULTIPORT;
    // we need to make sure we allow writing to emerg_wr even on unconfigured device. We need to write low byte of emerg_wr to output or log method
    if (dev_features & VIRTIO_CONSOLE_F_EMERG_WRITE) {
        if (virtio_mmio_select_features(d->dev, VIRTIO_CONSOLE_F_EMERG_WRITE)
            != VIRT_OK) {
            printf("Could not select features\n");
            return -VIRT_ERROR;
        }
    }
    //Get bits 32-63 of Features
    volatile_write32(DEVICEFEATURESSEL(d->dev->regs), 1); //Get High value
    dev_features = volatile_read32(DEVICEFEATURES(d->dev->regs));

    // for sanity sake, check the rest of the device features, make sure we at least have them all documented as options
    virtio_check_features(&dev_features, &request_features, console_features, sizeof(console_features) / sizeof(console_features[0]));
    virtio_check_features(&dev_features, &request_features, universal_features, universal_features_sizeof / universal_features_first_sizeof);
    if (dev_features) {
        printf("Virtio supports undocumented options %#010x\n", dev_features);
    }
    printf("We are requesting features: %#010x for our driver to use\n", request_features);
    // then write the ones we are okay with back to the DRIVERFEATURES
    volatile_write32(DRIVERFEATURESSEL(d->dev->regs), 0);
    volatile_write32(DRIVERFEATURES(d->dev->regs), request_features);
    volatile_write32(DRIVERFEATURESSEL(d->dev->regs), 1);
    volatile_write32(DRIVERFEATURES(d->dev->regs), 0);

    // Set the FEATURES_OK status bit. The driver MUST NOT accept new feature bits after this step.
    uint32_t status = volatile_read32(STATUS(d->dev->regs));
    volatile_write32(STATUS(d->dev->regs), status | VIRTIO_STATUS_FEATURES_OK);
    printf("Device Status after writing VIRTIO_STATUS_FEATURES_OK: %#010x\n", volatile_read32(STATUS(d->dev->regs)));

    // Re-read device status to ensure the FEATURES_OK bit is still set: otherwise,
    // the device does not support our subset of features and the device is unusable.
    status = volatile_read32(STATUS(d->dev->regs));
    printf("Dev Status 0x%08x\n", status);
    if (!(status & VIRTIO_STATUS_FEATURES_OK)) {
        printf("Virtio doesn't support our feature set\n");
        return -VIRT_ERROR;
    }
    // Perform device-specific setup, including discovery of virtqueues for the device,
    // optional per-bus setup, reading and possibly writing the device’s virtio
    // configuration space, and population of virtqueues.

    printf("Setting up serial config\n");
    d->config = (struct virtio_console_config*)(CONFIG(d->dev->regs));
    d->config->cols = 0; //what should this be?
    d->config->rows = 0; //what should this be?
    d->config->max_nr_ports = 2;
    d->config->emerg_wr = 1;
    printf("Serial config setup successful\n");

    virtio_init_queue(d->_ctrl_rx_data, VIRTIO_SERIAL_QSZ, &d->ctrl_rx);
    virtio_init_queue(d->_ctrl_tx_data, VIRTIO_SERIAL_QSZ, &d->ctrl_tx);
    virtio_init_queue(d->_rx_data, VIRTIO_SERIAL_QSZ, &d->rx);
    virtio_init_queue(d->_tx_data, VIRTIO_SERIAL_QSZ, &d->tx);
    printf("virtio_init_queues successful\n");

    virtio_mmio_init_queue(d->dev, &d->ctrl_rx, 2, VIRTIO_SERIAL_QSZ);
    virtio_mmio_init_queue(d->dev, &d->ctrl_tx, 3, VIRTIO_SERIAL_QSZ);
    virtio_mmio_init_queue(d->dev, &d->rx, 4, VIRTIO_SERIAL_QSZ);
    virtio_mmio_init_queue(d->dev, &d->tx, 5, VIRTIO_SERIAL_QSZ);

    printf("virtio_mmio_init_queues successful\n");

    // Set the DRIVER_OK status bit. At this point the device is “live”.
    virtio_mmio_driver_ok(d->dev);
    printf("virtio_mmio_driver_ok successful\n");

    // Initialize receiveq(port0) and transmitq(port0)
    virtio_open_tx_port(d, 0);
    virtio_open_rx_port(d, 0);

    // Initialize receiveq(port1) and transmitq(port1)
    virtio_open_tx_port(d, 1);
    virtio_open_rx_port(d, 1);

    // Tell Device Driver is ready
    status = volatile_read32(STATUS(d->dev->regs));
    volatile_write32(STATUS(d->dev->regs), status | VIRTIO_STATUS_DRIVER_OK);

    printf("virtio_mmio_write in virtio_serial_init successful\n");

    return VIRT_OK;
}

int virtio_serial_write(volatile virtio_serial_device* d, void* buf, size_t len)
{
    printf("in virtio_serial_write, calling virtio_mmio_write\n");
    return virtio_mmio_write(d->dev, &d->tx, buf, len);
}

int virtio_serial_read(volatile virtio_serial_device* d, void* buf, size_t len)
{
    // printf("Reading From Virt Queue\n");
    return virtio_mmio_read_one(d->dev, &d->rx, buf, len);
}

int virtio_open_rx_port(volatile virtio_serial_device* d, uint32_t port_num)
{
    struct virtio_console_control ctrl_msg;
    ctrl_msg.id = port_num;
    ctrl_msg.event = VIRTIO_CONSOLE_PORT_OPEN;
    ctrl_msg.value = 1;
    return virtio_mmio_write(d->dev, &d->ctrl_rx, (uint8_t*)&ctrl_msg,
        sizeof(ctrl_msg));
}

int virtio_open_tx_port(volatile virtio_serial_device* d, uint32_t port_num)
{
    struct virtio_console_control ctrl_msg;
    ctrl_msg.id = port_num;
    ctrl_msg.event = VIRTIO_CONSOLE_PORT_OPEN;
    ctrl_msg.value = 1;
    return virtio_mmio_write(d->dev, &d->ctrl_tx, (uint8_t*)&ctrl_msg,
        sizeof(ctrl_msg));
}
