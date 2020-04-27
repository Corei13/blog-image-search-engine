import os
import glob
import time
import datetime
from controller import save_embeddings

BATCH_SIZE=128

if __name__ == '__main__':
  paths = glob.glob(os.path.join(os.path.dirname(__file__), 'data/images/new/*.jpg'))
  start = time.time()
  processed, success, failed = 0, 0, 0

  for index in range(0, len(paths), BATCH_SIZE):
    try:
      keys = save_embeddings(paths[index: index + BATCH_SIZE])
      failed += len(paths[index: index + BATCH_SIZE]) - len(keys)
    except Exception as e:
      print ('Failed to get embeddings: {}'.format(e))
      failed += len(paths[index: index + BATCH_SIZE])
    
    processed += len(paths[index: index + BATCH_SIZE])
    elapsed = time.time() - start
    rate = processed / elapsed
    eta = datetime.timedelta(seconds=int((len(paths) - processed) / rate)) if rate > 0 else None
    print ('processed: {}, failed: {}, rate: {:.2f}/s, elapsed: {}, eta: {}'.format(processed, failed, rate, datetime.timedelta(seconds=int(elapsed)), eta))
