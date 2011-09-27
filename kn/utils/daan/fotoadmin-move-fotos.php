#!/usr/bin/php
<?php
	define('FOTO_DIR', '/var/fotos/');
	define('USER_DIRS', '/mnt/phassa/home/');

	if($_SERVER['argc'] < 3) {
		echo 'Usage: '. $_SERVER['argv'][0] ." <event> <user> <dir>\n";
		exit(1);
	}
	if(!preg_match('/^20\d{2}-\d{2}-\d{2}-[a-z0-9-]{3,64}$/', $_SERVER['argv'][1])) {
		echo $_SERVER['argv'][0] .": Invalid event\n";
		exit(1);
	}
	if(!preg_match('/^[a-z0-9]{3,32}$/', $_SERVER['argv'][2])) {
		echo $_SERVER['argv'][0] .": Invalid user\n";
		exit(1);
	}
	if(!preg_match('@^[^/\.][^/]*$@', $_SERVER['argv'][3])) { // XXX check for nul-bytes?
		echo $_SERVER['argv'][0] .": Invalid dir\n";
		exit(1);
	}
	$fdir = USER_DIRS . $_SERVER['argv'][2];
	$userdir = $fdir;
	if(!is_dir($fdir)) {
		echo $_SERVER['argv'][0] .": Invalid user\n";
		exit(1);
	}
	$fdir .= '/fotos/'. $_SERVER['argv'][3];
	if(!is_dir($fdir)) {
		echo $_SERVER['argv'][0] .": Invalid fotodir\n";
		exit(1);
	}

	if(strncmp($userdir, realpath($fdir), strlen($userdir)) != 0) {
		echo $_SERVER['argv'][0] .": Security exception\n";
		exit(1);
	}

	$event = $_SERVER['argv'][1];
	$tdir = FOTO_DIR . $event .'/';
	if(!is_dir($tdir)) {
		echo $_SERVER['argv'][0] .": Event does not exist\n";
		var_dump($tdir);
		exit(1);
	}

	$tdir .= $_SERVER['argv'][2];

	if(is_dir($tdir)) {
		for($i = 2; is_dir($tdir . $i); $i++) {
			if($i > 10000) {
				echo $_SERVER['argv'][0] .": Internal error\n";
				exit(1);
			}
		}
		$tdir .= $i;
	}

	$tdir .= '/';

	$ok = true;

	exec('mv '. escapeshellarg($fdir) .' '. escapeshellarg($tdir), $out, $ret);
	if($ret != 0) {
		echo $_SERVER['argv'][0] .": mv failed\n";
		exit(1);
	}

	exec('chown -R fotos:fotos '. escapeshellarg($tdir), $out, $ret);
	if($ret != 0) {
		echo $_SERVER['argv'][0] .": [warn] chown() failed\n";
		$ok = false;
	}
	exec('chmod -R 644 '. escapeshellarg($tdir), $out, $ret);
	if($ret != 0) {
		echo $_SERVER['argv'][0] .": [warn] chmod() (files) failed\n";
		$ok = false;
	}
	exec('find '. escapeshellarg($tdir) .' -type d -exec chmod 755 {} +', $out, $ret);
	if($ret != 0) {
		echo $_SERVER['argv'][0] .": [warn] chmod() (dirs) failed\n";
		$ok = false;
	}

	if(include('/srv/karpenoktem.nl/htdocs/fotos/config.php')) {
		mysql_connect($db_host, $db_user, $db_pass);
		mysql_select_db($db_db);

		$visibility = 'hidden';

		$res = mysql_query("SELECT visibility FROM fa_albums WHERE name='". addslashes($event) ."' AND path=''");
		if($row = mysql_fetch_assoc($res)) {
			if($row['visibility'] == 'hidden') {
				$visibility = 'world';
			}
		}

		if(!mysql_query("INSERT INTO fa_albums (name, path, visibility) VALUE ('". addslashes($_SERVER['argv'][2]) ."', '". addslashes($event) ."/', '". $visibility ."')")) {
			echo $_SERVER['argv'][0] .": [warn] Setting visibility failed\n";
			$ok = false;
		}
	}

	if($ok) {
		echo "Gelukt!\n";
	}
?>
