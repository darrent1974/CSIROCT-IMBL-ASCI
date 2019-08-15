import os.path
import h5py
import numpy as np
import csiroct_imbl_asci as cia
import csiroct_imbl_asci.convert as convert
import csiroct_imbl_asci.xtract as xtract
import pytest

def check_dataset_shape_type( dset, shape, dtype ):
    assert dset is not None
    assert dset.shape == shape
    assert dset.dtype == dtype

def create_test_epics_hdf5(file_test_epics):
    # Create test EPICS HDF5 file
    with h5py.File( file_test_epics, 'w' ) as f_test_epics:
        # Create a small test dataset from a numpy array
        arr = np.arange( (100 * 10 * 10), dtype=np.uint16 ).reshape( (100, 10, 10) )

        dset = f_test_epics.create_dataset( convert.h5_dataset_epics, data=arr )
        check_dataset_shape_type( dset, (100, 10, 10), np.uint16 )

    # Check that the file was created succesfully
    assert os.path.isfile( file_test_epics ) == True


def test_convert_epics_to_xtract_hdf5_no_stride(tmp_path):
    file_test_epics = os.path.join( tmp_path, 'test_epics.h5' )
    file_test_xtract = os.path.join( tmp_path, 'test_x-tract.h5' )

    create_test_epics_hdf5( file_test_epics )

    # Convert to X-TRACT compatible HDF5 using the same EPICS
    # test file for flats, darks and samples
    cia.convert_epics_to_xtract_hdf5( file_test_epics, file_test_epics, file_test_epics, file_test_xtract )

    # Check that the file was created succesfully
    assert os.path.isfile( file_test_xtract ) == True

    # Open the converted file to test the contents
    with h5py.File( file_test_xtract, 'r' ) as f_test_xtract:
        # Test datasets are present
        dset_flats = f_test_xtract[xtract.h5_dataset_xtract_flats]
        check_dataset_shape_type( dset_flats, (100, 10, 10), np.uint16 )

        dset_darks = f_test_xtract[xtract.h5_dataset_xtract_darks]      
        check_dataset_shape_type( dset_darks, (100, 10, 10), np.uint16 )

        dset_projections = f_test_xtract[xtract.h5_dataset_xtract_projections]
        check_dataset_shape_type( dset_projections, (100, 10, 10), np.uint16 )

def test_convert_epics_to_xtract_hdf5_stride(tmp_path):
    file_test_epics = os.path.join( tmp_path, 'test_epics.h5' )
    file_test_xtract = os.path.join( tmp_path, 'test_x-tract.h5' )

    create_test_epics_hdf5( file_test_epics )

    # Convert to X-TRACT compatible HDF5 using the same EPICS
    # test file for flats, darks and samples
    cia.convert_epics_to_xtract_hdf5( file_test_epics, file_test_epics, file_test_epics, file_test_xtract, 10, 10 )

    # Check that the file was created succesfully
    assert os.path.isfile( file_test_xtract ) == True

    # Open the converted file to test the contents
    with h5py.File( file_test_xtract, 'r' ) as f_test_xtract:
        # Test datasets are present
        dset_flats = f_test_xtract[xtract.h5_dataset_xtract_flats]
        check_dataset_shape_type( dset_flats, (100, 10, 10), np.uint16 )

        dset_darks = f_test_xtract[xtract.h5_dataset_xtract_darks]      
        check_dataset_shape_type( dset_darks, (100, 10, 10), np.uint16 )

        dset_projections = f_test_xtract[xtract.h5_dataset_xtract_projections]
        check_dataset_shape_type( dset_projections, (9, 10, 10), np.uint16 )