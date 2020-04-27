import os
import sys
import time
import hashlib
import datetime
import mimetypes
import urllib.request
from multiprocessing.pool import ThreadPool

DEBUG = os.environ.get('DEBUG') == 'TRUE'

def hash(text):
  return hashlib.md5(text.encode('UTF-8')).hexdigest()

def download(url, location):
  if not mimetypes.guess_type(url)[0] == 'image/jpeg':
    print ('Skip {}, not a jpeg image'.format(url))

  path = os.path.join(location, hash(url) + '.jpg')

  if not os.path.exists(path):
    try:
      loc = urllib.request.urlretrieve(url, path)
      if DEBUG:
        print ('Saved {} to {}'.format(url, path))
      return True
    except Exception as e:
      print ('Failed to download {}: {}'.format(url, e))
      return False
  else:
    if DEBUG:
      print ('Skip {}, already saved at {}'.format(url, path))

if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise Exception('Provide image url list to download')

  if len(sys.argv) < 3:
    raise Exception('Provide location to save downloaded images')

  location = sys.argv[2]
  if not os.path.exists(location):
    raise Exception('{} does not exist'.format(location))
  elif not os.path.isdir(location):
    raise Exception('{} is not a directory'.format(location))

  start = time.time()
  with open(sys.argv[1]) as f:
    lines = f.readlines()
    urls = map(str.strip, lines)
    processed, success, failed, skipped = 0, 0, 0, 0

    def _download(url):
      global processed, success, failed, skipped
      res = download(url, location)
      processed += 1
      if res is True:
        success += 1
      elif res is False:
        failed += 1
      else:
        skipped += 1
      if processed % 100 == 0:
        elapsed = time.time() - start
        rate = success / elapsed
        eta = datetime.timedelta(seconds=int((len(lines) - processed) / rate)) if rate > 0 else None
        print ('success: {}, failed: {}, skipped: {}, rate: {:.2f}/s, elapsed: {}, eta: {}'.format(success, failed, skipped, rate, datetime.timedelta(seconds=int(elapsed)), eta))

    with ThreadPool(100) as pool:
      pool.map(_download, urls)