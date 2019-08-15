import h5py
import subprocess
import os
import os.path

h5_group_xtract_exchange = 'exchange'

h5_dataset_xtract_projections = 'exchange/data'
h5_dataset_xtract_flats = 'exchange/data_flat'
h5_dataset_xtract_darks = 'exchange/data_dark'
h5_dataset_xtract_sinograms = 'exchange/data'

def assemble_command( file_command, dict_args ):
    list_cmd = [file_command]
    
    for arg, val in dict_args.items():
        list_cmd.append( '--{0}'.format(arg) )
        list_cmd.append( val )
        
    return list_cmd

def get_num_projections( file_xtract_hdf5 ):
    # Open HDF5 file as read-only
    with h5py.File(file_xtract_hdf5, 'r') as in_xtract:
        return in_xtract[h5_dataset_xtract_projections].shape[0]

def create_config_dictionary( file_config ):
    return []

def run_xli_cmd( dict_params, cmd_xli ):
        
    list_cmd = assemble_command( cmd_xli, dict_params )
    
    print( list_cmd )

    proc = subprocess.Popen( list_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )

    stdout,stderr = proc.communicate()
    
    return stdout, stderr

def run_XLICTPreProc( dict_params, cmd_non_env=None ):
    if cmd_non_env is None:
        cmd = os.path.join( os.environ['XTRACT_BIN_PATH'], os.environ['XTRACT_CTPREPROCSINO'] )
    else:
        cmd = cmd_non_env

    return run_xli_cmd( dict_params, cmd )

def run_XLICTWorkflow( dict_params, cmd_non_env=None ):
    if cmd_non_env is None:
        cmd = os.path.join( os.environ['XTRACT_BIN_PATH'], os.environ['XTRACT_CTWORKFLOW'] )
    else:
        cmd = cmd_non_env

    return run_xli_cmd( dict_params, cmd )

def run_XLICTRecon( dict_params, cmd_non_env=None ):
    if cmd_non_env is None:
        cmd = os.path.join( os.environ['XTRACT_BIN_PATH'], os.environ['XTRACT_CTRECON'] )
    else:
        cmd = cmd_non_env

    return run_xli_cmd( dict_params, cmd )    

def run_XLICOR( dict_params, cmd_non_env=None ):
    if cmd_non_env is None:
        cmd = os.path.join( os.environ['XTRACT_BIN_PATH'], os.environ['XTRACT_COR'] )
    else:
        cmd = cmd_non_env

    return run_xli_cmd( dict_params, cmd )    