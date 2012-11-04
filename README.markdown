
# Overview
This project is a XBMC remote with a webUI.
This remote will quickly index multiple media folders for quick recalling.

# FileTree
When the server is launched, it will scrape through the media folders and create a FIleTree.
This will be a JSON object.

## JSON Format
    {   "name":"/mnt/raid",
        "spath":"smb://192.168.0.200/public",
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

# TODO
* Package code for distribuition
    * etc, usr/shar, ...
* Clean Up Code
* Allow for standalone as well as imported bahavior
* Use more efficient languages
* Keep Track of Movies that have already been viewed
    * will likly need a database stored in /var/
* Dispaly Cover art for movies (look for .tbn)
* Set Maximum number of filted results (25 at a time)
* Remove folders without movies from results
* Remove non-movie files from FileTree
* Add Stop function for XBMC player
* STrip slashed from original path info

# Implementations
1. Python - For Quick Proof-of-Concept coding
2. Go - For performance
3. C/C++ - For efficiency

