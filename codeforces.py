from bs4 import BeautifulSoup as soup
import os
import requests
import json

handle = 'davidcairuz'

extension = {'C++': 'cpp', 'C': 'c', 'Java': 'java', 'Python': 'py', 'C#': 'cs', 'FPC': 'pas', 'PyPy': 'py', 'Delphi': 'dpr',}
submission_url = 'http://codeforces.com/contest/{contest_id}/submission/{submission_id}'

response = requests.get('http://codeforces.com/api/user.status?handle={}&from=1&count=10000'.format(handle)).json()

if response['status'] != 'OK':
	print('A problem ocurred. Please, try again in a moment...')

if not os.path.exists(handle):
    os.makedirs(handle)

submissions = response['result']

for submission in submissions:
	if submission['verdict'][0] == 'O':
		problem_name = submission['problem']['name']
		problem_id = submission['problem']['index']
		contest_id = submission['contestId']
		submission_id = submission['id']
		submission_language = submission['programmingLanguage']

		submission_extension = ""

		if 'C++' in submission_language:
			submission_extension = 'cpp'
		else:	
			for language, ext in extension.items():
				if language in submission_language:
					submission_extension = ext

		if submission_extension == '':
			print("Don't know the extension for", submission_language)
			print("Teach me in the dictionary above...")

		try:
			submission_text = requests.get(submission_url.format(contest_id=contest_id, submission_id=submission_id)).text
			submission_html = soup(submission_text, "html.parser")
			submission_code = submission_html.find('pre', {'id':'program-source-text'}).text.replace('\r', '')
			print("Downloading", problem_name)
		except:
			print("Could not download", problem_name)
			continue

		# Choose one of the options below:

		# Option 1: All problems in the same folder, identified by contest id and letter.
		# with open("{}/{}{} - {}.{}".format(handle, contest_id, problem_id, problem_name, submission_extension), "w") as f:
		# 	f.write(submission_code)

		# Option 2: All problems in a separate folder for each contest and identified by letter.
		if not os.path.exists("{}/{}".format(handle, contest_id)):
			os.makedirs("{}/{}".format(handle, contest_id))

		with open("{}/{}/{} - {}.{}".format(handle, contest_id, problem_id, problem_name, submission_extension), "w") as f:
			f.write(submission_code)