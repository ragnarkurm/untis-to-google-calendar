# nb! module logging already exists

start = None

def logs(type, message):

	from datetime import datetime

	# term len - timestamp - space - last char
	l = 80 - 14 - 1 - 1
	l = str(l)

	global start
	if  start is None:
		start = datetime.now()

	duration = datetime.now() - start
	duration = str(duration)

	message = message.strip()
	if type == 'h1':
		message = '===[ ' + message + ' ]'
		message = ('{:=<' + l + 's}').format(message)
	elif type == 'h2':
		message = '---[ ' + message + ' ]'
		message = ('{:-<' + l + 's}').format(message)
	elif type == 'h3':
		message = '...[ ' + message + ' ]'
		message = ('{:.<' + l + 's}').format(message)
	elif type == 'h4':
		message = '/// ' + message + ' ///'
	elif type == 'err':
		# if printing to stderr
		# strams' messages get mixed during 2>&1
		# meaning stderr printed before stdout
		message = '!!! ' + message
	else:
		pass

	message = '{} {}'.format(duration, message)
	# message = message.encode('utf-8')
	print(message)
