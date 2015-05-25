def login(flags, opts):

	from apiclient.discovery import build
	from httplib2 import Http
	from oauth2client import client
	from oauth2client import tools
	import oauth2client

	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""

	store = oauth2client.file.Storage(opts['credential_path'])
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(opts['client_secret_file'], opts['scopes'])
		flow.user_agent = opts['application_name']
		credentials = tools.run_flow(flow, store, flags)
	service = build('calendar', 'v3', http=credentials.authorize(Http()))
	return service

