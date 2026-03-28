# exportsnapmemories
Updated Python Script To Merge Tag and Organize Snapchat Export (Uses Folders From Zip)
NEW Stich.py a script you should run before the main script. Run it on your entire large memories folder and it will stich together the videos that need to be. (Run it 2-3 times because it misses some sometimes)

Just a simple python script that I remade into one single script that merges tags and deletes old overlays and organizes into Month (Year) folders.
Script came from https://github.com/annsopirate/snapchat-memories-organizer
Since I was having so many issues using the json file all of the links were not working so I found this script and did some edits. It works 98% of the time out of 4800 files about 20 didnt merge. Ill Take it.
Please make a master backup in case you notice things are gone.

Requirements:

FFMPEG INSTALLED Download the windows file from (https://www.ffmpeg.org/download.html) and then do the same thing as the EXIFTOOL below make a path var etc.

EXIFTOOL INSTALLED (https://www.youtube.com/watch?v=Ku1Nx-kl7RM)

Make sure both above are set as a path in windows since that is what is it going to look for.

PYTHON INSTALLED, Easy way open cmd type python and then enter, windows store should open and have you download that one. If not google it.


How to use Script

1. Download your snapchat data, should be all zip folders.
2. Take the memories folder from each zip folder and extract and merge them all into one giant memories folder. You should have just one memories folder that has all your .jpg and .png, Overwrite memories.html you dont need it
3. Take the script and put it in the root folder next to the memories folder, open it and change the folder location to the memories folder location
4. Change simulation to FALSE after you ran it to actually make any file changes.
5. Upload new folders where you want.
6. DONE

Will set the metadata data from the file name so wherever you upload it,  will have the correct day just not the time.
