# credit:
# http://www.kfirlavi.com/blog/2012/11/06/elegant-locking-of-bash-program/

readonly LOCK_DIR=/tmp
readonly LOCK_FD=200
readonly LOCK_PROG=$(/usr/bin/basename "$0")

lock() {
	local prefix="$1"
	local fd=${2:-$LOCK_FD}
	local lock_file="$LOCK_DIR/$prefix.lock"

	# create lock file
	eval "exec $fd>$lock_file"

	# acquire the lock
	/usr/bin/flock -n "$fd" \
	&& return 0 \
	|| return 1
}

lock_eexit() {
	local error_str="$@"

	echo "$error_str"
	exit 1
}

lock $LOCK_PROG \
|| exit 0

# || lock_eexit "Only one instance of $LOCK_PROG can run at one time."
