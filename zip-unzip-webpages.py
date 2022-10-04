import os
import glob
import shutil
import sys
import time
import zipfile
import argparse


EXTENSIONS = [ ".htm", ".html" ]
FOLDER_SUFFIXES = [ "_files" ]


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
                                print("found webpage [%s]" % basename) # note: if we confirm it is a saved webpage with subfiles
                                to_remove = []
                                zipname = basename + suffix + ".zip"
                                with zipfile.ZipFile(zipname, 'w') as z:
                                    for f in subitems:
                                        if f != zipname: # note: since glob.glob is dynamic, it reloads the files which causes the newly created zipfile to be found
                                            arcname = f.split(basedir)[1].lstrip("\\")
                                            try:
                                                z.write(filename=os.path.join(basedir, arcname), arcname=arcname)
                                                excluded_files += [f]
                                            except Exception as ex:
                                                print("Hackers removed file [%s] with exception [%s]" % (os.path.join(folder, arcname), ex))
                                    z.close()

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


def uncompress_archives(folders, delete):
    # help: [ https://stackoverflow.com/questions/3451111/unzipping-files-in-python ]
    to_remove_all = []
    for folder in folders:
        print("unzipping websites from [%s]" % folder)
        for suffix in FOLDER_SUFFIXES:
            items = list(glob.glob(folder + r"\**" + suffix + ".zip", recursive=True)) # note: do not unpack all zip files, only ones that were containing websites
            # todo: could peek inside archive and if it has structure of [ {webpage}, {webpage}_files ] then unzip it
            for item in items:
                dirpath = os.path.abspath(os.path.dirname(item))
                with zipfile.ZipFile(item, 'r') as z:
                    z.extractall(dirpath)
                    z.close()
                    to_remove_all += [item]
                print("unzipped archive [%s]" % item)

    time.sleep(3)  # note: for some reason file does not get closed properly, assuming its due to glob.glob

    # note: because of glob.glob need to do this after all archives are created
    if delete:
        # for to_remove in to_remove_all:
        if len(to_remove_all) > 0:
            reversed_list = list(reversed(to_remove_all))
            for f in reversed_list:
                # for i in range(len(to_remove, 0, -1)):
                # note: reverse the list and start removing items from the end
                # note: avoiding `if os.path.isfile` in order to speed up removal, since most items will be files and not folders
                try:
                    os.remove(f)
                    # print("Failed to remove [%s] with exception [%s]" % (f, ex1))
                except:
                    print("Failed to remove [%s]" % f)
                    try:
                        os.rmdir(f)
                    # except Exception as ex2:
                    #     print("Failed to remove [%s] with exception [%s]" % (f, ex2))
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

