# Import Libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging
from copy import deepcopy

# Constants & Variables
OWNER = 'nweye@utexas.edu'
ROOT_ID = 'sharedWithMe'
METADATA_FIELDS = ['title','modifiedDate','fileSize']
DEFAULT_CREDENTIALS_FILENAME = 'credentials.txt'
VERBOSE = False
DEFAULT_DOWNLOAD_DIRECTORY = '../downloads/'
PARAM_DICT = {
	'q': f"{ROOT_ID} and '{OWNER}' in owners and trashed=false",
	'includeTeamDriveItems': True,
	'supportsTeamDrives': True	
}

# Functions
def authenticate_drive(file_name=None,verbose=VERBOSE):
	'''
	Description
	----------
	Authenticates user and returns GoogleDrive instance.\\ 
	If credentials file exists and is unexpired, it is used to authenticate otherwise,\\
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
		file_name = DEFAULT_CREDENTIALS_FILENAME
	# Try to load saved client credentials
	try:
		gauth.LoadCredentialsFile(file_name)
		if gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
			updated_credentials = True
		else:
			# Initialize the saved creds
			gauth.Authorize()
	except:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
			updated_credentials = True
	# Save the current credentials to a file
	gauth.SaveCredentialsFile(file_name)
	if verbose and updated_credentials:
		print(f'Credentials saved to {file_name}')
	else:
		pass

	drive = GoogleDrive(gauth)
	return drive

def get_drive_file_list(param_dict=PARAM_DICT,drive=None,verbose=VERBOSE):
	'''
	Description
	----------
	Returns list of GoogleDriveFile instances that satisfy query in parameter dict.
	Parameters
	----------
	param_dict : dict, parameters to be satified by query\\
	drive : GoogleDrive, authenticated GoogleDrive instance\\
	verbose : bool, execution of print statements
	Returns
	-------
	list, contains GoogleDriveFile instances
	'''
	file_list = []
	try:
		file_list = drive.ListFile(param_dict).GetList()
	except Exception as e:
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
	
	return file_list

def get_drive_file_id_list(file_path=None,drive=None,root_id=ROOT_ID,owner=OWNER,verbose=VERBOSE):
	'''
	Description
	-----------
	Returns list of file IDs that map to the file path.
	Parameters
	----------
	file_path : str, absolute path to GoogleDriveFile\\
	drive : GoogleDrive, authenticated GoogleDrive instance\\
	root_id : str, file ID of root folder\\
	owner : str, owner of root folder\\
	verbose : bool, execution of print statements
	Returns
	-------
	list, contains GoogleDriveFile IDs
	'''
	title_list = file_path.split('/')
	file_id_list = []
	
	for i in range(len(title_list)):
		# Get query string
		if i == 0:
			q = f"{root_id} and title='{title_list[i]}' and '{owner}' in owners and trashed=false"
		else:
			q = f"'{file_id_list[-1]}' in parents and title='{title_list[i]}' and '{owner}' in owners and trashed=false"
		
		# Run query
		try:
			param_dict = {
				'q': q,
				'includeTeamDriveItems': True,
				'supportsTeamDrives': True
			}
			file_list = get_drive_file_list(param_dict=param_dict,drive=drive,verbose=verbose)
			assert len(file_list) == 1
			file_id_list.append(file_list[0]['id'])
		
		except AssertionError as e:
			if verbose:
				print(f'{"/".join(title_list[0:i+1])} not found in Drive or multiple match found.')
			else:
				pass
			logging.error(e)
			print(type(e).__name__ + ': ' + str(e))
			file_id_list = []
			break

		except Exception as e:
			logging.error(e)
			print(type(e).__name__ + ': ' + str(e))
			file_id_list = []
			break
	
	return file_id_list

def download(file_id=None,file_path=None,download_filename=None,download_directory='',drive=None,root_id=ROOT_ID,owner=OWNER,verbose=VERBOSE):
	'''
	Description
	-----------
	Downloads file in Google Drive to local drive.
	Parameters
	----------
	file_id : str, file ID of target GoogleDriveFile. Takes priority over file_path.\\
	file_path : str, absolute path to GoogleDriveFile. Ignored if file_id is parsed.\\
	download_filename : str, name to use for downloaded file.\\
	download_directory : str, absolute or relative path to download directory.\\
	drive : GoogleDrive, authenticated GoogleDrive instance\\
	root_id : file ID of root folder\\
	owner : owner of root folder\\
	verbose : bool, execution of print statements
	Returns
	-------
	bool
	'''
	try:
		# Get file ID if no file ID is parsed
		if file_id == None:
			file_id_list = get_drive_file_id_list(
				file_path=file_path,
				drive=drive,
				root_id=root_id,
				owner=owner,
				verbose=verbose
			)
			assert len(file_id_list) > 0
			file_id = file_id_list[-1]
		else:
			pass
		# Download
		filename = download_directory + download_filename
		drive.CreateFile({'id': file_id}).GetContentFile(filename)
		if verbose:
			print(f'Download location: {filename}')
		return True
	
	except AssertionError as e:
		if verbose:
			print(f'{file_path} not found in Drive')
		else:
			pass
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
		return False

	except Exception as e:
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
		return False

def get_file_metadata(file_path=None,param_dict=PARAM_DICT,metadata_fields=METADATA_FIELDS,drive=None,root_id=ROOT_ID,owner=OWNER,verbose=VERBOSE):
	'''
	Description
	-----------
	Queries for and returns GoogleDrive File instances' metadata.
	Parameters
	----------
	file_path : str, absolute path to GoogleDriveFile. Ignored if file_id is parsed.\\
	param_dict : dict, parameters to be satified by query\\
	metadata_fields : list, file metadata fields to be returned.\\
	drive : GoogleDrive, authenticated GoogleDrive instance\\
	root_id : file ID of root folder\\
	owner : owner of root folder\\
	verbose : bool, execution of print statements
	Returns
	-------
	list, contains dictionary of metadata fields for each file found in query
	'''
	metadata = []
	param_dict = deepcopy(PARAM_DICT)
	try:
		# Get file ID
		if not file_path == None:
			file_id_list = get_drive_file_id_list(file_path=file_path,drive=drive,root_id=root_id,owner=owner,verbose=verbose)
			assert len(file_id_list) > 0
			param_dict['q'] = f"'{file_id_list[-1]}' in parents and trashed=false" 
		else:
			pass
		parent = get_drive_file_list(param_dict=param_dict,drive=drive,verbose=verbose)
		
		for child in parent:
			child_metadata = {}
			
			for field in metadata_fields:
				try:
					child_metadata[field] = child[field]
				except:
					child_metadata[field] = '-'
			metadata.append(child_metadata)
	
	except AssertionError as e:
		if verbose:
			print(f'{file_path} not found in Drive')
		else:
			pass
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
		return False

	except Exception as e:
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
	
	return metadata

def is_integer(x=None):
	try:
		int(x)
		return True
	except:
		return False

def main():
	'''
	Description
	-----------
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
	current_file_path = ''
	current_id = None
	param_dict = deepcopy(PARAM_DICT)
	file_id_list = []
	current_file_path = current_file_path.strip()
	
	while True:
		if current_file_path == '':
			param_dict['q'] = f"{ROOT_ID} and '{OWNER}' in owners and trashed=false"
		elif not current_id == None:
			param_dict['q'] = f"'{current_id}' in parents and trashed=false"
		else:
			break
		
		metadata = get_file_metadata(param_dict=param_dict,drive=drive)
		response = ''
		while not is_integer(x=response) or int(response) < 1:
			print('\n------------------------\nIEL Data Management Tool\n------------------------')
			print(f'Current file path: /Shared with me/{current_file_path}')
			for i in range(len(metadata)):
				string = ', '.join([f'{key}: {metadata[i][key]}' for key in metadata[i]])
				print(f'({i+1}) {string}')

			print('\n----\nMenu\n----')	
			print('1. Exit.')
			print('2. Download file.')
			print('3. Navigate to folder.')
			response = input('Response: ').strip()
		
		response = int(response)
		if response == 1:
			break
		elif response > 3:
			continue
		else:
			# Get file path or filename as case may be
			file_path = ''
			while len(file_path) < 1:
				file_path = input('File path or title: ').strip()

			# Set as absolute file path
			if not file_path[0] == '/' and len(current_file_path) > 0:
				file_path = file_path.strip('/').split('/')
				temp_current_file_path = current_file_path.strip('/').split('/')
				while len(file_path) > 0 and len(temp_current_file_path) > 0:
					if file_path[0] == '..':
						del file_path[0]
						del temp_current_file_path[-1]
					else:
						break
				
				if len(file_path) == 0 and len(temp_current_file_path) == 0:
					current_file_path = ''
					current_id = None
					continue
				else:
					pass

				file_path = temp_current_file_path + file_path
				file_path = '/'.join(file_path)

			else:
				pass

			# Get id list as proxy for navigating through Drive
			file_path = file_path.strip('/')
			file_id_list = get_drive_file_id_list(
				file_path=file_path,
				drive=drive,
				root_id=ROOT_ID,
				owner=OWNER
			)

			if len(file_id_list) > 0:
				# Download
				if response == 2:
					success = download(
						file_path=file_path,
						file_id=file_id_list[-1],
						download_filename=file_path.split('/')[-1],
						download_directory=DEFAULT_DOWNLOAD_DIRECTORY,
						drive=drive,
						root_id=ROOT_ID,
						owner=OWNER,
						verbose=True
					)
				else:
					# Navigate
					current_file_path = file_path
					current_id = file_id_list[-1]		
			else:
				print(f'No file path in Drive matching: {file_path}')

# Terminal execution		
if __name__ == "__main__":
	main()
