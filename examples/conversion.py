import numpy
from PIL import Image

from PyV4L2Camera.camera import Camera

camera = Camera('/dev/video0', 1920, 1080)
controls = camera.get_controls()

for control in controls:
    print(control.name)

for _ in range(2):
    frame = camera.get_frame()

    # Decode the image
    im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                         'RGB')

    # Convert the image to a numpy array and back to the pillow image
    arr = numpy.asarray(im)
    im = Image.fromarray(numpy.uint8(arr))

    # Display the image to show that everything works fine
    im.show()

camera.close()
