import os
import glob
import shutil
import sys
import time
import zipfile
import argparse


EXTENSIONS = [ ".htm", ".html" ]
FOLDER_SUFFIXES = [ "_files" ]


def timeit(f):
    """
    help: [ https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator ]
    :param f:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        print('>>> func:[{}] started @ [{}]'.format(f.__name__, ts))
        result = f(*args, **kw)
        te = time.time()
        print('<<< func:[{}] ended @ [{}]'.format(f.__name__, te))
        print('=== func:[{}] took: [{}]'.format(f.__name__, print_time(te - ts)))
        return result
    return timed


def print_time(time):
    miliseconds = time * 1000 % 1000
    seconds = time % 60
    time /= 60
    minutes = time % 60
    time /= 60
    hours = time % 24
    time /= 24
    days = time
    return "%ddays %.2d:%.2d:%.2d.%.3d" % (days, hours, minutes, seconds, miliseconds)


ILLEGAL_CHARS = [ '\u021b', '\u0159', '\u0102', '\u0103', '\u0219', '\u2103' ]


@timeit
def compress_folders(folders, delete):
    # todo: need to process files such that script guarantees non-nesting of websites archives inside each other - plain archives
    to_remove = []
    excluded_files = []
    for folder in folders:
        print("zipping websites from [%s]" % folder)
        items = list(glob.glob(folder + r"\**", recursive=True))
        for item in items:
            for ext in EXTENSIONS:
                if item not in excluded_files: # note: ugly comparison that slows things down, but avoids bugs related to `glob` dynamic list
                    if ext == "." + item.split(".")[-1]:
                        basename = item.split(ext)[0]
                        basedir = os.sep.join(basename.split(os.sep)[:-1])
                        subitems = [x for x in items if basename in x]

                        for suffix in FOLDER_SUFFIXES:
                            if os.path.exists(basename + suffix):
                                try:
                                    print("found webpage [{}]".format(basename)) # note: if we confirm it is a saved webpage with subfiles
                                except:
                                    illegal = basename
                                    for char in ILLEGAL_CHARS:
                                        illegal = illegal.replace(char, '_')
                                    print("gotcha: [%s]" % illegal)
                                    basename = illegal
                                exceptions = []
                                zipname = basename + suffix + ".zip"
                                if not os.path.exists(zipname):
                                    with zipfile.ZipFile(zipname, 'w') as z:
                                        for f in subitems:
                                            if f != zipname: # note: since glob.glob is dynamic, it reloads the files which causes the newly created zipfile to be found
                                                filename = f.split(basedir)[1].lstrip("\\")
                                                illegal = filename
                                                for char in ILLEGAL_CHARS:
                                                    illegal = illegal.replace(char, "_")
                                                filename = illegal
                                                arcname = filename
                                                try:
                                                    z.write(filename=os.path.join(basedir, filename), arcname=arcname)
                                                    excluded_files += [f]
                                                except Exception as ex:
                                                    # todo: fix error code 3, which potentially appears due to MAX_PATH = 260 limitation in registry
                                                    # help: [ https://novaworks.knowledgeowl.com/help/how-to-fix-error-code-3 ]
                                                    print("Hackers removed file [%s] with exception [%s]" % (os.path.join(basedir, arcname), ex))
                                                    exceptions += [ex]
                                        z.close()
                                    if len(exceptions) == 0:
                                        # remove the base files only if there are no exceptions
                                        to_remove += [ basename + suffix, basename + ext ]

    time.sleep(3) # note: for some reason file does not get closed properly, assuming its due to glob.glob

    # note: because of glob.glob need to do this after all archives are created
    if delete:
        for item in to_remove:
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
            except:
                print("Failed to remove [%s]" % item)


@timeit
def uncompress_archives(folders, delete):
    # help: [ https://stackoverflow.com/questions/3451111/unzipping-files-in-python ]
    to_remove_all = []
    for folder in folders:
        print("unzipping websites from [%s]" % folder)
        for suffix in FOLDER_SUFFIXES:
            items = list(glob.glob(folder + r"\**\**" + suffix + ".zip", recursive=True)) # note: do not unpack all zip files, only ones that were containing websites
            # todo: could peek inside archive and if it has structure of [ {webpage}, {webpage}_files ] then unzip it
            for item in items:
                dirpath = os.path.abspath(os.path.dirname(item))
                try:
                    with zipfile.ZipFile(item, 'r') as z:
                        z.extractall(dirpath)
                    to_remove_all += [item]
                    print("unzipped archive [%s]" % item)
                except:
                    print("encountered exception while unzipping [%s]" % item)

    time.sleep(3)  # note: for some reason file does not get closed properly, assuming its due to glob.glob

    # note: because of glob.glob need to do this after all archives are created
    if delete:
        for f in to_remove_all:
            try:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            except:
                print("Failed to remove [%s]" % f)


def menu():
    parser = argparse.ArgumentParser(description='Compress or decompress saved webpages recursively in one or multiple paths given')

    parser.add_argument('-c', '--compress', default=True, action='store_true', required=False,
                        help='flag indicating if the script should compress saved webpage. This is the default action if no flag is provided.')
    parser.add_argument('-u', '--uncompress', default=False, action='store_true', required=False,
                        help='flag indicating if the script should decompress saved webpages. This will override `-c` flag if provided.')
    parser.add_argument('-d', '--delete', default=False, action='store_true', required=False,
                        help='flag indicating the script should delete the source files after zip archive is finalized without errors. Or should delete zip archive if `-u` flag was provided.')
    parser.add_argument('paths', metavar='paths', nargs='+',
                        help='paths where to search through - list of strings separated by space')
    arguments = parser.parse_args()

    if arguments.uncompress:
        arguments.compress = False

    return arguments


def main():
    """
    Script that will get an input folder and zip [ *.html *.htm ] and corresponding [ *_files ] into [ .zip ] archives
    NOTE: need to prefix files containing UTF-8 filenames with infected, as they could be triggering some latent exploits in [ explorer.exe ] 
    """
    args = menu()

    if args.compress:
        compress_folders(args.paths, args.delete)

    if args.uncompress:
        uncompress_archives(args.paths, args.delete)

    pass  # used for debug breakpoint

if __name__ == "__main__":
    main()

