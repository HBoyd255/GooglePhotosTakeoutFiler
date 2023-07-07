# Google Photos Takeout Filer

This program organizes your photos from a Google Photos takeout export and
arranges them into east to navigate folders 

To achieve this it:
* Extracts the capture date from each photo's accompanying JSON file and
applies it to the modified date of the photo.
* Renames each photo to better reflect the capture date.
* Sorts each photo into a folder based on the month that it was captured.

## To-do
- [X] Correctly extract date taken for each photo
- [ ] Deal with the 1% of photos that are badly labeled by takeout
- [ ] Move photos into folders based on month
- [X] Rename photos based on date captured
- [ ] Sort code into modules
- [ ] Write Docstrings for all functions

## Bugs to fix
- [ ] duplicate files are getting listed as file(1)(2).png, not just file(2).png







