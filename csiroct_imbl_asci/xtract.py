#!/usr/bin/env python

import h5py
import subprocess
import os
import os.path
import logging

"""Module constants"""
h5_group_xtract_exchange = 'exchange'
h5_dataset_xtract_projections = 'exchange/data'
h5_dataset_xtract_flats = 'exchange/data_flat'
h5_dataset_xtract_darks = 'exchange/data_dark'
h5_dataset_xtract_sinograms = 'exchange/data_sino'


def assemble_command(file_command, dict_args) -> list:
    """Assembles a given command string and a dictionay of
    parameters into a unified list that can be passed to
    a Python subprocess object for execution

    Parameters
    ----------
    file_command : str
        command
    dict_args : dict
        Dictionary of parameter key/value pairs to
        be added to the command list

    Returns
    -------
    list
        A list of string items with the initial command and
        parameter key/value pairs as seperate elements.
        Parameter keys are prepended with '--'
    """
    list_cmd = [file_command]

    for arg, val in dict_args.items():
        list_cmd.append('--{0}'.format(arg))
        list_cmd.append(val)

    return list_cmd


def get_num_projections(file_xtract_hdf5) -> int:
    """Returns the number of projections in an X-TRACT
    compatible HDF5 file.

    Parameters
    ----------
    file_xtract_hdf5 : str
        Filename of input X-TRACT HDF5 file

    Returns
    -------
    int
        Number of projections, ie the magnitude of the
        0'th dimension of the 'exchange/data' dataset
    """
    # Open HDF5 file as read-only
    with h5py.File(file_xtract_hdf5, 'r') as in_xtract:
        return in_xtract[h5_dataset_xtract_projections].shape[0]


def create_config_dictionary(file_config) -> dict:
    """Creates a dictionary of key/value pairs by parsing
    the input JSON file

    Parameters
    ----------
    file_config : str
        Filename of JSON file containing key/value pairs

    Returns
    -------
    dict
        Dictionary of key/value pairs
    """
    raise NotImplemented()


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        universal_newlines=True)

    for stdout_line in iter(popen.stdout.readline, ''):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()

    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def run_xli_cmd(dict_params, cmd_xli):
    """Run the specified X-TRACT (XLI) executable with the given
    dictionary of parameters

    Parameters
    ----------
    dict_params : dict
        Dictionary of key/value parameters

    cmd_xli : str
        String specifying the full path of the
        X-TRACT executable
    """
    list_cmd = assemble_command(cmd_xli, dict_params)
    logging.debug('run_xli_cmd, cmd - %s', list_cmd)

    for path in execute(list_cmd):
        print(path, end='')


def run_XLICTPreProc(dict_params, cmd_non_env=None):
    """Wrapper for the X-TRACT XLICTPreProc (Pre-processing) executable
    with the given dictionary of parameters

    Parameters
    ----------
    dict_params : dict
        Dictionary of key/value parameters

    cmd_non_env : str (optional)
        String specifying the full path of an alternative
        XLICTPreProc executable (default=None).
        By default the the path is formed from environment
        variables.
    """
    if cmd_non_env is None:
        # Construct command from environment variables
        cmd = os.path.join(
            os.environ['XTRACT_BIN_PATH'],
            os.environ['XTRACT_CTPREPROCSINO'])
    else:
        cmd = cmd_non_env

    run_xli_cmd(dict_params, cmd)


def run_XLICTWorkflow(dict_params, cmd_non_env=None):
    """Wrapper for the X-TRACT XLICTWorkflow (CT-Workflow) executable
    with the given dictionary of parameters

    Parameters
    ----------
    dict_params : dict
        Dictionary of key/value parameters

    cmd_non_env : str (optional)
        String specifying the full path of an alternative
        XLICTWorkflow executable (default=None).
        By default the the path is formed from environment
        variables.
    """
    if cmd_non_env is None:
        # Construct command from environment variables
        cmd = os.path.join(
            os.environ['XTRACT_BIN_PATH'],
            os.environ['XTRACT_CTWORKFLOW'])
    else:
        cmd = cmd_non_env

    run_xli_cmd(dict_params, cmd)


def run_XLICTRecon(dict_params, cmd_non_env=None):
    """Wrapper for the X-TRACT XLICTRecon (CT Recon) executable
    with the given dictionary of parameters

    Parameters
    ----------
    dict_params : dict
        Dictionary of key/value parameters

    cmd_non_env : str (optional)
        String specifying the full path of an alternative
        XLICTRecon executable (default=None).
        By default the the path is formed from environment
        variables.
    """
    if cmd_non_env is None:
        # Construct command from environment variables
        cmd = os.path.join(
            os.environ['XTRACT_BIN_PATH'],
            os.environ['XTRACT_CTRECON'])
    else:
        cmd = cmd_non_env

    run_xli_cmd(dict_params, cmd)


def run_XLICOR(dict_params, cmd_non_env=None):
    """Wrapper for the X-TRACT XLICOR (Centre-of-rotation) executable
    with the given dictionary of parameters

    Parameters
    ----------
    dict_params : dict
        Dictionary of key/value parameters

    cmd_non_env : str (optional)
        String specifying the full path of an alternative
        XLICOR executable (default=None).
        By default the the path is formed from environment
        variables.
    """
    if cmd_non_env is None:
        # Construct command from environment variables
        cmd = os.path.join(
            os.environ['XTRACT_BIN_PATH'],
            os.environ['XTRACT_COR'])
    else:
        cmd = cmd_non_env

    run_xli_cmd(dict_params, cmd)
