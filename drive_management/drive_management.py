# Import libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import logging

# Constants & variables
owner = 'nweye@utexas.edu'
root_id = 'sharedWithMe'
file_description_fields = ['title','modifiedDate','fileSize']

# Methods for various API Calls
def authenticate_drive(file_name=None,verbose=False):
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
		file_name = "credentials.txt"

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

def get_drive_file_list(param_dict=None,drive=None,verbose=False):
	file_list = []
	
	try:
		file_list = drive.ListFile(param_dict).GetList()
	
	except Exception as e:
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
	
	return file_list

def get_drive_file_id_list(file_path=None,drive=None,owner=None,verbose=False):
	'''
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
				print(f'{"/".join(title_list[0:i+1])} not found in Drive')
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

def download(file_path=None,file_id=None,download_to='downloads/',drive=None,owner=None,verbose=False):
	'''
	'''
	
	try:
		if file_id == None:
			file_id_list = get_drive_file_id_list(
				file_path=file_path,
				drive=drive,
				owner=owner,
				verbose=verbose
			)
			assert len(file_id_list) > 0
			file_id = file_id_list[-1]
		else:
			pass

		filename = download_to + file_path.split('/')[-1]
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

def get_file_path_summary(param_dict=None,drive=None,verbose=False):
	'''
	'''

	summary = []

	try:
		parent = get_drive_file_list(param_dict=param_dict,drive=drive,verbose=verbose)
		
		for child in parent:
			file_description = []
			
			for field in file_description_fields:
				
				try:
					file_description.append(f'{field}: {child[field]}')
				except:
					file_description.append(f'{field}: -')

			summary.append(', '.join(file_description))

	except Exception as e:
		logging.error(e)
		print(type(e).__name__ + ': ' + str(e))
	
	return summary

def is_integer(x=None):
	try:
		int(x)
		return True
	except:
		return False

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
	current_file_path = ''
	current_id = None
	param_dict = {
		'q': '',
		'includeTeamDriveItems': True,
		'supportsTeamDrives': True
	}
	file_id_list = []

	current_file_path = current_file_path.strip()
	while True:
		# print current filepath
		if current_file_path == '':
			param_dict['q'] = f"{root_id} and '{owner}' in owners and trashed=false"
		elif not current_id == None:
			param_dict['q'] = f"'{current_id}' in parents and trashed=false"
		else:
			break
		
		summary = get_file_path_summary(param_dict=param_dict,drive=drive)
		response = ''
		while not is_integer(x=response) or int(response) < 1:
			print('\n------------------------\nIEL Data Management Tool\n------------------------')
			print(f'Current file path: /{current_file_path}')
			for i in range(len(summary)):
				print(f'({i+1}) {summary[i]}')

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

				file_path = temp_current_file_path + file_path
				file_path = '/'.join(file_path)

			else:
				pass

			# Get id list as proxy for navigating through Drive
			file_path = file_path.strip('/')
			file_id_list = get_drive_file_id_list(file_path=file_path,drive=drive,owner=owner)

			if len(file_id_list) > 0:
				# Download
				if response == 2:
					download(
						file_path=file_path,
						file_id=file_id_list[-1],
						drive=drive,
						verbose=True
					)
				else:
					# Navigate
					current_file_path = file_path
					current_id = file_id_list[-1]
					
			else:
				print(f'No file path in Driver matching: {file_path}')

# Terminal execution		
if __name__ == "__main__":
	main()