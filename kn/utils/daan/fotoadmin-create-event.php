#!/usr/bin/php
<?php
	define('FOTO_DIR', '/var/fotos/');

	if($_SERVER['argc'] < 3) {
		echo 'Usage: '. $_SERVER['argv'][0] ." <date> <name> [humanname]\n";
		exit(1);
	}
	if(!preg_match('/^20\d{2}-\d{2}-\d{2}$/', $_SERVER['argv'][1])) {
		echo $_SERVER['argv'][0] .": Invalid date\n";
		exit(1);
	}
	if(!preg_match('/^[a-z0-9-]{3,64}$/', $_SERVER['argv'][2])) {
		echo $_SERVER['argv'][0] .": Invalid name\n";
		exit(1);
	}

	$event = $_SERVER['argv'][1] .'-'. $_SERVER['argv'][2];
	$dir = FOTO_DIR . $event;

	if(is_dir($dir)) {
		echo $_SERVER['argv'][0] .": Already exists\n";
		exit(1);
	}

	$ok = true;

	if(!mkdir($dir, 0775)) {
		echo $_SERVER['argv'][0] .": [warn] mkdir() failed\n";
		$ok = false;
	}
	if(!chown($dir, 'root')) {
		echo $_SERVER['argv'][0] .": [warn] chown() failed\n";
		$ok = false;
	}
	if(!chgrp($dir, 'kn')) {
		echo $_SERVER['argv'][0] .": [warn] chgrp() failed\n";
		$ok = false;
	}

	if(include('/srv/karpenoktem.nl/htdocs/fotos/config.php')) {
		mysql_connect($db_host, $db_user, $db_pass);
		mysql_select_db($db_db);

		if($_SERVER['argc'] == 3) {
			$humanname = 'NULL';
		} else {
			$humanname = "'". addslashes($_SERVER['argv'][3]) ."'";
		}

		if(!mysql_query("INSERT INTO fa_albums (name, path, humanname, visibility) VALUE ('". addslashes($event) ."', '', ". $humanname .", 'hidden')")) {
			echo $_SERVER['argv'][0] .": [warn] Setting visibility failed\n";
			$ok = false;
		}
	}

	if($ok) {
		echo "Gelukt!\n";
	}
?>
