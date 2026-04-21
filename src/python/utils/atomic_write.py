import os
import tempfile

def atomic_write(file_path, content):
    dir_name = os.path.dirname(file_path) or '.' 
    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
        tf.write(content)
        temp_name = tf.name
        tf.flush()
        os.fsync(tf.fileno())
    os.replace(temp_name, file_path)
