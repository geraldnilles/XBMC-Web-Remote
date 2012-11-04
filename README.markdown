
# Overview
This project is a XBMC remote with a webUI.
This remote will quickly index multiple media folders for quick recalling.

# FileTree
When the server is launched, it will scrape through the media folders and create a FIleTree.
This will be a JSON object.

## JSON Format
    {   "name":"/mnt/raid/",
        "children":[
            {   "name":"Movies",
                "children":[
                    {   "name":"Zoolander.mkv",
                        "children":[]
                    }
                ]
            },
            {   "name":"TV",
                "children":[]
            }
        ]
    }

# Type of Program
This program will be a service started and stopped using the "sudo service ... start/stop/restart" command.
I need to figure out how to do that. 


# Implementations
1. Python - For Quick Proof-of-Concept coding
2. Go - For performance
3. C/C++ - For efficiency

