#!/usr/bin/env python

import os, socket, json, random, hashlib
from urlparse import parse_qs
from cgi import escape
from urllib import unquote
from wsgiref.simple_server import make_server

def start_server():
    r = remote( {"bedroom":"192.168.0.210","familyroom":"192.168.0.211"}, # Dict of Frontends and IPs
                ["TV","Movies/Features"], # List of folders
                {"fpath":"/mnt/raid","spath":"smb://192.168.0.200/public"}) # Samba to Filesystem comparison
    # Start WSGI
    httpd = make_server("",8000,r.process_request)
    print "Serving on port 8000"
    httpd.serve_forever()

class remote():
    def __init__(self,  fes, # List of frontends 
                        folders, # List of folders
                        smbinfo): # dictionary of Samba Path Info
        # A list of valid Frontends.  Each frontend is a dictionary with IP and Name
        self.FrontEnds = fes
        # Load a FileTree in memory containing all of the filesystem info
        # TODO Strip Slashes
        self.uniqueint = 0

        self.FileTree = {   "name":smbinfo["fpath"],
                            "spath":smbinfo["spath"],
                            "children":[]}    

        for f in folders:
            self.FileTree["children"].append({"name":f,"children":[],"parent":self.FileTree,"uid":self.uid()})
        # Parse the folders and populate the FileTree
        self.refresh_file_tree()
        self.add_uids()

    ############
    ## FileTree Methods
    ###########

    # Browse the file system and arange media files in a tree
    def refresh_file_tree(self):
        self.scan_folders(self.FileTree["children"])


    # Recursive Helper Function for refreshing the FileTree
    def scan_folders(self,fs): # List of files/Folders
        # For each file/folder
        for f in fs:
            # If directory
            fpath = self.get_fpath(f)
            if os.path.isdir(fpath):
                # Add all file to the "children" list and recursivly scan those children
                for c in sorted(os.listdir(fpath)):
                    f["children"].append({"name":c,"children":[],"parent":f,"uid":self.uid()})

            self.scan_folders(f["children"])

    def add_uids(self,f=None):
        if f == None:
            f = self.FileTree
        f["uid"] = hashlib.sha1(self.get_spath(f)).hexdigest()
        for c in f["children"]:
            self.add_uids(c)
    
    # Creates filesystem path for given file/folder object from FileTree
    def get_fpath(self,f):
        fpath = f["name"]
        while "parent" in f:
            # Move up a level
            f = f["parent"]
            # Ad to path
            fpath = f["name"]+"/"+fpath

        return fpath

    # Creates Samba path for give file/forlder object from FileTree 
    def get_spath(self,f):
        spath = f["name"]
        while "parent" in f:
            # Move up a level
            f = f["parent"]
            # Add to path
            if "spath" in f:
                spath = f["spath"]+"/"+spath
            else:
                spath = f["name"]+"/"+spath

        return spath

    # Search Tree or a String
    def search(self,q):
        ms = []
        self.search_req(ms,q,self.FileTree)
        return ms

    def search_req(self,ms, # List of matching file/folder objects
                        q,  # Search Query
                        f): # Current File/Folder Object
        if self.matches(q,f["name"]):
            ms.append(f)
        else:
            for c in f["children"]:
                self.search_req(ms,q,c)

    def search_uid(self,uid,f=None):
        if f == None:
            f = self.FileTree
        if f["uid"] == uid:
            return f
        else:
            for c in f["children"]:
                m = self.search_uid(uid,c)
                if m != None:
                    return m
                    
            
        
    def matches(self,   q, # Search QUery
                        fname): # File/folder name
        if q == "" or q == "*":
            return True
        elif fname.lower().find(q.lower()) != -1 :
            return True
        else:
            return False

    def print_tree(self,fs,ind = 0):
        for f in fs:
            print ("  "*ind)+f["name"]
            self.print_tree(f["children"],ind+1)

    def uid(self):
        self.uniqueint += 1
        return str(self.uniqueint)
            


    ###############
    ## JSON-RPC Methods
    ################

    # Send a json object to the frontend using TCP communication
    def send_json(self,js,f):

        # Get IP from f
        ip = f

        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((ip,9090))

        for j in js:
            s.send(json.dumps(j))
            print s.recv(1024)
        s.close()
        return 0

    ## For testing
    def test_cmd(self):
        self.send_json([self.clear_playlist(),self.add_item(),self.start_playlist()],"192.168.0.210")

    # Adds an item to the playlist
    def add_item(self,spath):# Complete Samba Path
        j = self.blank_json()
        j["method"] = "Playlist.Add"
        j["params"] = {"playlistid":1}
        j["params"]["item"] = {"file":spath}
        return j

    # Clears the playlist
    def clear_playlist(self):
        j = self.blank_json()
        j["method"] = "Playlist.Clear"
        j["params"] = {"playlistid":1}
        return j

    # Starts the playlist
    def start_playlist(self):
        j = self.blank_json()
        j["method"] = "Player.Open"
        j["params"] = [{"playlistid":1}]
        return j

    ## TODO Add method that stops active players

    # Creates a blank JSON Request
    def blank_json(self):
        return {"jsonrpc":"2.0", "id":1}

    # Selects a random friends episode and plays the next 4 episodes
    def play_group(self,f,  # Folder Object
                        feip, # FrontEnd IP
                        numeps): # Number of Eps
        numeps = int(numeps)
        # Selects the first match for the Query
        # Get total number of episodes
        totaleps = len(f["children"])
        if totaleps < numeps:
            numeps = totaleps
        # Select a random episode

        index = random.randint(0,totaleps-numeps)
        # JSON Requests
        js = []
        js.append(self.clear_playlist())
        for i in range(index,index+numeps):
            js.append(self.add_item(self.get_spath(f["children"][i])))
        js.append(self.start_playlist())
        
        self.send_json(js,feip)
        
    def play_single(self, f,feip):
        # JS Requests
        js = []
        js.append(self.clear_playlist())
        js.append(self.add_item(self.get_spath(f)))
        js.append(self.start_playlist())

        self.send_json(js,feip)

    #############
    ## HTTP Methods
    #############

    # Converts tree to HTML text so it looks nice.
    def tree_to_html(self, tree):
        pass

    # Process the HTTP Request
    def process_request(self,e,s):
        # Set Type as HTML

        wholepath = e.get("PATH_INFO",'').lstrip("/").rstrip("/")
        path = wholepath.split("/")[0]


        output = ""
        if path=="":
            output = self.main_page_req()
        elif path == "list":
            output = self.list_req(e)
        elif path == "cmd":
            output = self.cmd_req(e)
        else: 
            output = "Invalid Path"

        s('200 OK', [('Content-Type', 'text/html; charset=ISO-8859-1')])
        return [output]

    # Prints main HTML page.  The environment variable is not passed since its not needed
    def main_page_req(self):
        # Open HTML file
        f = open("main.html","r")
        data = f.read()
        f.close()
        return data

    def list_req(self,e):
        # Parse GET/POST data for filter query
        d = self.get_dict(e)
        # Create q entry if not present
        if "q" not in d:
            d["q"] = ""
        # Filter Tree
        results = self.search(d["q"])
        # Convert to HTML and return
        return self.tree_to_html(results)

    def cmd_req(self,e):
        # Parse GET/POST data
        d = self.get_dict(e)

        # Find Object based on UID
        f = self.search_uid(d["uid"])
        fe = self.FrontEnds[d["room"]]
        # Check if a single file was selected
        if len(f["children"]) == 0 :
            self.play_single(f,fe)
        else:
            numeps = d["numeps"]
            self.play_group(f,fe,numeps)

        #self.send_json(j,f)
        return "Command Sent" # Otherwise return error

    def get_dict(self,e):
        d = parse_qs(e["QUERY_STRING"])
        fix_d = {}
        for key in d:
            fix_d[key] = escape(unquote(d[key][0]))
        return fix_d

    def tree_to_html(self,fs):
        output = ""
        for f in fs:
            output += "<div class=\"result\" >"
            # If a file (no children)
            output += "<a href=\"#\" class=\"item\" uid=\""+f["uid"]+"\"  >" 
            output += f["name"]
            output += "</a>"
            output += self.tree_to_html(f["children"])
            output += "</div>"
        return output

### Start Server Call
if __name__ == "__main__":
    start_server()

