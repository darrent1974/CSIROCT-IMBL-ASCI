#!/usr/bin/env python

import os.path
import h5py
import logging
import numpy
import csiroct_imbl_asci.xtract as xtract

from tifffile import imsave

"""Module constants"""
file_imbl_h5_flat = 'BG_BEFORE.hdf'
file_imbl_h5_dark = 'DF_BEFORE.hdf'
file_imbl_h5_sample = 'SAMPLE.hdf'
h5_dataset_epics = 'entry/data/data'
h5_extension = '.h5'


def convert_xv_to_xtract_hdf5(file_flat, file_dark, file_sample_xv,
                              file_output_prefix, time_points=1,
                              read_buffer_gb=20) -> int:
    """Convert specified EPICS HDF5 flat, dark and strided XV samples
    into a series of X-TRACT compatible HDF5 files.

    Parameters
    ----------
    file_flat : str
        Filename of EPICS HDF5 for flats
    file_dark : str
        Filename of EPICS HDF5 for flats
    file_sample_xv : str
        Filename of EPICS HDF5 for XV samples
    file_output_prefix : str
        Filename of output X-TRACT HDF5
    time_points : int, optional
        Number of sample time points
        (default=1)
    read_buffer_gb : int, optional
        Internal read buffer size (GB)
        (default=20)

    Returns
    -------
    int
        The number of files created
    """

    logging.debug(
        'convert_xv_to_xtract_hdf5, time_points = %d', time_points)

    # Define empty arrays for flats and darks
    arr_flat = None
    arr_dark = None

    # Cacluate the required max read buffer in bytes
    max_buffer_size = read_buffer_gb * (1024 ** 3)

    # Open input IMBL (EPICS) flat HDF5 file
    with h5py.File(file_flat, 'r') as in_flat:
        logging.debug('Opened flat - %s', file_flat)
        # Read the entire dataset
        arr_flat = in_flat[h5_dataset_epics][:, :, :]
        logging.debug('Read flat dataset')

    # Open input IMBL (EPICS) dark HDF5 file
    with h5py.File(file_dark, 'r') as in_dark:
        logging.debug('Opened dark - %s', file_dark)
        # Read the entire dataset
        arr_dark = in_dark[h5_dataset_epics][:, :, :]
        logging.debug('Read dark dataset')

    # Open input IMBL (EPICS) xv sample HDF5 file
    with h5py.File(file_sample_xv, 'r') as in_sample:
        logging.debug('Opened sample - %s', file_sample_xv)

        dset_sample = in_sample[h5_dataset_epics]

        max_proj_idx = dset_sample.shape[0]

        # Check that the z-dimension matches the number of time points.
        # If not, adjust it by truncating left over projections
        if dset_sample.shape[0] % time_points != 0:
            max_proj_idx = dset_sample.shape[0] - (dset_sample.shape[0] %
                                                   time_points)

            logging.debug('Truncating projections from %d to %d',
                          dset_sample.shape[0],
                          max_proj_idx)

        # Number of projections for each time point
        num_proj_time_point = max_proj_idx // time_points

        # Zero padding length, for filename generation
        pad_length = len(str(time_points))

        # Compute the size of a single projection in bytes
        proj_size = (dset_sample.shape[1] *
                     dset_sample.shape[2] *
                     dset_sample.dtype.itemsize)

        buffer_time_points = max_buffer_size // (proj_size * time_points)
        adjusted_buffer_size = buffer_time_points * (proj_size * time_points)  

        # Size of the sample in bytes
        sample_size = max_proj_idx * proj_size

        # Compute how many partitions the sample set will
        # need to be split into based on the size of the
        # desired read buffer
        num_partitions = sample_size // adjusted_buffer_size

        # Account for left-overs
        if (sample_size % adjusted_buffer_size) > 0:
            num_partitions += 1

        # Construct an array of projections partitioned to
        # fit within the specified read buffer
        proj_partitions = numpy.array_split(numpy.arange(max_proj_idx),
                                            num_partitions)

        logging.debug('Number of partitions: %d', len(proj_partitions))

        h5_files = []
        h5_datasets = []

        # First loop, create and add flats/darks to output HDF5 files
        for i in range(time_points):

            filename = '%s%s%s' % (file_output_prefix,
                                   str(i).zfill(pad_length),
                                   h5_extension)

            # Create HDF5 file for writing
            h5_file = h5py.File(filename, 'w')

            # Append HDF5 file object
            h5_files.append(h5_file)
            logging.debug('Created file - %s', filename)

            # Create and store flats
            h5_file.create_dataset(
                xtract.h5_dataset_xtract_flats,
                data=arr_flat)

            logging.debug(
                'Created dataset - %s',
                xtract.h5_dataset_xtract_flats)

            # Create and store darks
            h5_file.create_dataset(
                xtract.h5_dataset_xtract_darks,
                data=arr_dark)

            logging.debug(
                'Created dataset - %s',
                xtract.h5_dataset_xtract_darks)

            # Flush flats and darks
            h5_file.flush()

            # Create sample dataset, chunked for projections
            dset = h5_file.create_dataset(
                xtract.h5_dataset_xtract_projections,
                (num_proj_time_point,
                 dset_sample.shape[1],
                 dset_sample.shape[2]),
                chunks=(1, dset_sample.shape[1], dset_sample.shape[2]),
                dtype=dset_sample.dtype)

            h5_datasets.append(dset)

        index_time_point = numpy.zeros(time_points, dtype=int)

        # Loop over the projection partitions
        for proj_part in proj_partitions:

            logging.debug(
                'Reading projections %d to %d of %d',
                proj_part[0], proj_part[-1], max_proj_idx)

            # Create an array to read into
            arr_proj_part = numpy.zeros(
                (proj_part.size, dset_sample.shape[1], dset_sample.shape[2]),
                dtype=dset_sample.dtype)

            # Define the source partition
            source_sel = numpy.s_[proj_part[0]:proj_part[-1]+1]

            # Read the projections in the given partition
            dset_sample.read_direct(
                arr_proj_part,
                source_sel=source_sel)

            logging.debug('Done')

            # Write projections from the partition to
            # the corresponding time point file
            for index_file in range(time_points):
                # Create an array copy of the sliced input partition
                # for the sample set, it's quicker to create a
                # contiguous copy rather than using a view and specifying
                # a source selection in the call to write_direct below
                arr_proj_time_point = arr_proj_part[index_file:
                                                    proj_part.size - time_points + index_file:
                                                    time_points].copy()

                #if index_file == 0:
                #   imsave('proj_{0}_{1}'.format(index_file,part_idx), arr_proj_time_point[0])                

                # Determine the how many projections are in the
                # associated view for this time point
                time_point_partition_size = arr_proj_time_point.shape[0]

                # Define s destination selection for the sample
                # set in the output file
                dest_sel = numpy.s_[index_time_point[index_file]:
                                    (index_time_point[index_file] +
                                     time_point_partition_size)]

                logging.debug(
                    'Writing file, time point %d, projections %d to %d',
                    index_file,
                    index_time_point[index_file],
                    index_time_point[index_file] + time_point_partition_size - 1)                     

                # Write projection partition directly into the
                # associated output file for the time point
                h5_datasets[index_file].write_direct(
                    arr_proj_time_point,
                    dest_sel=dest_sel)

                # Flush the HDF5 file
                #h5_files[index_file].flush()

                # Update the index for writing sample set
                index_time_point[index_file] += time_point_partition_size

                # Force garbage collection to keep
                # the memory footprint down
                arr_proj_time_point = None

            logging.debug(
                'Written partition %d to %d of %d',
                proj_part[0], proj_part[-1], max_proj_idx)

            # Force garbage collection to keep
            # the memory footprint down
            arr_proj_part = None

        logging.debug('Flushing and closing HDF5 files')
        # Third loop, cleanup
        for h5_file in h5_files:
            h5_file.flush()
            h5_file.close()

        logging.debug('Conversion complete')

    return time_points


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
