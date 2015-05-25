import acl
import calendarlist
import calendars
import event
import login
import logs
import untis


sections = [
	('teachers', 'teacher_id', 'TR'),
	('rooms',    'room_id',    'RM'),
	('classes',  'class_id',   'CL'),
]


def check_date_format(value):
	import re
	import argparse
	if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
		raise argparse.ArgumentTypeError("Invalid date format: %s" % value)
	from datetime import datetime
	value = datetime.strptime(value, '%Y-%m-%d')
	value = value.strftime('%s')
	value = int(value)
	return value


def args():

	from oauth2client import tools
	import argparse

	choices = ['all']
	for (s, id, prefix) in sections:
		choices.append(s)
	tools.argparser.add_argument(
		'--sections',
		choices = choices,
		default = 'all'
	)

	tools.argparser.add_argument(
		'--sync',
		choices = ['all', 'calendars', 'events', 'none'],
		default = 'all'
	)

	tools.argparser.add_argument(
		'--id',
		help = 'Check ID from untis file. Examples: CL_IS-13, RM_P215, TR_RKu.'
	)

	tools.argparser.add_argument(
		'--begin',
		type = check_date_format,
		help = 'Import from /begin/ date. Format YYYY-MM-DD',
	)

	tools.argparser.add_argument(
		'--end',
		type = check_date_format,
		help = 'Import until /end/ date. Format YYYY-MM-DD',
	)

	tools.argparser.add_argument(
		'--calendar_delete_allow',
		'-d',
		action='store_true',
		help = 'Allow to delete dedundant calendars. API operation limits may apply.',
	)

	tools.argparser.add_argument(
		'untis_xml_file',
		help = 'Untis XML file',
	)

	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
	if flags.begin is not None and flags.end is not None and flags.end < flags.begin:
		raise argparse.ArgumentTypeError("Begin (%s) must be before End (%s)." % (flags.begin, flags.end))
	return flags


def sync_calendars(service, id2summary, sync, delete, id_prefix, opts):

	active = calendarlist.list(service)
	active_id2 = calendarlist.id2map(active)

	deleted = set(active_id2.keys()) - set(id2summary.keys())
	import re
	deleted = filter(lambda x: re.match(r'^' + id_prefix + '_', x), deleted)
	deleted = list(deleted)
	if len(deleted) > 0:
		if delete:
			logs.logs('h3', 'Deleting calendars')
			i = 1
			count = len(deleted)
			for id in deleted:
				cal = active_id2[id]
				logs.logs(None, '{:02d}% {}: {}'.format(int(100 * i / count), id, cal['summary']))
				calendarlist.delete(service, cal['id'])
				i = i + 1
		else:
			logs.logs('h3', 'Redundant calendars')
			for id in deleted:
				cal = active_id2[id]
				logs.logs(None, id + ': ' + cal['summary'])
			logs.logs(None, 'You can delete calendars in one of following ways:')
			logs.logs(None, '* Use Google web interface.')
			logs.logs(None, '* Use gcal_rm.')
			logs.logs(None, '* Specify --calendar_delete_allow or -d.')

	if sync:
		logs.logs('h3', 'Checking/inserting/updating calendars')
	i = 1
	count = len(id2summary)
	for id2, summary in id2summary.items():

		# this is "goto end" replacement
		if not sync:
			break

		logs.logs(None, '{:02d}% {}'.format(int(100 * i / count), summary))
		i = i + 1

		if id2 in active_id2:
			calendar = active_id2[id2]
			id = calendar['id']
		else:
			calendar = {
				'summary': summary,
				'description': calendars.encode(id2),
			}
			calendar = calendars.insert(service, calendar, opts)
			id = calendar['id']
			calendar = calendarlist.get(service, id)
			calendar = {
				'id': calendar['id'],
				'selected': False,
			}
			calendar = calendarlist.patch(service, calendar)
			active[id] = calendar
			active_id2[id2] = calendar

		# now we have: id, id2, calendar

		# check if need to patch calendar settings

		patch = {}
		if calendar['summary'] != summary:
			patch['summary'] = summary

		encoded = calendars.encode(id2)
		if calendar['description'] != encoded:
			patch['description'] = encoded

		if calendar['location'] != opts['location']:
			patch['location'] = opts['location']

		if calendar['timeZone'] != opts['timezone']:
			patch['timeZone'] = opts['timezone']

		if len(patch) > 0:
			patch['id'] = id
			calendars.patch(service, patch)

		# check if need to update acl

		# {
		#	'scope': {
		#		'type': 'default',
		#		'value': '__public_principal__@public.calendar.google.com'
		#	},
		#	'kind': 'calendar#aclRule',
		#	'etag': '"00001430601714475000"',
		#	'role': 'reader',
		#	'id': 'default'
		# }

		acls = acl.list(service, id)
		update = True
		role = 'reader'
		typ = 'default'
		value = opts['public_calendar']
		for k, a in acls.items():
			if True \
				and a['role'] == role \
				and a['scope']['type'] == typ \
				and a['scope']['value'] == value \
			:
				update = False
				break

		if update:
			acl.insert(service, id, {
				'role': role,
				'scope': {
					'type': typ,
					'value': 'default',
				},
			})

	ret_id2 = {}
	for id2 in id2summary:
		ret_id2[id2] = active_id2[id2]

	return ret_id2


def sync_events(calendar, lessons, begin, end, service, opts):

	import binascii

	(old, deleted) = event.list(service, calendar, begin, end, opts)

	begin = int(begin)
	end = int(end)

	lessons = {k:v for (k,v) in lessons.items() if v['start'] < end and v['end'] > begin}

	# delete
	ids = set(old.keys()) - set(lessons.keys())
	i = 1
	count = len(ids)
	if count > 0:
		logs.logs('h4', 'Deleting')
	for id in ids:
		logs.logs(None, '{}/{} {}'.format(i, count, id))
		event.delete(service, calendar, id)
		i = i + 1

	# insert
	ids = set(lessons.keys()) - set(old.keys()) - set(deleted.keys())
	i = 1
	count = len(ids)
	if count > 0:
		logs.logs('h4', 'Inserting')
	for id in ids:
		logs.logs(None, '{}/{} {}'.format(i, count, id))
		event.insert(service, calendar, lessons[id])
		i = i + 1

	# update
	ids = set(lessons.keys()) & set(deleted.keys())
	i = 1
	count = len(ids)
	if count > 0:
		logs.logs('h4', 'Updating')
	for id in ids:
		logs.logs(None, '{}/{} {}'.format(i, count, id))
		event.update(service, calendar, lessons[id])
		i = i + 1


def main_level2(opts):

	from datetime import datetime

	flags = args()

	now = datetime.now()
	now = now.strftime('%Y-%m-%d %H:%M:%S')
	logs.logs(None, 'Now: ' + now)

	logs.logs('h1', 'Arguments')
	for (k, v) in flags.__dict__.items():
		if k in ['begin', 'end'] and v is not None:
			logs.logs(None, k + ' = ' + str(datetime.fromtimestamp(float(v))))
		else:
			logs.logs(None, k + ' = ' + str(v))

	events = untis.untis(flags.untis_xml_file, opts)
	if flags.sync == 'none':
		import sys
		logs.logs(None, 'Finish')
		sys.exit()

	if flags.begin is None:
		begin = events['termbegin']
	else:
		begin = flags.begin

	if flags.end is None:
		end = events['termend']
	else:
		end = flags.end

	service = login.login(flags, opts)

	for (section, field, prefix) in sections:
		if flags.sections != 'all' and section != flags.sections:
			continue
		logs.logs('h1', 'Section ' + section)
		sync = flags.sync in ['all', 'calendars']
		if sync:
			logs.logs('h2', 'Syncing Calendar')
		cal_delete = flags.calendar_delete_allow
		id2cal = sync_calendars(service, events[section], sync, cal_delete, prefix, opts)
		if flags.sync not in ['all', 'events']:
			continue
		i = 1
		count = len(id2cal)
		for id2, calendar in id2cal.items():
			if isinstance(flags.id, str) and id2 != flags.id:
				continue
			elif flags.id is None:
				logs.logs('h3', '{:02d}% Syncing events in {}'.format(int(100 * i / count), calendar['summary']))
			else:
				logs.logs('h3', 'Syncing events in {}'.format(calendar['summary']))

			i = i + 1
			id = calendar['id']
			lessons = untis.dofilter(events['lessons'], field, id2)
			sync_events(id, lessons, begin, end, service, opts)

	logs.logs(None, 'Finish')


def main(opts):
	import sys # exit
	from apiclient.errors import HttpError
	from oauth2client.client import AccessTokenRefreshError
	from httplib2 import ServerNotFoundError

	try:
		main_level2(opts)

	except KeyboardInterrupt:
		logs.logs('err', 'Manual interruption ')
		sys.exit(1)

	except AccessTokenRefreshError:
		logs.logs('err', 'The credentials have been revoked or expired, please re-run the application to re-authorize')
		sys.exit(1)

	except TypeError as e:
		# Handle errors in constructing a query.
		logs.logs('err', 'There was an error in constructing your query : %s' % e)
		sys.exit(1)

	except HttpError as e:
		# Handle API service errors.
		logs.logs('err', 'There was an API error : %s : %s' % (e.resp.status, e._get_reason()))
		print(e.content)
		sys.exit(1)

	except ServerNotFoundError as e:
		logs.logs('err', str(e))
		sys.exit(1)
