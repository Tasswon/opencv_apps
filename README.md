# Opencv Apps
Basic opencv programs made with a PyQt5 gui.

Includes:
  - Webcam loading and playing
  - Snapshots
  - Image loading
  - Image histogram equalization

## Image Morph
**Gui Library**: PyQt5\
**Delaunay Library**: scipy.spatial.Delaunay\
**Image Library**: OpenCV

The images do not need to be the same size, however they must have the same number of manually selected key points. This is verified prior to performing the actual triangulation between the two sets of points. Additionally, the key points should be in the same relative position, to avoid unexpected shifts.

An issue with this task is related to the actual functions utilized in opencv itself. The affine transformation is applied to the entire image, whereas the purpose is to apply it to the individual triangles. The original function applied a simple methodology, however it requires many key points to smooth out the result. Therefore, cropping the image with a bounding box was used to efficiently mitigate this problem.

