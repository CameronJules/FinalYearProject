import tensorflow
import argparse
from os import symlink, remove, makedirs
from os.path import join, dirname, abspath
from shutil import copytree, rmtree
from subprocess import call
context = 'usr/local'

tf_dir = dirname(tensorflow.__file__)
version = tensorflow.__version__

version_list = version.split('.')
major_version = int(version_list[0])
minor_version = int(version_list[1])

# From Tensorflow 1.15. libraries are stored in `tensorflow_core`
if major_version >= 1:
    if minor_version >= 15:
        tf_dir = tf_dir + '_core'

print('found tensorflow in "{}"'.format(tf_dir))
print('tensorflow version: {}'.format(version))

file_dir = dirname(abspath(__file__))

# create symbolic links fo the libraries
print('creating symbolic links...')

libtensorflow = 'tensorflow_framework'
pywrap_tensorflow_internal = 'pywrap_tensorflow_internal'

libtensorflow_name = 'lib{}.so.{}'.format(libtensorflow, major_version)
src = join(tf_dir, libtensorflow_name)
tgt = join(context, 'lib', libtensorflow_name)
# call(['ln', '-sf', src, tgt])

pywrap_tensorflow_name = '_{}.so'.format(pywrap_tensorflow_internal)
src = join(tf_dir, 'python', pywrap_tensorflow_name)
tgt = join(context, 'lib', pywrap_tensorflow_name)
# call(['ln', '-sf', src, tgt])
print(f"src: {src} \n target: {tgt}")
# add also symbolic links with standarized library names
tgt = join(context, 'lib', 'lib{}.so'.format(libtensorflow))
# call(['ln', '-sf', libtensorflow_name, tgt])

tgt = join(context, 'lib', 'lib{}.so'.format(pywrap_tensorflow_internal))
# call(['ln', '-sf', pywrap_tensorflow_name, tgt])

libs = ('-l{} -l{}'.format(pywrap_tensorflow_internal, libtensorflow))
print("Tensor wrap:",tgt)
# copy headers to the context dir
include_dir = join(context, 'include', 'tensorflow', 'c')
rmtree(include_dir, ignore_errors=True)
# copytree(join(dirname(__file__), 'c'), include_dir)


# WARNING. With `--mode libtensorflow`, the following problem is known
# to arise when importing Essentia and Tensorflow in Python at the same time.
#   In [1]: import tensorflow
#   In [2]: import essentia
#
#   ImportError: /usr/local/lib/libtensorflow.so.1: undefined symbol:
#  _ZN6google8protobuf5Arena18CreateMaybeMessageIN10tensorflow16OptimizerOptionsEIEEEPT_PS1_DpOT0_

# The recommended solution is to link Essentia against the Tensorflow shared
# libraries shipped with the Tensorflow wheel with `--mode python`