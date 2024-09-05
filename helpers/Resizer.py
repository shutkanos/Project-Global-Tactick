from PIL import Image
import numpy as np
im = Image.open('t.png')
pixels = list(im.getdata())
Width, Height = im.size
Step = Width // 50
pixels = [pixels[i * Width:(i + 1) * Width] for i in range(Height)]
NoxPixels = [[pixels[i][j] for j in range(Step // 2, Width, Step)] for i in range(Step // 2, Height, Step)]
array = np.array(NoxPixels, dtype=np.uint8)
new_image = Image.fromarray(array)
new_image.save("t2.png")
