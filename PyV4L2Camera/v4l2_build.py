from cffi import FFI

ffi = FFI()

ffi.cdef('''
    #define VIDIOC_G_FMT ...
    #define VIDIOC_S_FMT ...
    #define VIDIOC_REQBUFS ...
    #define VIDIOC_QUERYBUF ...
    #define VIDIOC_STREAMON ...
    #define VIDIOC_STREAMOFF ...
    #define VIDIOC_QBUF ...
    #define VIDIOC_DQBUF ...

    #define V4L2_PIX_FMT_RGB24 ...
    #define V4L2_BUF_TYPE_VIDEO_CAPTURE ...
    #define V4L2_MEMORY_MMAP ...

    #define PROT_READ ...
    #define PROT_WRITE ...
    #define MAP_SHARED ...

    void *memset (void *buffer, int c, size_t num);

    int v4l2_open (const char *file, int oflag, ...);
    int v4l2_close(int fd);
    int v4l2_ioctl(int fd, unsigned long int request, ...);
    static int xioctl(int fd, unsigned long int request, void *arg);
    void *v4l2_mmap(void *start, size_t length, int prot, int flags,
                    int fd, int64_t offset);
    int v4l2_munmap(void *_start, size_t length);

    typedef struct {
        ...;
    } fd_set;

    void FD_ZERO(fd_set *set);
    void FD_SET(int fd, fd_set *set);
    static int xselect(int nfds, fd_set *readfds, fd_set *writefds,
                       fd_set *exceptfds, struct timeval *timeout);

    struct v4l2_pix_format {
        uint32_t   width;
        uint32_t   height;
        uint32_t   pixelformat;
        uint32_t   field;
        uint32_t   bytesperline;
        uint32_t   sizeimage;
        uint32_t   colorspace;
        uint32_t   priv;
        uint32_t   flags;
        uint32_t   ycbcr_enc;
        uint32_t   quantization;
        uint32_t   xfer_func;
    };

    struct v4l2_format {
        uint32_t type;

        union {
            struct v4l2_pix_format        pix;
            struct v4l2_pix_format_mplane *pix_mp;
            struct v4l2_window            *win;
            struct v4l2_vbi_format        *vbi;
            struct v4l2_sliced_vbi_format *sliced;
            struct v4l2_sdr_format        *sdr;
            uint8_t                       raw_data[200];
        } fmt;
    };

    struct v4l2_requestbuffers {
        uint32_t count;
        uint32_t type;
        uint32_t memory;

        ...;
    };

    struct v4l2_buffer {
        uint32_t index;
        uint32_t type;
        uint32_t memory;
        uint32_t length;
        uint32_t bytesused;

        union {
            uint32_t          offset;
            unsigned long     userptr;
            struct v4l2_plane *planes;
            int32_t           fd;
        } m;

        ...;
    };

    struct timeval {
        long    tv_sec;
        long    tv_usec;
    };

    struct v4lconvert_data *v4lconvert_create(int fd);
    int v4lconvert_convert(struct v4lconvert_data *data,
                           const struct v4l2_format *src_fmt,
                           const struct v4l2_format *dest_fmt,
                           unsigned char *src, int src_size,
                           unsigned char *dest, int dest_size);
''')

ffi.set_source('_v4l2', '''
    #include <linux/videodev2.h>
    #include <libv4l2.h>
    #include <libv4lconvert.h>
    #include <sys/mman.h>
    #include <sys/select.h>

    static int xioctl(int fd, unsigned long int request, void *arg) {
        int r;
        do {
            r = v4l2_ioctl(fd, request, arg);
        }
        while (-1 == r && EINTR == errno);
        return r;
    }

    static int xselect(int nfds, fd_set *readfds, fd_set *writefds,
                       fd_set *exceptfds, struct timeval *timeout) {
        int r;
        do {
            r = select(nfds, readfds, writefds, exceptfds, timeout);
        }
        while (-1 == r && EINTR == errno);
        return r;
    }
''', libraries=['v4l2'])

if __name__ == '__main__':
    ffi.compile()
