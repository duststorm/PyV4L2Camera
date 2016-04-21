from PIL import Image

from PyV4L2Camera.camera import Camera

camera = Camera('/dev/video0')

for _ in range(3):
    frame = camera.get_frame()
    im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                         'RGB')
    im.show()

camera.close()
