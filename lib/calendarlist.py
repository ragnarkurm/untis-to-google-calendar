def list(service):

	# print("CalendarList: Listing ...")

	pagetoken = ''
	active = {}
	while type(pagetoken) is str:
		items = service.calendarList().list(
			pageToken=pagetoken,
			showDeleted=False
		).execute()

		for item in items['items']:
			id = item['id']
			active[id] = item 

		pagetoken = items.get('nextPageToken', False)

	return active


def id2map(calendars):
	import re
	mapping = {}
	for id, c in calendars.items():
		if 'description' not in c:
			continue
		desc = c['description']
		id2 = re.match(r'\[\[([^\]]+)\]\]', desc);
		if not id2:
			continue
		id2 = id2.group(1)
		if id2 in mapping:
			print("Warning: Duplicate ID in calendar description: " + id2)
			continue
		mapping[id2] = c
	return mapping


def get(service, calendar):

	# print("CalendarList: Getting " + calendar)

	calendar = service.calendarList().get(
		calendarId=calendar,
	).execute()
	return calendar

# check from doc which fields are writable
def patch(service, calendar):

	# print("CalendarList: Patching " + calendar['id'])

	calendar = service.calendarList().patch(
		calendarId=calendar['id'],
		body=calendar
	).execute()
	return calendar

def delete(service, calendar):

	# print("CalendarList: Deleting " + calendar)

	calendar = service.calendarList().delete(
		calendarId=calendar,
	).execute()
