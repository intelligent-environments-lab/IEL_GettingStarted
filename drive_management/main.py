from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

glob_file_path = "root"
current_folder_id = "null"

# Methods for various API Calls

def authenticate_drive(file_name=None,verbose=True):
	'''
	Authenticates user and returns GoogleDrive instance.\\ 
	If credentials file exists and is unexpired, it is used to authenticate otherwise, 
	user is prompted with a Google authentication webpage for new credentials.  
	Parameters
	----------
	file_name : str, absolute file path of user credentials.
	Returns
	-------
	GoogleDrive.
	'''
	gauth = GoogleAuth()
	updated_credentials = False

	try:
		assert file_name != None
	except AssertionError as e:
		file_name = "mycreds.txt"

	# Try to load saved client credentials
	gauth.LoadCredentialsFile(file_name)
	if gauth.credentials is None:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
			updated_credentials = True
	elif gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
			updated_credentials = True
	else:
			# Initialize the saved creds
			gauth.Authorize()
	
	# Save the current credentials to a file
	gauth.SaveCredentialsFile(file_name)
	if verbose:
		print("Credentials saved to "+file_name)
	else:
		pass

	drive = GoogleDrive(gauth)
	return drive

def download_file(file_name=None,drive=None):
	'''
	Queries entire Drive (shared and personal) for file name and downloads into specified file path.\\
	NOTE: Potential conflict if multiple files have same file name. 
	Parameters
	----------
	file_name : str, title of file to download.
	drive : GoogleDrive
	Returns
	-------
	None
	'''
	file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(current_folder_id)}).GetList()
	download_path = input("Enter the file path for the download location: ")
	for file1 in file_list:
		if file1['title'] == file_name:
			file2 = drive.CreateFile({'id': file1['id']})
			print('Downloading file %s from Google Drive' % file2['title']) 
			full_path = download_path + "/" + file_name
			file2.GetContentFile(full_path)  # Save Drive file as a local file

def get_folder_id(folder=None,drive=None):
	'''
	Searches folder by name and returns folder ID.
	Parameters
	----------
	folder : str, title of folder to download.
	drive : GoogleDrive
	Returns
	-------
	str
	'''
	file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
	for files in file_list:
		if files['title'] == folder:
			return files['id']

def get_folder_contents(folder=None,drive=None):
	'''
	Returns contents inside a given folder, query uses folderID.
	Parameters
	----------
	folder : str, name of folder to download.
	drive : GoogleDrive
	Returns
	-------
	list
	'''
	folder_id = get_folder_id(folder=folder,drive=drive)
	file_list = drive.ListFile({'q': "'{}' in parents".format(folder_id)}).GetList()
	return file_list

def nav_helper(parent=None,child=None):
	'''
	Helper function for file navigation.
	Parameters
	----------
	parent : unknown
	child : unknown
	Returns
	-------
	bool
	'''
	for i in parent:
		if i['title'] == child:
			return True
	return False

def file_path_nav(file_path=None,drive=None):
	'''
	Prints the content of a given file path.
	Parameters
	----------
	parent : unknown
	child : unknown
	Returns
	-------
	None
	'''
	folder_list = file_path.split("/")
	if(len(folder_list) == 1): # if only only folder is queried 
		res = get_folder_contents(folder=folder_list[0],drive=drive)
		for files in res:
			print('title: %s, id: %s' % (files['title'], files['id']))
		return
	i = 0     
	while(i < len(folder_list) - 1):
		parent = get_folder_contents(folder=folder_list[i],drive=drive)
		isChild = nav_helper(parent, folder_list[i+1])
		if(isChild == True):
			i+=1
		else: # folder does not exist in parent
			print("folder not found")
			return
	if(isChild == True):
		res = get_folder_contents(folder=folder_list[i],drive=drive)
		global current_folder_id
		global glob_file_path
		glob_file_path = file_path
		current_folder_id = get_folder_id(folder=folder_list[i],drive=drive)
		for files in res:
			print(file_path + '/%s, id: %s' % (files['title'], files['id']))

def main():
	'''
	Provides interface for file download.\\
	Called when script is executed from Terminal.
	Parameters
	----------
	None
	Returns
	-------
	None
	'''
	drive = authenticate_drive()

	file_path = input("Enter a file path to navigate to: ")
	file_path_nav(file_path=file_path,drive=drive)

	file_name = input("Enter file name to be downloaded: ")
	download_file(file_name=file_name,drive=drive)
	#print(glob_file_path)
		
if __name__ == "__main__":
	main()

# ISSUES TO BE FIXED:
#  - identical folder/file names create conflict
#  - potential fix is to nav folder and download using file id
#  - authentication credentials are temporary, eventually asks the user to login to google everytime script is run

# Potential Fix
# - save most recent file path queued as a global,
# - restrict the scope of downloadFile to only query within the current directory
# - this avoids conflict of file and folders with same name



# displays all files and folders in "Shared with Me"
# def showShared():
#   print("Showing 'Shared with Me' Folders and Files")
#   file_list = drive.ListFile({'q': "sharedWithMe"}).GetList()
#   for files in file_list:
#       print('title: %s, id: %s' % (files['title'], files['id']))


# # displays all files and folders, shared and personal
# def showMyDrive():
#   print("Showing All Folders and Files (excluding trash)")
#   file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
#   for files in file_list:
#     print(files['title'], files['id'])

# # prints contents of folder by folder name
# def folderNav(folder):
#   folder_id = getFolderID(folder)
#   file_list = drive.ListFile({'q': "'{}' in parents".format(folder_id)}).GetList()
#   for files in file_list:
#     print('title: %s, id: %s' % (files['title'], files['id']))
