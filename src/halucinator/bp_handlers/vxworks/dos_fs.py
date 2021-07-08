# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC 
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, 
# the U.S. Government retains certain rights in this software.

'''bp_handlers for the dos filesystem'''
import logging
import types

from halucinator.bp_handlers.vxworks.ios_dev import IosDev
from halucinator.peripheral_models.dos_fs_model import DosFsModel
from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler

log = logging.getLogger(__name__)


class DosFsLib(BPHandler):
    '''
        This implements the DOS FS intercepts
        Usage:
           - class: halucinator.bp_handlers.vxworks.dos_fs.DosFsLib
             class_args: (optional) {dd_dirent_offset: Offset to dir entry in structure)
             function: 
             symbol: <BOARD_SPECIFIC> or
             addr:
    '''
    def __init__(self, impl=DosFsModel,dd_dirent_offset=8):
        self.model = impl
        self.dd_dirent_offset = dd_dirent_offset

    def fio_move(self, qemu, bp_addr, fd, arg):
        '''
            Move file
        '''
        new_path= qemu.read_string(arg)
        self.model.fio_move(fd, new_path)
        return True, 0

    def fio_time_set(self, qemu, bp_addr, fd, time_struct):
        '''
            Sets time on file
        '''
        # TODO: Parameterize
        # **BINARY DEPENDANT**
        # time_struct = actime
        # time_struct + 4 = modtime
        
        log.debug("fio_time_set")
        atime = int.from_bytes(qemu.read_memory(time_struct , 1, 4,raw=True) , "little")
        modtime = int.from_bytes(qemu.read_memory(time_struct + 4, 1, 4, raw=True) , "little")
        self.model.fio_time_set(fd,atime, modtime)
        return True, 0

    def fio_attrib_set(self, qemu, bp_addr,fd,st_attrib):
        '''
            0x01   read-only
            0x02   hidden  
            0x04   system file 
            0x08   volume label  
            0x10   sub-directory 
            0x20   archive file
        '''


    def fio_rename(self, qemu, bp_addr, fd, p_new_name):
        '''
            Rename file
        '''
        log.debug("fio_rename")
        new_name = qemu.read_string(arg)
        self.model.fio_rename(fd,new_name)
        return True,0

    def fio_read(self, qemu, bp_addr, fd, d_size):
        '''
            Read d_size bytes from file
        '''
        log.debug("FIOREAD")
        rem = self.model.fio_read(fd)
        qemu.write_memory(d_size, 4,rem)
        return True, 0

    def fio_read_dir(self, qemu, bp_addr, fd, p_dir):
        '''
            Read files in directory
        '''
        log.debug("FIOREADDIR")
        dd_dirent_offset = 8
        dd_dirent = p_dir + self.dd_dirent_offset

        # redir is initiated on fd
        if fd in self.model.readdir.keys():
            # check to see if we need to return null
            ret_val = self.model.fio_read_dir(fd, False)
            if ret_val is not None:
                #write to arg in memory
                for i, r_val in enumerate(ret_val):
                    qemu.write_memory(dd_dirent + i, 1, r_val)
                # Delimit
                qemu.write_memory(dd_dirent + i+1, 1, 0x00)
                return True, 0
        # first time
        else:
            ret_val = self.model.fio_read_dir(fd, True)
            if ret_val:
                #write to arg in memory
                for i, r_val in enumerate(ret_val):
                    qemu.write_memory(dd_dirent + i, 1, r_val)
                return True, 0

        return True, None

    def fio_where(self, qemu, bp_addr, fd, arg):
        '''
            fio_where
        '''
        log.debug("FIOWHERE")
        return True, self.model.fio_where(fd)

    def fio_seek (self, qemu, bp_addr, fd, arg):
        '''
            fio_seek
        '''
        log.debug('FIOSEEK')
        self.model.fio_seek(fd, arg)
        return True, 0

    def fio_fstat_get(self, qemu, bp_addr, fd, p_stat):
        '''
            fstat_get
        '''
        # TODO: make not binary dependent by parameterizing
        #     **BINARY DEPENDANT**
        #     (int *pFd,int *p_stat)
        #     p_stat + 0x0 = st_dev
        #     p_stat + 0xa = st_nlink
        #     p_stat + 0x14 = st_size
        #     p_stat + 0x24 = st_blksize
        #     p_stat + 0x28 = st_blocks
        #     p_stat + 0x2c = st_attrib
        #     p_stat + 0x8 = st_mode
        #     #Missing file date info
        #     p_stat + 0x18 = st_atime
        #     p_stat + 0x1c = st_mtime

        log.debug('FIOFSTATGET: %s' % self.model.get_filename(fd))

        stat= self.model.fio_fstat_get(fd)

        qemu.write_memory(p_stat + 0x0, self.model.st_dev, stat["st_dev"])
        qemu.write_memory(p_stat + 0x8, self.model.st_mode, stat["st_mode"])
        qemu.write_memory(p_stat + 0xa, self.model.st_nlink, stat["st_nlink"])
        qemu.write_memory(p_stat + 0x14, self.model.st_size, stat["st_size"])
        qemu.write_memory(p_stat + 0x18, self.model.st_atime_32, stat["st_atime"])
        qemu.write_memory(p_stat + 0x1c, self.model.st_mtime_32, stat["st_mtime"])
        qemu.write_memory(p_stat + 0x24, self.model.st_blksize, stat["st_blksize"])
        qemu.write_memory(p_stat + 0x28, self.model.st_blocks, stat["st_blocks"])
        qemu.write_memory(p_stat + 0x2c, self.model.st_blocks, stat["st_attrib"])

        return True, 0

    @bp_handler(['delete'])
    def delete(self, qemu, bp_addr):
        '''
            delete break point handler
        '''
        log.debug("#######################")
        log.debug("delete")
        log.debug("#######################")
        drv = qemu.get_arg(0)
        path = qemu.read_string(qemu.get_arg(1))
        drive = IosDev.get_driver(drv)
        return True,self.model.delete(drv, path, drive)

    @bp_handler(['create'])
    def create(self, qemu, bp_addr):
        '''
            create break point handler
        '''
        log.debug("#######################")
        log.debug("create ")
        log.debug("#######################")
        drv = qemu.get_arg(0)
        drive = IosDev.get_driver(drv)
        name = qemu.read_string(qemu.get_arg(1))
        name = drive + name
        flags = qemu.get_arg(2) | 600
        mode = 0x8000
        return self.model.creat_or_open(name, flags, mode)

    @bp_handler(['open'])
    def open(self, qemu, bp_addr):
        '''
            open break point handler
        '''
        # PARAMETERS:
        # pointer to volume descriptor */
        #     char *	pPath,	/* dosFs full path/filename */
        #     int		flags,	/* file open flags */
        #     int		mode	/* file open permissions (mode) */

        #     0x0000 Read only
        #     0x0001 Write only
        #     0x0002 Read/Write
        #     0x0200 Create
        
        log.debug("#######################")
        log.debug("open ")
        log.debug("#######################")
        drv = qemu.get_arg(0)
        drive = IosDev.get_driver(drv)
        name = qemu.read_string(qemu.get_arg(1))
        name = drive + name
        flags = qemu.get_arg(2)
        mode = qemu.get_arg(3)
        return self.model.creat_or_open(name,flags,mode)

    @bp_handler(['close'])
    def close(self, qemu, bp_addr):
        '''
            close break point handler
        '''
        fd = qemu.get_arg(0)
        log.debug("#######################")
        log.debug(" close")
        log.debug("#######################")
        log.debug("\tFD: %d" % fd)
        try:
            log.debug("CLOSING FILE: %s" % self.model.fd_table[fd])
            self.model.close( fd )
            return True, 0
        except OSError as err:
            print(err)
            log.debug("EXCEPTION CAUGHT RETURNING ERROR")
            return True,  0xffffffff

    @bp_handler(['read'])
    def read(self, qemu, bp_addr):
        '''
            read break point handler
        '''
        log.debug("#######################")
        log.debug("read ")
        log.debug("#######################")
        log.debug("\tFD: %d" % qemu.get_arg(0))
        fd = qemu.get_arg(0)
        buf_ptr = qemu.get_arg(1)
        size = qemu.get_arg(2)
        data = self.model.read(fd, size)
        log.debug(data[:256])
        if len(data):
            for i, dat in enumerate(data):
                qemu.write_memory(buf_ptr + i, 1, dat)
        return True, len(data)

    @bp_handler(['write'])
    def write(self, qemu, bp_addr):
        '''
            write break point handler
        '''
        log.debug("#######################")
        log.debug("write ")
        log.debug("#######################")
        fd = qemu.get_arg(0)
        buf_ptr = qemu.get_arg(1)
        size = qemu.get_arg(2)
        buf = qemu.read_memory(buf_ptr, 1, size, raw=True)
        self.model.write(fd, buf)
        return True, len(buf)

    @bp_handler(['ioctl'])
    def ioctl(self, qemu, bp_addr):
        '''
            ioctl bp_handler
        '''
        log.debug("#######################")
        log.debug("ioctl")
        log.debug("#######################")
        fd = qemu.get_arg(0)
        func = qemu.get_arg(1)
        arg = qemu.get_arg(2)

        if func in self.switcher.keys():
            if isinstance(self.switcher[func], types.FunctionType):
                #return True,self.switcher[func](self,qemu, bp_addr)
                return self.switcher[func](self,qemu, bp_addr,fd,arg)
            log.debug("Unimplemented Fucntion: %s"%self.switcher[func])
            log.debug(qemu.read_memory(arg, 1, 4))
            return False, None
        log.debug("Undefined Function %s", func)
        input("Press Enter to continue")
        return True, 0

    switcher = {
        1:fio_read,
        2:"FIOFLUSH",
        5:"FIODISKFORMAT",
        6:"FIODISKINIT",
        7:fio_seek,
        8: fio_where,
        10 : "fio_rename",
        11:"FIODISKCHANGE",
        18:"FIOGETNAME",
        21:"FIOSYNC",
        30:"FIONFREE",
        31:"FIOMKDIR" ,
        32:"FIORMDIR" ,
        33:"FIOLABELGET" ,
        34:"FIOLABELSET",
        35: "fio_attrib_set" ,
        36:"FIOCONTIG" ,
        38:fio_fstat_get,
        37:fio_read_dir ,
        39:"FIOUNMOUNT" ,
        41:"FIONCONTIG",
        42:"FIOTRUNC" ,
        44: fio_time_set,
        47:"fio_move" ,
        49:"FIOCONTIG64" ,
        50:"FIONCONTIG64",
        51:"FIONFREE64",
        52:"FIONREAD64" ,
        53:"FIOSEEK64" ,
        54:"FIOWHERE64" ,
        55: "FIOTRUNC64" ,
        }
