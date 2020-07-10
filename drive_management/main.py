from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Authentication 
# Needs to be tweaked, currently unclear how credentials are saved and how long they last
# Seems to ask to reauthenticate after a short time period


gauth = GoogleAuth()
#gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
#gauth.SaveCredentialsFile("mycreds.txt")
gauth.LoadCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)


# Methods for various API Calls

# queries ENTIRE Drive (shared and personal) for filename, downloads into specified filepath
# potential conflict if multiple files have same filename 
def downloadFile(file_name):
  file_list = drive.ListFile({'q':"title = '{}' and trashed=false".format(file_name)}).GetList()
  download_path = input("Enter the file path for the download location: ")
  for file1 in file_list:
    if file1['title'] == file_name:
      file2 = drive.CreateFile({'id': file1['id']})
      print('Downloading file %s from Google Drive' % file2['title']) 
      full_path = download_path + "/" + file_name
      file2.GetContentFile(full_path)  # Save Drive file as a local file


# searches folder by name and returns folder ID
def getFolderID(folder_name):
  file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
  for files in file_list:
    if files['title'] == folder_name:
      return files['id']


# displays all files and folders in "Shared with Me"
def showShared():
  print("Showing 'Shared with Me' Folders and Files")
  file_list = drive.ListFile({'q': "sharedWithMe"}).GetList()
  for files in file_list:
      print('title: %s, id: %s' % (files['title'], files['id']))


# displays all files and folders, shared and personal
def showMyDrive():
  print("Showing All Folders and Files (excluding trash)")
  file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
  for files in file_list:
    print(files['title'], files['id'])

# prints contents of folder by folder name
def folderNav(folder_name):
  folder_id = getFolderID(folder_name)
  file_list = drive.ListFile({'q': "'{}' in parents".format(folder_id)}).GetList()
  for files in file_list:
    print('title: %s, id: %s' % (files['title'], files['id']))

# returns contents inside a given folder, query uses folderID
def getFolderContents(folder):
  folder_id = getFolderID(folder)
  file_list = drive.ListFile({'q': "'{}' in parents".format(folder_id)}).GetList()
  return file_list

# helper function for file navigation
def navHelper(parent, child):
  for i in parent:
    if i['title'] == child:
      return True
  return False

# prints the content of a given file path
def filePathNav(file_path):
  folder_list = file_path.split("/")
  if(len(folder_list) == 1): # if only only folder is queried 
    res = getFolderContents(folder_list[0])
    for files in res:
      print('title: %s, id: %s' % (files['title'], files['id']))
    return
  i = 0     
  while(i < len(folder_list) - 1):
    parent = getFolderContents(folder_list[i])
    isChild = navHelper(parent, folder_list[i+1])
    if(isChild == True):
      i+=1
    else: # folder does not exist in parent
      print("folder not found")
      return
  if(isChild == True):
    res = getFolderContents(folder_list[i])
    for files in res:
      print('title: %s, id: %s' % (files['title'], files['id']))


# test cases
def navTest():
  path = input("Enter a file path to navigate to: ")
  filePathNav(path)

def downloadTest():
  file_name = input("Enter filename to be downloaded: ")
  downloadFile(file_name)


navTest()
#downloadTest()


# ISSUES TO BE FIXED:
#  - identical folder/file names create conflict
#  - potential fix is to nav folder and download using file id
#  - authentication credentials are temporary, eventually asks the user to login to google everytime script is run

# Potential Fix
# - save most recent file path queued as a global,
# - restrict the scope of downloadFile to only query within the current directory
# - this avoids conflict of file and folders with same name
