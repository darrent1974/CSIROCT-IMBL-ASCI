from setuptools import setup
import os
import sys

# set environment variables for X-TRACT paths and executables
os.system("export XTRACT_BIN_PATH=/opt/x-tract/bin/")
os.system("export XTRACT_CTWORKFLOW=XLICTWorkflowMPI")
os.system("export XTRACT_CTPREPROCSINO=XLICTPreProcSinoMPI")
os.system("export XTRACT_CTRECON=XLICTReconMPI")
os.system("export XTRACT_COR=XLICOR")

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'csiroct_imbl_asci', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='csiroct_imbl_asci',
    version=version['__version__'],
    description=('CSIROCT IMBL ASCI library.'),
    long_description=long_description,
    author='Darren Thompson',
    author_email='darren.thompson@csiro.au',
    url='https://github.com/darrent1974/CSIROCT-IMBL-ASCI',
    license='GPL-3.0',
    packages=['csiroct_imbl_asci'],
    install_requires=[
        'numpy',
        'h5py',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],
    )
