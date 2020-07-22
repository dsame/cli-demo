import os
import hashlib
import json

from oml.exceptions import OMLException


def create_manifest(root):
    manifest = {'files': []}
    os.chdir(root)
    for path, subdirs, files in os.walk(root):
        for file in files:
            if file == 'signature':
                raise OMLException("File with name 'signature' is not allowed. Please change and rerun.")
            file_path = os.path.join(path, file)
            file_data = {
                'name': os.path.relpath(file_path, root),  # Do we need .//?
                'length': os.path.getsize(file_path),
                'value': generate_file_sha512(file_path),
                'algorithm': 'SHA512'
            }
            manifest['files'].append(file_data)
    json_manifest = json.dumps(manifest, indent=4, ensure_ascii=True)
    with open("SecureManifest.json", "w") as text_file:
        text_file.write(json_manifest)


def generate_file_sha512(filepath, blocksize=2**20):
    m = hashlib.sha512()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest().upper()
