#!/bin/python
import dropbox
import os

apikey = "<YOURAPIKEY>"

dropbox_dir = "/somefiles/"
local_dir = "/home/mebus/dropbox_mirror/"


class Dropget:

    def __init__(self):

        self.client = dropbox.client.DropboxClient(apikey)
        self.usermeta = self.client.account_info()

        print "Account-Info: "+self.usermeta['display_name'] + ", " + self.usermeta['email'] + "\n"
    
    def make_folder_savepath(self, base_path, rel_path):
        return  os.path.join(base_path, rel_path.lower()[1:])

    def download_folder(self, path, outpath):

        self.outpath = outpath

        if not os.path.isdir(self.outpath):
            print "\nOutput directory does not exist! Exiting."
            return

        folder_meta = self.client.metadata(path)

        #make the start folder
        savepath = self.make_folder_savepath(self.outpath, folder_meta['path'])
        
        if not os.path.isdir(savepath) and not os.path.isfile(savepath):
                    print "MKDIR: " + savepath
                    os.makedirs(savepath)
        
        # start recursion

        print "\nmaking directory structure\n------------------------\n"
        self.recur_dir(folder_meta);

        print "\ndownloading files\n--------------------\n"
        self.recur_files(folder_meta);

        print "FINISHED."

    def recur_dir(self, folder_meta):
        # make directory structure

        for a in folder_meta['contents']:

            savepath = self.make_folder_savepath(self.outpath, a['path'])

            if a['is_dir']:

                if not os.path.isdir(savepath) and not os.path.isfile(savepath):
                    print "MKDIR: " + savepath
                    os.makedirs(savepath)
                else: 
                    print "ALREADY EXISTS: "+savepath

                # subfolders
                folder_meta_sub = self.client.metadata(a['path'])
                self.recur_dir(folder_meta_sub)

    def recur_files(self, folder_meta):
        #download the files

        for a in folder_meta['contents']:

            savepath = self.make_folder_savepath(self.outpath, a['path'])

            if a['is_dir']:

                folder_meta_sub = self.client.metadata(a['path'])
                self.recur_files(folder_meta_sub)

            else:

                # gef file

                if (not os.path.isdir(savepath)) and (not os.path.isfile(savepath)):
                    print "SAVE: " + savepath
                    f = self.client.get_file(a['path'])

                    # save the output
                    out = open(savepath, 'wb')
                    out.write(f.read())
                    out.close()

                else:
                    print "ALREADY EXISTS: " + savepath


if __name__ == '__main__':
   
    dropget = Dropget()
    dropget.download_folder(dropbox_dir, local_dir)
