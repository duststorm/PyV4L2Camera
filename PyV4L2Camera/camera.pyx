from v4l2 cimport *
from libc.errno cimport errno, EINTR
from libc.string cimport memset, strerror
from libc.stdlib cimport malloc, calloc
from posix.select cimport fd_set, timeval, FD_ZERO, FD_SET, select
from posix.fcntl cimport O_RDWR
from posix.mman cimport PROT_READ, PROT_WRITE, MAP_SHARED


cdef class Camera:
    cdef int fd
    cdef fd_set fds

    cdef v4l2_format fmt
    cdef v4l2_format dest_fmt

    cdef public unsigned int width
    cdef public unsigned int height
    cdef unsigned int conv_dest_size
    cdef unsigned char *conv_dest

    cdef v4l2_requestbuffers buf_req
    cdef v4l2_buffer buf
    cdef buffer_info *buffers

    cdef timeval tv
    cdef v4lconvert_data *convert_data

    def __cinit__(self, device_path):
        device_path = device_path.encode()

        self.fd = v4l2_open(device_path, O_RDWR)
        if -1 == self.fd:
            raise RuntimeError('Error opening device {}'.format(device_path))

        memset(&self.fmt, 0, sizeof(self.fmt))
        self.fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE

        if -1 == xioctl(self.fd, VIDIOC_G_FMT, &self.fmt):
            raise RuntimeError('Getting format failed')

        self.dest_fmt.type = self.fmt.type
        self.dest_fmt.fmt.pix.width = self.fmt.fmt.pix.width
        self.dest_fmt.fmt.pix.height = self.fmt.fmt.pix.height
        self.dest_fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_RGB24

        self.width = self.fmt.fmt.pix.width
        self.height = self.fmt.fmt.pix.height

        self.conv_dest_size = self.width * self.height * 3
        self.conv_dest = <unsigned char *>malloc(self.conv_dest_size)
        if self.conv_dest == NULL:
            raise RuntimeError('Allocating memory for converted data failed')
        self.convert_data = v4lconvert_create(self.fd)

        memset(&self.buf_req, 0, sizeof(self.buf_req))
        self.buf_req.count = 4
        self.buf_req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        self.buf_req.memory = V4L2_MEMORY_MMAP

        if -1 == xioctl(self.fd, VIDIOC_REQBUFS, &self.buf_req):
            raise RuntimeError('Requesting buffer failed')

        self.buffers = <buffer_info *>calloc(self.buf_req.count,
                                             sizeof(self.buffers[0]))
        if self.buffers == NULL:
            raise RuntimeError('Allocating memory for buffers array failed')
        self.initialize_buffers()

        if -1 == xioctl(self.fd, VIDIOC_STREAMON, &self.buf.type):
            raise RuntimeError('Starting capture failed')

    cdef inline int initialize_buffers(self) except -1:
        for buf_index in range(self.buf_req.count):
            memset(&self.buf, 0, sizeof(self.buf))
            self.buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            self.buf.memory = V4L2_MEMORY_MMAP
            self.buf.index = buf_index

            if -1 == xioctl(self.fd, VIDIOC_QUERYBUF, &self.buf):
                raise RuntimeError('Querying buffer failed')

            bufptr = v4l2_mmap(NULL, self.buf.length,
                               PROT_READ | PROT_WRITE,
                               MAP_SHARED, self.fd, self.buf.m.offset)

            if bufptr == <void *>-1:
                raise RuntimeError('MMAP failed: {}'.format(
                    strerror(errno).decode())
                )

            self.buffers[buf_index] = buffer_info(bufptr, self.buf.length)

            memset(&self.buf, 0, sizeof(self.buf))
            self.buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            self.buf.memory = V4L2_MEMORY_MMAP
            self.buf.index = buf_index

            if -1 == xioctl(self.fd, VIDIOC_QBUF, &self.buf):
                raise RuntimeError('Exchanging buffer with device failed')

        return 0

    cpdef bytes get_frame(self):
        FD_ZERO(&self.fds)
        FD_SET(self.fd, &self.fds)

        self.tv.tv_sec = 2

        r = select(self.fd + 1, &self.fds, NULL, NULL, &self.tv)
        while -1 == r and errno == EINTR:
            FD_ZERO(&self.fds)
            FD_SET(self.fd, &self.fds)

            self.tv.tv_sec = 2

            r = select(self.fd + 1, &self.fds, NULL, NULL, &self.tv)

        if -1 == r:
            raise RuntimeError('Waiting for frame failed')

        memset(&self.buf, 0, sizeof(self.buf))
        self.buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        self.buf.memory = V4L2_MEMORY_MMAP

        if -1 == xioctl(self.fd, VIDIOC_DQBUF, &self.buf):
            raise RuntimeError('Retrieving frame failed')

        if -1 == v4lconvert_convert(
                self.convert_data,
                &self.fmt, &self.dest_fmt,
                <unsigned char *>self.buffers[self.buf.index].start,
                self.buf.bytesused,
                self.conv_dest,
                self.conv_dest_size
        ):
            raise RuntimeError('Conversion failed')

        if -1 == xioctl(self.fd, VIDIOC_QBUF, &self.buf):
            raise RuntimeError('Exchanging buffer with device failed')

        return self.conv_dest[:self.conv_dest_size]

    def close(self):
        xioctl(self.fd, VIDIOC_STREAMOFF, &self.buf.type)

        for i in range(self.buf_req.count):
            v4l2_munmap(self.buffers[i].start, self.buffers[i].length)

        v4l2_close(self.fd)
