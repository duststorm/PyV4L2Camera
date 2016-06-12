from libc.errno cimport errno, EINTR

cdef extern from 'linux/videodev2.h':
    ctypedef unsigned char           __u8
    ctypedef signed char             __s8
    ctypedef unsigned short          __u16
    ctypedef signed short            __s16
    ctypedef unsigned int            __u32
    ctypedef signed int              __s32
    ctypedef unsigned long long int  __u64
    ctypedef signed long long int    __s64
    
    enum: VIDIOC_G_FMT
    enum: VIDIOC_S_FMT
    enum: VIDIOC_REQBUFS
    enum: VIDIOC_QUERYBUF
    enum: VIDIOC_STREAMON
    enum: VIDIOC_STREAMOFF
    enum: VIDIOC_QBUF
    enum: VIDIOC_DQBUF
    enum: VIDIOC_QUERYMENU
    enum: VIDIOC_QUERYCTRL
    enum: V4L2_CID_BASE
    enum: V4L2_CID_LASTP1
    enum: V4L2_CID_PRIVATE_BASE
    enum: V4L2_CTRL_FLAG_DISABLED

    enum: V4L2_CTRL_FLAG_DISABLED
    enum: V4L2_CTRL_FLAG_GRABBED
    enum: V4L2_CTRL_FLAG_READ_ONLY
    enum: V4L2_CTRL_FLAG_UPDATE
    enum: V4L2_CTRL_FLAG_INACTIVE
    enum: V4L2_CTRL_FLAG_WRITE_ONLY

    cdef struct v4l2_pix_format:
        __u32   width
        __u32   height
        __u32   pixelformat
        __u32   field
        __u32   bytesperline
        __u32   sizeimage
        __u32   colorspace
        __u32   priv
        __u32   flags
        __u32   ycbcr_enc
        __u32   quantization
        __u32   xfer_func

    cdef union __v4l2_format_fmt:
        v4l2_pix_format        pix
        __u8                   raw_data[200]

    cdef struct v4l2_format:
        __u32 type
        __v4l2_format_fmt fmt
            

    cdef struct v4l2_requestbuffers:
        __u32 count
        __u32 type
        __u32 memory

    cdef union __v4l2_buffer_m:
        __u32          offset
        unsigned long  userptr
        __s32          fd

    cdef struct v4l2_buffer:
        __u32 index
        __u32 type
        __u32 memory
        __u32 length
        __u32 bytesused

        __v4l2_buffer_m m

    cdef enum v4l2_ctrl_type:
        V4L2_CTRL_TYPE_INTEGER
        V4L2_CTRL_TYPE_BOOLEAN
        V4L2_CTRL_TYPE_MENU
        V4L2_CTRL_TYPE_BUTTON
        V4L2_CTRL_TYPE_INTEGER64
        V4L2_CTRL_TYPE_STRING
        V4L2_CTRL_TYPE_CTRL_CLASS

    cdef struct v4l2_queryctrl:
        __u32             id
        v4l2_ctrl_type    type
        __u8	          name[32]
        __s32	          minimum
        __s32	          maximum
        __s32	          step
        __s32	          default_value
        __u32	          flags
        __u32	          reserved[2]

    cdef struct v4l2_querymenu:
        __u32	id
        __u32	index
        __u8	name[32]
        __u32	reserved

cdef extern from 'libv4l2.h':
    enum: V4L2_PIX_FMT_RGB24
    enum: V4L2_BUF_TYPE_VIDEO_CAPTURE
    enum: V4L2_MEMORY_MMAP

    cdef struct v4lconvert_data:
        pass

    int v4l2_open(const char *device_name, int flags)
    int v4l2_close(int fd)

    int v4l2_ioctl(int fd, int request, void *argp)

    void *v4l2_mmap(void *start, size_t length, int prot, int flags, int fd,
                    __s64 offset)
    int v4l2_munmap(void *_start, size_t length)

cdef extern from 'libv4lconvert.h':
    v4lconvert_data *v4lconvert_create(int fd)
    int v4lconvert_convert(v4lconvert_data *data,
                           const v4l2_format *src_fmt,
                           const v4l2_format *dest_fmt,
                           unsigned char *src, int src_size,
                           unsigned char *dest, int dest_size)

cdef inline int xioctl(int fd, unsigned long int request, void *arg):
    cdef int r = v4l2_ioctl(fd, request, arg)
    while -1 == r and EINTR == errno:
        r = v4l2_ioctl(fd, request, arg)

    return r

cdef struct buffer_info:
    void *start
    size_t length
