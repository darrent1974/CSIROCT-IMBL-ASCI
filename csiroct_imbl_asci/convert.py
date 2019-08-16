#!/usr/bin/env python

import os.path
import h5py
import logging
import numpy
import csiroct_imbl_asci.xtract as xtract

"""Module constants"""
file_imbl_h5_flat = 'BG_BEFORE.hdf'
file_imbl_h5_dark = 'DF_BEFORE.hdf'
file_imbl_h5_sample = 'SAMPLE.hdf'
h5_dataset_epics = 'entry/data/data'


def convert_epics_to_xtract_hdf5(file_flat, file_dark, file_sample,
                                 file_output, sample_start=0,
                                 sample_stride=1) -> int:
    """Convert multiple EPICS HDF5 plugin style HDF5 files into a single
    HDF5 file as used by X-TRACT. Separate files for flats, darks and
    samples are specified which will be added as separate datasets in
    the output file. An optional start index and striding can be applied
    when copying the sample dataset to extract a subset to be written
    to the output projection dataset. Note: This will only be applied
    to sample dataset only.

    Parameters
    ----------
    file_flat : str
        Filename of EPICS HDF5 for flats
    file_dark : str
        Filename of EPICS HDF5 for flats
    file_sample : str
        Filename of EPICS HDF5 for samples
    file_output : str
        Filename of output X-TRACT HDF5
    sample_start : int, optional
        The start index to copy from the input sample
        projection dataset (default=0)

    sample_stride : int, optional
        Striding to use for copying input sample
        projections (default=1)

    Returns
    -------
    int
        The number of projections in the output projection dataset
        as determined by sample_start and sample_stride
    """

    logging.debug(
        'convert_epics_to_xtract_hdf5, sample_start = %d, sample_stride = %d',
        sample_start, sample_stride)

    # Open output X-TRACT HDF5 file
    with h5py.File(file_output, 'w') as out_xtract:
        logging.debug('Opened output - %s', file_output)
        group_exchange = out_xtract.create_group(
            xtract.h5_group_xtract_exchange)

        # Open input IMBL (EPICS) flat HDF5 file
        with h5py.File(file_flat, 'r') as in_flat:
            logging.debug('Opened flat - %s', file_flat)
            # Copy dataset
            in_flat.copy(h5_dataset_epics, group_exchange, 'data_flat')
            logging.debug('Copied flat dataset to - %s', 'data_flat')

        # Open input IMBL (EPICS) dark HDF5 file
        with h5py.File(file_dark, 'r') as in_dark:
            logging.debug('Opened dark - %s', file_dark)
            # Copy dataset
            in_dark.copy(h5_dataset_epics, group_exchange, 'data_dark')
            logging.debug('Copied dark dataset to - %s', 'data_dark')

        # Open input IMBL (EPICS) sample HDF5 file
        with h5py.File(file_sample, 'r') as in_sample:
            logging.debug('Opened sample - %s', file_sample)

            if sample_start == 0 and sample_stride == 1:
                # Simply copy the dataset as with darks and flats
                in_sample.copy(h5_dataset_epics, group_exchange, 'data')
            else:
                # Need to create a new dataset and copy strided projections
                # from the given start index

                dset_in = in_sample[h5_dataset_epics]

                # Determine the shape of the input sample dataset
                shape = dset_in.shape
                logging.debug('Sample input dataset shape - %s', str(shape))

                # Construct a list of indicies to copy
                list_indexes = list(range(sample_start, shape[0],
                                          sample_stride))

                logging.debug('list_indexes length = %d', len(list_indexes))

                # Create the output dataset
                dset_out = group_exchange.create_dataset(
                    'data',
                    (len(list_indexes), shape[1], shape[2]),
                    dtype=dset_in.dtype)

                logging.debug(
                    'Sample output dataset shape - %s',
                    str(dset_out.shape))

                # Create a temporary array to hold a single projection
                projection = numpy.zeros(
                    (1, shape[1], shape[2]),
                    dtype=dset_out.dtype)

                # Copy strided projections to the new dataset
                index_output = 0
                for index_input in list_indexes:
                    # Read
                    dset_in.read_direct(
                        projection,
                        source_sel=numpy.s_[index_input])

                    # Write
                    dset_out.write_direct(
                        projection,
                        dest_sel=numpy.s_[index_output])

                    index_output += 1

                logging.debug(
                    'copied %d sample projections',
                    len(list_indexes))

            return group_exchange['data'].shape[0]
