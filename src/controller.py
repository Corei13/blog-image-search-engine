import os
import faiss
import random
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input

vgg16 = VGG16(weights='imagenet')
model = tf.keras.models.Model(inputs=vgg16.input, outputs=vgg16.get_layer('fc2').output)

def make_path(*args):
  return os.path.join(os.path.dirname(__file__), *args)

def get_faiss_index(faiss_index_path):
  if os.path.exists(faiss_index_path):
    faiss_index = faiss.read_index(faiss_index_path)
    print ('Read faiss index from {}'.format(faiss_index_path))
    return faiss_index
  else:
    faiss_index = faiss.IndexFlatIP(4096)
    faiss_index = faiss.IndexIDMap2(faiss_index)
    print ('Creating new faiss index at {}'.format(faiss_index_path))
    return faiss_index

faiss_index_path = make_path('data/embeddings.index')
faiss_index = get_faiss_index(faiss_index_path)

def compute_embeddings(images):
  processed = []
  for image in images:
    image = image.resize((224, 224)).convert('RGB')
    image = tf.keras.preprocessing.image.img_to_array(image)
    processed.append(image)

  processed = preprocess_input(np.stack(processed, axis=0)) # (*, 224, 224, 3)

  embedding = model.predict(processed) # (*, 4096)
  embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
  return embedding

def save_embeddings(paths):
  location = make_path('data/images')

  images = {}
  for path in paths:
    try:
      images[os.path.basename(path)] = Image.open(path)
    except Exception as e:
      print ('Failed to load {}: {}'.format(path, e))

  embeddings = compute_embeddings(images.values())
  keys = [random.randint(0, 2**63) for _ in range(len(images))]
  faiss_index.add_with_ids(embeddings, np.asarray(keys))
  faiss.write_index(faiss_index, faiss_index_path)

  keys = ['{:020d}'.format(key) for key in keys]
  for key, path in zip(keys, images.keys()):
    prev_path = make_path('data/images/new', path)
    new_path = make_path('data/images/processed', key + '.jpg')
    try:
      os.rename(prev_path, new_path)
    except Exception as e:
      print ('Failed to move {}: {}'.format(prev_path, e))

  return keys

def search(key, total=30):
  try:
    embedding = faiss_index.reconstruct(int(key))
    results = faiss_index.search(np.expand_dims(embedding, axis=0), k=total + 1)
    return list(zip(results[0][0], ['{:020d}'.format(k) for k in results[1][0] if k != key]))
  except Exception as e:
    print (e)

def save_image(file):
  try:
    image = Image.open(file.stream)
    image = image.convert('RGB')
    path = make_path('data/images/new', '{:020d}.jpg'.format(random.randint(0, 2**63)))
    image.save(path)
    print ('Saved file to', path)
    return save_embeddings([path])[0]
  except Exception as e:
    print ('Failed to save:', e)
