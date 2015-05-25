<?php

$BASEPATH = realpath(dirname(__FILE__) . '/..');
require "$BASEPATH/etc/conf.php";

function input() {
	global $SEPARATOR;
	global $SECTIONS;
	$rx = array_map(function($a){return $a['id_prefix'];}, $SECTIONS);
	$rx = implode('|', $rx);
	$rx = "/^({$rx})_/";
	$data = array();
	while($l = fgets(STDIN)){
		$l = trim($l);
		$l = explode($SEPARATOR, $l);
		list($untis_id, $gcal_id, $timezone, $name) = $l;
		if (!preg_match($rx, $untis_id, $match)) {
			print "Unknown ID: $untis_id\n";
			exit(0);
		}
		$section = $match[1];
		$data[$section][] = array(
			'untis_id' => $untis_id,
			'gcal_id' => $gcal_id,
			'timezone' => $timezone,
			'name' => $name,
		);
	}
	return $data;
}

function convert($data) {
	foreach (array_keys($data) as $section) {
		usort($data[$section], function($a, $b) { return strcmp($a['name'], $b['name']); });
	}
	return $data;
}

function anchor($c) {
	global $CALENDAR_URL;
	$name = $c['name'];
	$name = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
	$query = array(
		'src' => $c['gcal_id'],
		'mode' => 'week',
		'ctz' => $c['timezone'],
	);
	$query = http_build_query($query);
	$href = "$CALENDAR_URL?$query";
	$l = "<a href=\"$href\" target=\"_blank\">$name</a>";
	return $l;
}

function output($calendars, $title) {
	$title = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
	$links = array();
	foreach ($calendars as $c) {
		$links[] = '<li>' . anchor($c) . '</li>' . "\n";
	}
	$links = implode('', $links);
	$links = '<div class="item"><h2>' . $title . '</h2><ul>' . $links . '</ul></div>';
	return $links;
}

$data = input();
$data = convert($data);
$sections = array();
foreach ($SECTIONS as $s) {
	$sections[] = output($data[$s['id_prefix']], $s['name']);
}
$sections = implode("\n", $sections);
$template = file_get_contents($TEMPLATE_PATH);
$page = preg_replace('/%%DATA%%/', $sections, $template);
print $page;
