import os.path
import h5py
import .x-tract

file_imbl_h5_flat = 'BG_BEFORE.hdf'
file_imbl_h5_dark = 'DF_BEFORE.hdf'
file_imbl_h5_samle = 'SAMPLE.hdf'

h5_dataset_epics = 'entry/data/data'

def convert_epics_to_xtract_hdf5( file_flat, file_dark, file_sample, file_output, sample_start=None, sample_stride=None ):
    # Open output X-TRACT HDF5 file
    with h5py.File(os.path.join(dir_experiment_output, file_output), 'w') as out_xtract:
        group_exchange = out_xtract.create_group( h5_group_xtract )

        # Open input IMBL (EPICS) flat HDF5 file
        with h5py.File(os.path.join(dir_experiment_input, file_flat), 'r') as in_flat:
            # Copy dataset
            in_flat.copy( h5_dataset_epics, group_exchange, 'data_flat' )

        # Open input IMBL (EPICS) dark HDF5 file    
        with h5py.File(os.path.join(dir_experiment_input, file_dark), 'r') as in_dark:
            # Copy dataset
            in_dark.copy( h5_dataset_epics, group_exchange, 'data_dark' )

        # Open input IMBL (EPICS) sample HDF5 file    
        with h5py.File(os.path.join(dir_experiment_input, file_sample), 'r') as in_sample:
            # Copy dataset
            in_sample.copy( h5_dataset_epics, group_exchange, 'data' )
            
            # return the number of projections
            return group_exchange['data'].shape[0]