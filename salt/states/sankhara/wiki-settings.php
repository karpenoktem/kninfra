<?php
if ( !defined( 'MEDIAWIKI' ) ) { exit; }

$wgSitename      = "KnWiki";

$wgScriptPath       = "/W";
$wgArticlePath      = "/wiki/$1";
$wgUsePathInfo      = true;
$wgScriptExtension  = ".php";

# TODO https
$wgServer           = "http://{{ grains['fqdn'] }}";

$wgStylePath        = "$wgScriptPath/skins";

$wgEnableEmail      = true;
$wgEnableUserEmail  = true; # UPO

$wgEmergencyContact = "webcie@{{ grains['fqdn'] }}";
$wgPasswordSender   = "root@{{ grains['fqdn'] }}";

$wgEnotifUserTalk      = false;
$wgEnotifWatchlist     = false;
$wgEmailAuthentication = true;

$wgFileExtensions = array( 'png', 'gif', 'jpg', 'jpeg', 'pdf' );

$wgDBtype           = "mysql";
$wgDBserver         = "localhost";
$wgDBname           = "wiki";
$wgDBuser           = "wiki";
$wgDBpassword       = "{{ pillar['secrets']['mysql_wiki'] }}";
$wgDBprefix         = "";

$wgDBTableOptions   = "ENGINE=InnoDB, DEFAULT CHARSET=binary";
$wgDBmysql5 = false;

$wgMainCacheType    = CACHE_MEMCACHED;
$wgMemCachedServers = array( '127.0.0.1:11211');

$wgEnableUploads  = true;
$wgUseImageMagick = true;
$wgImageMagickConvertCommand = "/usr/bin/convert";

$wgUseInstantCommons  = false;
$wgShellLocale = "en_US.utf8";

$wgLanguageCode = "nl";
$wgSecretKey = "{{ pillar['secrets']['wiki_key'] }}";
$wgUpgradeKey = "{{ pillar['secrets']['wiki_upgrade_key'] }}";

wfLoadSkin('Vector');
$wgDefaultSkin = "vector";

$wgRightsPage = "";
$wgRightsUrl  = "";
$wgRightsText = "";
$wgRightsIcon = "";

$wgDiff3 = "/usr/bin/diff3";

if (is_file("/etc/mediawiki-extensions/extensions.php")) {
	include("/etc/mediawiki-extensions/extensions.php");
}

$wgResourceLoaderMaxQueryLength = -1;

$wgGroupPermissions['*']['createaccount'] = false;
$wgGroupPermissions['*']['edit'] = false;
$wgGroupPermissions['*']['read'] = false;
$wgGroupPermissions['webcie']['delete'] = true;
$wgGroupPermissions['webcie']['undelete'] = true;
$wgGroupPermissions['webcie']['browsearchive'] = true;
$wgGroupPermissions['webcie']['deletedhistory'] = true;

$wgLogo             = "/djmedia/base/wiki-logo.png";
# TODO
# $wgUsersNotifiedOnAllChanges = array('Bas', 'Bramw');
$wgGroupPermissions['user']['createaccount'] = false;
$wgGroupPermissions['leden'] = $wgGroupPermissions['user'];
$wgGroupPermissions['user']['edit'] = false;
$wgGroupPermissions['user']['read'] = false;
$wgUseRCPatrol = false;
$wgGroupPermission['sysop']['patrol'] = false;
# TODO
# require_once($IP ."/extensions/APC/APC.php");
# $wgGroupPermissions['sysop']['apc'] = true;
$wgAllowExternalImagesFrom = array('https://nirodha.karpenoktem.nl/');

require_once "/etc/mediawiki/knauth/KNAuth.php";
$wgKNAuthVerifyURL = 'http://localhost/accounts/api/';
