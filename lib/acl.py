def list(service, calendar):

	# print("Acl: Listing ...")

	pagetoken = ''
	acls = {}
	while type(pagetoken) is str:
		items = service.acl().list(
		calendarId=calendar,
		showDeleted=False,
				pageToken=pagetoken
		).execute()

		for item in items.get('items', []):
			id = item.get('id', '')
			acls[id] = item 

		pagetoken = items.get('nextPageToken', False)

	return acls


def insert(service, calendar, acl):

	# print("Acl: Inserting acl")

	a = service.acl().insert(calendarId=calendar, body=acl).execute()
	return a
