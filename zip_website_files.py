import os
import glob
import sys
import time
import zipfile

def iterate_folder(folder):
    extensions = [ ".htm", ".html" ]

    print("zipping websites from [ %s ]" % folder)

    if folder == "":
        sys.exit()

    listdir = []
    if os.path.isdir(folder):
        listdir = os.listdir(folder)

    # [ [ print(i) for j in extensions if j in i ]  for i in listdir ]

    listglob = glob.glob(folder+r"\**",recursive=True)

    to_remove = []
    for item in listdir:
        for ext in extensions:
            if ext in item:
                files = []
                for file in listglob:
                    basename = item.split(ext)[0]
                    if basename in file:
                        files += [file]
                # [ print(f) for f in files ]
                with zipfile.ZipFile(os.path.join(folder, basename + ".zip"), 'w') as z:
                    for f in files:
                        arcname = f.split(folder)[1].lstrip("\\")
                        try:
                            z.write(filename=os.path.join(folder,arcname),
                                    arcname=arcname)
                        except:
                            print("Hackers removed file [ %s ]" % os.path.join(folder, arcname))

                for f in reversed(files):
                    file = os.path.join(folder, f)
                    to_remove += [ file ]

    for f in to_remove:
        try:
            os.remove(f)
        except:
            try:
                os.rmdir(f)
            except:
                pass
            print("Failed to remove [ %s ]" % f)


if __name__ == "__main__":
    """
    Script that will get an input folder and zip [ .html .htm ] and corresponding [ _files ] into [ .zip ] archives
    
    NOTE: need to prefix files containing UTF-8 filenames with infected, as they could be triggering some latent exploits in [ explorer.exe ] 
    """
    folder = sys.argv[1]
    folders = [ os.path.join(folder,f) if os.path.isdir(os.path.join(folder,f)) else "" for f in os.listdir(folder) ]
    folders = [ f for f in folders if f ] # NOTE: why the fuck folders.remove("") does not work anymore ?
    # print(folders)
    for f in folders:
        iterate_folder(f)
