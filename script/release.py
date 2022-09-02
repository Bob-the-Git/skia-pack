#! /usr/bin/env python3

import common, json, os, re, sys, urllib.request

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'skia'))
  version = common.version()
  build_type = common.build_type()
  machine = common.machine()
  target = common.target()
  classifier = common.classifier()
  os.chdir(os.pardir)

  zip = 'Skia-' + version + '-' + target + '-' + build_type + '-' + machine + classifier + '.zip'
  if not os.path.exists(zip):
    print('Can\'t find "' + zip + '"')
    return 1


  CHUNK_SIZE = 1024 * 1024 * 1024
  file_number = 1
  with open(zip) as f:
      chunk = f.read(CHUNK_SIZE)
      while chunk:
          with open(zip + "." + str(file_number)) as chunk_file:
              chunk_file.write(chunk)
          upload(zip + "." + str(file_number))
          file_number += 1
          chunk = f.read(CHUNK_SIZE)

  return 0

def upload(zip):
    headers = common.github_headers()

    try:
      resp = urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/Bob-the-Git/skia-pack/releases/tags/' + common.version(), headers=headers)).read()
    except urllib.error.URLError as e:
      data = '{"tag_name":"' + common.version() + '","name":"' + common.version() + '"}'
      resp = urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/Bob-the-Git/skia-pack/releases', data=data.encode('utf-8'), headers=headers)).read()
    upload_url = re.match('https://.*/assets', json.loads(resp.decode('utf-8'))['upload_url']).group(0)

    print('Uploading', zip, 'to', upload_url)
    headers['Content-Type'] = 'application/zip'
    headers['Content-Length'] = os.path.getsize(zip)
    with open(zip, 'rb') as data:
      urllib.request.urlopen(urllib.request.Request(upload_url + '?name=' + zip, data=data, headers=headers))

if __name__ == '__main__':
  sys.exit(main())
