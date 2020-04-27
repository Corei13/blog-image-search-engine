import os
import sys
import glob
import math
import random
from PIL import Image


if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise Exception('Provide number of images to create sprite')

  N = int(math.ceil(math.sqrt(int(sys.argv[1]))))

  output_location = os.path.join(os.path.dirname(__file__), 'data')

  D = min(8192 // N, 200)

  paths = random.sample(glob.glob(os.path.join(os.path.dirname(__file__), 'data/images/processed/*.jpg')), N * N)

  sprite = Image.new(
    mode='RGB',
    size=(N * D, N * D),
    color=(0, 0, 0))
  
  for x in range(N):
    for y in range(N):
      index = x * N + y
      if index >= len(paths):
        break
      image = Image.open(paths[index])
      image.thumbnail((D, D), Image.ANTIALIAS)
      sprite.paste(image, (x * D, y * D))

      if index % 100 == 0:
        print ('processed {}/{}'.format(index + 1, len(paths)))

  sprite.save(output_location, transparency=0)
