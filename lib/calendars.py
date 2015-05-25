def delete(service, calendar):

	# print("Calendars: Deleting " + calendar)

	result = service.calendars().delete(
		calendarId=calendar,
	).execute()


def get(service, calendar):

	# print("Calendars: Getting " + calendar)

	calendar = service.events().get(
		calendarId=calendar
	).execute()
	return calendar


def encode(id2):
	return '[[' + id2 + ']]'


def build(calendar, opts):

	calendar['location'] = opts['location']
	calendar['timeZone'] = opts['timezone']
	return calendar


def insert(service, calendar, opts):

	# print("Calendars: Inserting " + calendar['summary'])

	calendar = build(calendar, opts)
	calendar = service.calendars().insert(
		body=calendar
	).execute()
	return calendar


def patch(service, calendar):

	# print("Calendars: Patching " + calendar['id'])

	calendar = service.calendars().patch(
		calendarId=calendar['id'],
		body=calendar
	).execute()
	return calendar
