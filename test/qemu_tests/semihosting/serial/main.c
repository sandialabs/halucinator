#include <qemu/char/virtio.h>
#include <qemu/char/virtio_serial_console.h>
#include <stdio.h>
#include <unistd.h>

static struct virtio_serial_device serial_dev __a4k;

int virtio_init(uint32_t base_addr)
{
    volatile virtio_device* dev = (virtio_device*)(base_addr);
    printf("MAGIC VALUE: 0x%08x\n", volatile_read32(MAGICVALUE(dev->regs)));
    if (volatile_read32(MAGICVALUE(dev->regs)) != VIRTIO_MAGIC) {
        printf("Magic error %x\n", volatile_read32(MAGICVALUE(dev->regs)));
        return VIRT_ERROR;
    }
    uint32_t version = volatile_read32(VERSION(dev->regs));
    printf("VERISON 0x%08x\n", version);
    if (version != 0x2) { //virtio version 1.0 (I think it should work on 1.1 too)
        printf("Unknown Version! Cannot initialize Virt IO device\n");
        printf("error: virtio at 0x%x did not have compatible version. "
               "Got 0x%x\n",
            dev, version);
        return -VIRT_ERROR;
    }
    // print_v1_info(dev);

    switch (volatile_read32(DEVICEID(dev->regs))) {
    case VIRTIO_SERIAL_DEV:
        serial_dev.dev = dev;
        printf("base of serial: %08x\n", base_addr);
        return virtio_serial_init(&serial_dev);
    case VIRTIO_NET_DEV:
        printf("Net based virtio device ID 0x%x not implemented yet\n", volatile_read32(DEVICEID(dev->regs)));
        return -VIRT_ERROR;
    default:
        printf("unsupported virtio device ID 0x%x\n", volatile_read32(DEVICEID(dev->regs)));
    }
    return -VIRT_ERROR;
}

int write_to_serial(void* buf, size_t size)
{
    size_t bytes_to_write = size;
    size_t chunk = 0;
    size_t written = 0;
    uint8_t* p = (uint8_t*)buf;

    while (bytes_to_write) {
        chunk = (bytes_to_write > (PG_SIZE)) ? PG_SIZE : bytes_to_write;

        written += virtio_serial_write(&serial_dev, p, chunk);

        bytes_to_write -= chunk;
        p += chunk;
    }

    if (written == size)
        return VIRT_OK;
    else {
        printf("Wanted to write %zu but only %zu bytes was written\n",
            size, written);
        return -VIRT_ERROR;
    }
}

size_t read_from_serial(char* buf, size_t size)
{
    printf("read_from_serial\n");
    size_t bytes_to_read = size;
    size_t chunk = 0;
    size_t read_bytes = 0;
    uint8_t* p = (uint8_t*)buf;

    while (bytes_to_read) {
        chunk = (bytes_to_read > PG_SIZE) ? PG_SIZE : bytes_to_read;

        read_bytes += virtio_serial_read(&serial_dev, p, chunk);
        printf("\nFILE: %s, Function: %s, LINE %d, \nReceive Buffer: %s\n",
            __FILE__, __PRETTY_FUNCTION__, __LINE__, buf);
        bytes_to_read -= chunk; //read_bytes; //chunk;
        p += chunk;
    }

    if (read_bytes == size)
        return VIRT_OK;
    else {
        printf("Wanted to read %d but got %d bytes\n", size, read_bytes);
        return VIRT_ERROR;
    }
}

#define NUM_BYTES_TO_READ 20
int main()
{
    size_t num_read;
    size_t size;
    char buf[NUM_BYTES_TO_READ];

    // if (virtio_init(0xFFFF0000)) { //net device
    //     printf("Error initializing net device\n");
    // }
    if (virtio_init(0xFFFF2000)) { //serial device
        printf("Error initializing serial device, not sending message\n");
        return -1;
    }
    //now try writing to the device
    char test_message[] = "Testing serial\n";
    write_to_serial(test_message, sizeof(test_message));
    printf("Sent message to serial\n");

    //now try reading from device
    size = NUM_BYTES_TO_READ;

    // write to the file quick before reading again
    // FILE *pFile;
    // char write_buffer[] = "123456789abcde\n";
    // pFile=fopen("/tmp/ty0", "a");
    // fprintf(pFile, "%s", write_buffer);
    // fclose(pFile);

    printf("\nReading from virtio Serial\n");
    if (read_from_serial(buf, size) == VIRT_ERROR) {
        printf("Did not read from serial correctly\n");
        fflush(stdout);
        fflush(stderr);
    }

    printf("\nReading from virtio Serial 2\n");
    if (read_from_serial(buf, size) == VIRT_ERROR) {
        printf("Did not read from serial correctly\n");
        fflush(stdout);
        fflush(stderr);
        return -1;
    }
    printf("\nExiting Correctly\n");
    fflush(stdout);
    fflush(stderr);
    return 0;
}

// void exit(int __status){
//     while(1);
// }
