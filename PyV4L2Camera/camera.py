import os

from ._v4l2 import ffi, lib


class Camera:
    def __init__(self, path: str):
        fd = lib.v4l2_open(path.encode(), os.O_RDWR)
        if -1 == fd:
            raise RuntimeError('Error opening device {}'.format(path))

        self._fd = fd
        self._fds = ffi.new('fd_set *')
        self._tv = ffi.new('struct timeval *')
        self._v4lconvert_data = lib.v4lconvert_create(fd)

        fmt = ffi.new('struct v4l2_format *')
        fmt.type = lib.V4L2_BUF_TYPE_VIDEO_CAPTURE

        if -1 == lib.xioctl(fd, lib.VIDIOC_G_FMT, fmt):
            raise RuntimeError('Getting format failed')

        dest_fmt = ffi.new('struct v4l2_format *')
        dest_fmt.type = fmt.type
        dest_fmt.fmt.pix.width = fmt.fmt.pix.width
        dest_fmt.fmt.pix.height = fmt.fmt.pix.height
        dest_fmt.fmt.pix.pixelformat = lib.V4L2_PIX_FMT_RGB24

        self.width = fmt.fmt.pix.width
        self.height = fmt.fmt.pix.height
        self._fmt = fmt
        self._dest_fmt = dest_fmt
        self._conv_dest_size = self.width * self.height * 3
        self._conv_dest = ffi.new('unsigned char[]',
                                  self._conv_dest_size)

        self._buf = ffi.new('struct v4l2_buffer *')
        self._bufptr = self._initialize_buffer()

        if -1 == lib.xioctl(fd, lib.VIDIOC_STREAMON,
                            ffi.new_handle(self._buf.type)):
            raise RuntimeError('Starting capture failed')

    def _initialize_buffer(self):
        buf = self._buf
        fd = self._fd

        req = ffi.new('struct v4l2_requestbuffers *')
        req.count = 1
        req.type = lib.V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = lib.V4L2_MEMORY_MMAP

        if -1 == lib.xioctl(fd, lib.VIDIOC_REQBUFS, req):
            raise RuntimeError('Requesting buffer failed')

        lib.memset(buf, 0, ffi.sizeof(buf))
        buf.type = lib.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = lib.V4L2_MEMORY_MMAP
        buf.index = 0

        if -1 == lib.xioctl(fd, lib.VIDIOC_QUERYBUF, buf):
            raise RuntimeError('Querying buffer failed')

        bufptr = lib.v4l2_mmap(ffi.NULL, buf.length,
                               lib.PROT_READ | lib.PROT_WRITE, lib.MAP_SHARED,
                               fd, buf.m.offset)

        if bufptr == ffi.cast('void *', -1):
            raise RuntimeError('MMAP failed: {}'.format(os.strerror(ffi.errno)))

        lib.memset(buf, 0, ffi.sizeof(buf))
        buf.type = lib.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = lib.V4L2_MEMORY_MMAP
        buf.index = 0

        if -1 == lib.xioctl(fd, lib.VIDIOC_QBUF, buf):
            raise RuntimeError('Exchanging buffer with device failed')

        return bufptr

    def get_frame(self):
        fd = self._fd
        buf = self._buf
        fds = self._fds
        tv = self._tv

        lib.FD_ZERO(fds)
        lib.FD_SET(fd, fds)

        tv.tv_sec = 2

        if -1 == lib.xselect(fd + 1, fds, ffi.NULL, ffi.NULL, tv):
            raise RuntimeError('Waiting for frame failed')

        lib.memset(buf, 0, ffi.sizeof(buf))
        buf.type = lib.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = lib.V4L2_MEMORY_MMAP

        if -1 == lib.xioctl(fd, lib.VIDIOC_DQBUF, buf):
            raise RuntimeError('Retrieving frame failed')

        if -1 == lib.v4lconvert_convert(self._v4lconvert_data,
                                        self._fmt, self._dest_fmt,
                                        self._bufptr, buf.bytesused,
                                        self._conv_dest,
                                        self._conv_dest_size):
            raise RuntimeError('Conversion failed')

        if -1 == lib.xioctl(fd, lib.VIDIOC_QBUF, buf):
            raise RuntimeError('Exchanging buffer with device failed')

        return bytes(self._conv_dest)

    def __del__(self):
        lib.xioctl(self._fd, lib.VIDIOC_STREAMOFF,
                   ffi.new_handle(lib.V4L2_BUF_TYPE_VIDEO_CAPTURE))
        lib.v4l2_munmap(self._bufptr, self._buf.length)
        lib.v4l2_close(self._fd)
