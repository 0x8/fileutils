import coloredlogs
import logging
import hashlib
import shutil
import pprint
import time
import os

LOG_LEVEL = 'DEBUG'
_LOG_LEVEL = eval('logging.' + LOG_LEVEL)

logger = logging.getLogger('pth_test')
logger.setLevel(_LOG_LEVEL)

coloredlogs.install(level=LOG_LEVEL, logger=logger)

def strip_path(full_path, partial_path):
    ''' 
    Strip partial_path out of full_path
    For example:
        full_path: A/B/C/D/E.txt
        partial_path: A/B/C
        return: D/E.txt

    or:
        full_path: A/B/C/D/E.txt
        partial_path: A/B/C/
        return: D/E.txt

    (Accounts for extra/trailing '/' characters)
    '''
    # First replace partial_path with empty ''
    adjusted_path = full_path.replace(partial_path,'')

    # Next handle leftover '/' or '\\' characters in
    # the beginning of the path.
    if adjusted_path.startswith('/'):
        adjusted_path = adjusted_path.lstrip('/')
    if adjusted_path.startswith('\\'):
        adjusted_path = adjusted_path.lstrip('\\')

    return adjusted_path


def enumerate_relative_subdirectories(path):
    '''
    Given a path, find all unique subdirectories along it
    '''
    unique_relative_dirs = set()
    for dirpath, subdirs, files in os.walk(path):
        if subdirs:
            for subdir in subdirs:
                full_sub_path = os.path.join(dirpath, subdir)
                if os.path.isdir(full_sub_path):
                    rel_sub_path = strip_path(full_sub_path, path)
                    unique_relative_dirs.add(rel_sub_path)

    return unique_relative_dirs


def copy_dir(src, dst):
    '''
    Copy directory at src to directory at dst. The source directory _must_ exist
    however the destination directory may exist or not exist.

    This is meant to wrap shutil and remedy its _many_ shortcomings with copy.
    '''
    
    # Exit if source does not exist
    if not os.path.isdir(src):
        logger.error('Source must be a valid directory.')
        return
    
    # Create destination if it does not exist
    if not os.path.isdir(dst):
        os.mkdir(dst)

    # Enumerate relative subdirectories to the root of each path
    src_rel_subdirectories = enumerate_relative_subdirectories(src)
    dst_rel_subdirectories = enumerate_relative_subdirectories(dst)

    # Check if the destination already contains the same relative subdirs
    missing = src_rel_subdirectories - dst_rel_subdirectories
    if missing:
        # Source subdirectories are missing from destination
        # Add them.
        for relative_path in missing:
            _path = os.path.join(dst, relative_path) 
            if not os.path.isdir(_path):
                logger.debug('Creating subdirectory at path: [{}]'.format(_path))
                os.mkdir(_path)

    # Once all of the missing subdirectories have been created, copy the files over
    for dirpath, subdirs, files in os.walk(src):
        for _file in files:
            fpath = os.path.join(dirpath, _file)
            rpath = strip_path(fpath, src)
            dpath = os.path.join(dst, rpath)
            logger.debug('fpath: [{}]'.format(fpath))
            logger.debug('rpath: [{}]'.format(rpath))
            logger.debug('dpath: [{}]'.format(dpath))
            logger.info('Copying {} to {} ...'.format(fpath, dpath))
            shutil.copy(fpath, dpath)


def enumerate_files_local(path):
    ''' 
    Build a dictionary for local files containing their name, full path,
    path from the root of the srcdir (e.g. for A/B/C.txt, relative is B/C.txt),
    and the filehash (sha256).

    This information is used to build a picture of the unique files contained and necessary.
    '''
    
    if not os.path.isdir(path):
        logger.error('Provided path [{}] is not a valid directory.'.format(path))
        raise FileNotFound

    file_dict = dict()
    # FIELDS = ['filepath','relpath','sha256']

    for dirpath, subdirs, files in os.walk(path):
        for _file in files:
            fullpath = os.path.join(dirpath, _file)
            relpath = strip_path(fullpath, path)
            sha256 =  get_hash_local(fullpath).hexdigest()
            filename = _file
            file_dict[filename] = dict()
            file_dict[filename]['filepath'] = fullpath
            file_dict[filename]['relpath'] = relpath
            file_dict[filename]['sha256'] = sha256
    
    return file_dict


# Hash function for local files
def get_hash_local(fpath, block_size=65536):
    '''
    based on: https://gist.github.com/rji/b38c7238128edf53a181#file-sha256-py
    vars renamed to support changing the checksum used without being annoying
    '''
    checksum = hashlib.sha256()
    with open(fpath,'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            checksum.update(block)
    return checksum


if __name__ == '__main__':

    pth = os.path.expandvars("$HOME/Documents/Github/docmaster_core/docdaemon/utests/Example1")
    dst = os.path.join(os.path.dirname(os.path.realpath(__file__)),'sample')
    file_list = enumerate_files_local(pth)
    pprint.pprint(file_list)
#    copy_dir(pth, dst)
