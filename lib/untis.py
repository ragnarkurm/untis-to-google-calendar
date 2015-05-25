def strip(txt):
	import re
	txt = txt.strip()
	txt = re.sub(r' {2,}', ' ', txt)
	return txt

def untis(file, opts):

	import logs
	logs.logs('h1', 'Untis import')
	logs.logs(None, 'File: ' + file)

	from datetime import datetime
	# import base64 # broken
	import binascii
	import os
	import re
	import sys
	import time
	import xml.etree.ElementTree as ET

	os.environ['TZ'] = opts['timezone']
	time.tzset()

	# print('Reading XML from stdin ...')
	# file = "\n".join(sys.stdin)
	# tree = ET.fromstring(file)
	tree = ET.parse(file)
	tree = ET.ElementTree(tree)
	root = tree.getroot()

	termbegin = root.find('general').find('termbegindate').text
	termbegin = datetime.strptime(termbegin, '%Y%m%d')
	logs.logs(None, 'Term Begin: ' + termbegin.strftime('%Y-%m-%d'))
	termbegin = termbegin.strftime('%s')
	termbegin = int(termbegin)

	termend = root.find('general').find('termenddate').text
	termend = datetime.strptime(termend, '%Y%m%d')
	logs.logs(None, 'Term End: ' + termend.strftime('%Y-%m-%d'))
	termend = termend.strftime('%s')
	termend = int(termend)

	rooms = {}
	for room in root.find('rooms'):
		id = room.attrib['id']
		id2 = re.sub(r'^RM_', '', id)
		longname = room.find('longname')
		if longname is None:
			rooms[id] = id2
		else:
			rooms[id] = id2 + ' ' + strip(longname.text)
	logs.logs(None, 'Rooms: ' + str(len(rooms)))

	subjects = {}
	for subject in root.find('subjects'):
		id = subject.attrib['id']
		id2 = re.sub(r'^SU_', '', id)
		longname = subject.find('longname')
		if longname is None:
			subjects[id] = id2
		else:
			subjects[id] = strip(longname.text)

	teachers = {}
	for teacher in root.find('teachers'):
		id = teacher.attrib['id']
		id2 = re.sub(r'^TR_', '', id)
		surname = teacher.find('surname')
		if surname is None:
			teachers[id] = id2
		else:
			teachers[id] = strip(surname.text)
	logs.logs(None, 'Teachers: ' + str(len(teachers)))

	classes = {}
	for clss in root.find('classes'):
		id = clss.attrib['id']
		id2 = re.sub(r'^CL_', '', id)
		longname = clss.find('longname')
		if longname is None:
			classes[id] = id2
		else:
			classes[id] = strip(longname.text)
	logs.logs(None, 'Classes: ' + str(len(classes)))

	lessons = {}
	for lesson in root.find('lessons').findall('lesson'):

		subject_id = lesson.find('lesson_subject')
		if subject_id is None:
			subject = ''
			subject_id = ''
		else:
			subject_id = subject_id.attrib['id']
			subject = subjects[subject_id]

		teacher_id = lesson.find('lesson_teacher')
		if teacher_id is None:
			teacher = ''
			teacher_id = ''
		else:
			teacher_id = teacher_id.attrib['id']
			teacher = teachers[teacher_id]

		times = lesson.find('times')

		# class id-s may contain spaces, yuck!
		class_ids = lesson.find('lesson_classes')
		if class_ids is None:
			class_ids = ['']
		else:
			class_ids = class_ids.attrib['id']
			class_ids = re.split(r'\s*CL_', class_ids)
			class_ids = filter(lambda x: len(x) > 0, class_ids)
			class_ids = map(lambda x: 'CL_' + x, class_ids)

		for class_id in class_ids:
			class_id = class_id
			if len(class_id) > 0:
				clAss = classes[class_id]
			else:
				clAss = ''
			for time in times:
				room = time.find('assigned_room')
				if room is None:
					room_id = ''
					room = ''
				else:
					room_id = room.attrib['id']
					room = rooms[room_id]

				date = time.find('assigned_date').text

				start0 = time.find('assigned_starttime').text
				start = datetime.strptime(date + start0, '%Y%m%d%H%M').strftime('%s')
				start = int(start)

				end0 = time.find('assigned_endtime').text
				end = datetime.strptime(date + end0, '%Y%m%d%H%M').strftime('%s')
				end = int(end)

				id = [subject_id, teacher_id, class_id, room_id, str(start), str(end)]
				id = ':'.join(id)
				# b32encode() is unable to handle unicode
				id = id.encode('ascii', 'xmlcharrefreplace')
				# id = base64.b32encode(id) # broken
				id = binascii.hexlify(id)
				id = id.decode('utf-8')
				id = id.lower()

				lessons[id] = {
					'id': id,
					'subject_id': subject_id,
					'subject': subject,
					'teacher_id': teacher_id,
					'teacher': teacher,
					'room_id': room_id,
					'room': room,
					'class_id': class_id,
					'class': clAss,
					'start': start,
					'end': end,
					# for debugging timezone
					# 'start0': start0,
					# 'end0': end0,
					'timezone': opts['timezone'],
				}

	logs.logs(None, 'Lessons: ' + str(len(lessons)))

	return {
		'termbegin': termbegin,
		'termend': termend,
		'rooms': rooms,
		'classes': classes,
		'subjects': subjects,
		'teachers': teachers,
		'lessons': lessons
	}

def dofilter(lessons, field, value):
	filtered = {}
	for id, l in lessons.items():
		if field in l and l[field] == value:
			filtered[id] = l
	return filtered
