#!/usr/bin/python3

#Python3 modules to install with pip3: Pillow, exifread

from datetime import datetime
from os import makedirs, path, walk, remove
from shutil import move
from subprocess import Popen, PIPE
from time import sleep
import PIL.Image
import exifread
from hashlib import md5
import logging

logging.basicConfig(filename='error.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S :', level=logging.WARNING)

try:
	p = Popen(['perl', '-v'])
	perl = 1
	p.terminate()
except:
	perl = 0
	logging.warning("Perl is not installed, will not try with Exiftool if other methods do not work.")
	print("\nPerl is not installed, will not try with Exiftool if other methods do not work.")
	sleep(2)
	pass

original_folder = input("\nSource directory?\n\n")
while not path.exists(original_folder):
	original_folder = input("\nThis folder does not exist.\nPlease enter a valid path, e.g.: C:/Documents/Mes Photos or /media/disk/pictures.\n\n")

target_folder = input("\nTarget directory?\nIt can be an existing directory. Nothing will be overwritten or deleted unless the file exists already. Write permissions are necessary.\n\n")

while not path.exists(target_folder):
	if input("\nNo such directory. Create it? (Y/N, or Ctrl + C to exit)\n\n").lower() == "y":
		try:
			makedirs(target_folder)
		except Exception as e:
			print("\nGot an error: " +str(e) + "\nPlease check the path and filesystem permissions and retry.\n\n")
			pass
	else:
		target_folder = input("\nTarget directory?\n\n")


print("\nWorking.\nIt may take a while.\nIf any errors are encountered, they will be displayed at the end.\n\n")
sleep(2)

dirsNumber = 0
filesNumber = 0

for root, dirs, files in walk(original_folder):

	for d in dirs:
		dirsNumber += 1
	for f in files:
		filesNumber += 1

print("\nThe source directory contains {0} folders and {1} files.\n".format(dirsNumber, filesNumber))

for root, dirs, files in walk(original_folder):

	for f in files:
		try:
			date = datetime.strptime(str(exifread.process_file(open(path.join(root, f), 'rb')).get('EXIF DateTimeOriginal')),"%Y:%m:%d %H:%M:%S").date().strftime("%Y-%m")
		except:
			try:
				date = datetime.strptime(PIL.Image.open(path.join(root, f))._getexif()[36867], "%Y:%m:%d %H:%M:%S").date().strftime("%Y-%m")
			except Exception as e:
				if perl == 1:
					try:
						date = datetime.strptime(Popen(["perl", "-w", "exiftool", "-createDate", path.join(root, f)], stderr=PIPE,
                                           stdout=PIPE).communicate()[0].decode('utf-8')[34:44],
                                     "%Y:%m:%d").date().strftime("%Y-%m")
					except Exception as e:
						logging.error(path.join(root, f) + ": Couldn't retrieve the date. Original error is: " + str(e))
						pass

				else:
					logging.error(path.join(root, f) + ": Couldn't retrieve the date. Original error is: " + str(e))
					pass

		if 'date' in locals():
				if not path.exists(path.join(target_folder, date)):
					try:
						makedirs(path.join(target_folder, date))
					#print(path.join(root, f), date)
					except Exception as e:
						print("Couldn't create the directory in the target folder.\nPlease check that you have write permissions.\n\nExiting.\n")
						exit(1)

				try:
					move(path.join(root, f), path.join(target_folder, date))

				except Exception as e:
					if 'already exists' in str(e):
						try:
							if md5(open(path.join(root, f), 'rb').read()).hexdigest() == md5(open(path.join(target_folder, date, f), 'rb').read()).hexdigest():
								remove(path.join(root, f))
							else:
								move(path.join(root, f, '-2'), path.join(target_folder, date))
						except Exception as e:
							print("Couldn't move the file to the target folder.\nPlease check that you have write permissions.\n\nExiting.\n")
							exit(1)

print("\nHere is a list of the errors encountered, if any (typically, the creation date isn't present in the EXIF data.\nThe concerned files have not been moved.\n\n")
sleep(2)
print(open('error.log', 'r').read())

filesNumber = 0
for root, dirs, files in walk(original_folder):
	for f in files:
		filesNumber += 1
print("\n\n{0} files remain in the source directory.\n".format(filesNumber))

exit(0)
