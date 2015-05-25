# google event filtering works in following way:
# event.begin < end && event.end > begin

def list(service, calendar, begin, end, opts):

	# print("Events: Listing ...")

	from datetime import datetime
	import pytz

	# 2015-05-02T10:00:00.000

	tz = opts['timezone']
	tz = pytz.timezone(tz)

	begin = float(begin)
	begin = datetime.fromtimestamp(begin)
	begin = tz.localize(begin)
	begin = begin.strftime('%Y-%m-%dT%H:%M:%S%z')

	end = float(end)
	end = datetime.fromtimestamp(end)
	end = tz.localize(end)
	end = end.strftime('%Y-%m-%dT%H:%M:%S%z')

	# print("event.list(): begin = ", begin)
	# print("event.list(): end = ", end)

	pagetoken = ''
	active = {}
	deleted = {}
	while type(pagetoken) is str:
		items = service.events().list(
			calendarId=calendar,
			singleEvents=True,
			showDeleted=True,
			# maxResults=5,
			pageToken=pagetoken,
			timeMin=begin,
			timeMax=end,
		).execute()

		for item in items.get('items', []):
			id = item.get('id', '')
			if item['status'] == 'confirmed':
				active[id] = item 
			else:
				deleted[id] = item

		pagetoken = items.get('nextPageToken', False)

	return (active, deleted)


def delete(service, calendar, event):

	# print("Events: Deleting " + event)

	result = service.events().delete(
		calendarId=calendar,
		eventId=event
	).execute()


def get(service, calendar, event):

	# print("Events: Getting " + event)

	event = service.events().get(
		calendarId=calendar,
		eventId=event
	).execute()
	return event


def build(event):

	from datetime import datetime

	# 2015-05-02T10:00:00.000

	start = event['start']
	start = float(start)
	start = datetime.fromtimestamp(start)
	start = start.strftime('%Y-%m-%dT%H:%M:%S.%f')

	end = event['end']
	end = float(end)
	end = datetime.fromtimestamp(end)
	end = end.strftime('%Y-%m-%dT%H:%M:%S.%f')

	description = '' \
		+ 'Teacher: ' + event['teacher'] + "\n" \
		+ 'Class: ' + event['class'] + "\n" \


	event = {
		'summary': event['subject'],
	'description': description,
	'id': event['id'],
		'location': event['room'],
		'start': {
			'dateTime': start,
			'timeZone': event['timezone'],
		},
		'end': {
			'dateTime': end,
			'timeZone': event['timezone'],
		},
		'guestsCanInviteOthers': False,
		'guestsCanSeeOtherGuests': False,
	}

	return event


def insert(service, calendar, event):

	# print("Events: Inserting " + event['id'])

	event = build(event)
	event = service.events().insert(calendarId=calendar, body=event).execute()
	return event


def update(service, calendar, event):

	# print("Events: Updating " + event['id'])

	event = build(event)
	event = service.events().update(calendarId=calendar, eventId=event['id'], body=event).execute()
	return event

