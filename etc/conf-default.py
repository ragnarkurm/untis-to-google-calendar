# -*- coding: utf-8 -*-

from basepath import basepath

opts = {
	'credential_path': basepath('state', 'credentials-untis-gcal.json'),
	'client_secret_file': basepath('etc', 'client_secret.json'),
	'scopes': 'https://www.googleapis.com/auth/calendar',
	'application_name': 'Untis to Google Calendar',
	'location': 'School Name, City, County, Country',
	'timezone': 'Time/Zone',
	'public_calendar': '__public_principal__@public.calendar.google.com',
	'csv_separator': "\t",
	'csv_replacement': ' ',
}
