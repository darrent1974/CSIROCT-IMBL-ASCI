import csiroct_imbl_asci
import os.path
import logging

logging.basicConfig(level=logging.DEBUG)

cmdXLICTPreProcSino = '/home/tho78s/development/X-TRACT-trunk/build/linux/XLICTPreProcSino.exe'
cmdXLICTWorkflowMPI = '/home/tho78s/development/X-TRACT-trunk/build/linux/XLICTWorkflowMPI.exe'
cmdXLICTReconMPI = '/home/tho78s/development/X-TRACT-trunk/build/linux/XLICTReconMPI.exe'
cmdXLICOR = '/home/tho78s/development/X-TRACT-trunk/build/linux/XLICOR.exe'

dirTestH5 = '/mnt/csiro/civ/scratch/lung/HRCT/19-2-R2173-Lung'

file_flat = os.path.join(  dirTestH5, csiroct_imbl_asci.convert.file_imbl_h5_flat )
file_dark = os.path.join(  dirTestH5, csiroct_imbl_asci.convert.file_imbl_h5_dark )
file_sample = os.path.join(  dirTestH5, csiroct_imbl_asci.convert.file_imbl_h5_sample )
file_output = '/mnt/Data/x-tract_converted.h5'

numProj = csiroct_imbl_asci.convert_epics_to_xtract_hdf5( file_flat, 
    file_dark, file_sample, file_output, sample_start=10, sample_stride=100 )

print( 'Num projections = ', numProj )

