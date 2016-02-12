#!/bin/python

"""
Dropget - simple script to download files from dropbox
Copyright (C) 2016 by Mebus

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import dropbox
import os
import hashlib
import json
import gzip

apikey = "<YourAPIKey>"

dropbox_dir = "/somefiles/"
local_dir = "/home/mebus/dropbox_mirror/"

revision_file = "revisions.json.gz"


class Dropget:

    def __init__(self):

        self.client = dropbox.client.DropboxClient(apikey)
        self.usermeta = self.client.account_info()

        print "Account-Info: "+self.usermeta['display_name'] + ", " + self.usermeta['email'] + "\n"

    
    def make_folder_savepath(self, base_path, rel_path):
        return  os.path.join(base_path, rel_path.lower()[1:])

    def download_folder(self, path, outpath):


        #revision house keeping
        self.hash = hashlib.sha1()
        self.revisionlist = {}

        if os.path.isfile(revision_file):

            print "Reading revisions from file"

            with gzip.open(revision_file, 'r') as content_file:
                    jsoncont = content_file.read()

            self.revisionlist = json.loads(jsoncont)

        else:
            print "Revision file not found."

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

        #save the revisionlist
        jsoncont =  json.dumps(self.revisionlist)
        
        out = gzip.open(revision_file, 'wb')
        out.write(jsoncont)
        out.close()

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

                self.hash.update(savepath.encode('utf-8'))
                local_path_hash = self.hash.hexdigest()


                # don't download empty files
                if a['size'] == "0 bytes":
                    print "EMTPY FILE: " + savepath

                else:


                    if (not os.path.isdir(savepath)) and (not os.path.isfile(savepath)):
                        print "SAVE: " + savepath + ", SIZE: " + a['size'] 
                        
                        self.save_file(a['path'], savepath)

                    else:

                        print "ALREADY EXISTS: " + savepath

                    
                        if local_path_hash in self.revisionlist:
                            
                            if a['revision'] > self.revisionlist[local_path_hash]:
                                print "SAVE NEW VERSION:" + savepath + ", SIZE: " + a['size']
                                self.save_file(a['path'], savepath)

                    # update digest
                    self.revisionlist[local_path_hash] = a['revision']

    def save_file(self, path, savepath):
        f = self.client.get_file(path)
    
        # save the output
        out = open(savepath, 'wb')
        out.write(f.read())
        out.close()



if __name__ == '__main__':
   
    dropget = Dropget()
    dropget.download_folder(dropbox_dir, local_dir)
