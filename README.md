A small program that allows to classify pictures and videos based on their EXIF data into subfolders (Year - Month).

Source and target directories are asked through prompts, and the items are moved to the appropriate location.
Errors are listed dynamically, and a recap printed at the end of the process (sometimes the EXIF data does not contain any timestamp)

A couple methods are used (the second is attempted if the first did not work).

Perl is needed for the first one to be executed, if not present it just defaults to the second.
