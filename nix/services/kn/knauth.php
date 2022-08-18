<?php
// we use the Auth_remoteuser extension, with some extra hooks
// to set the login url and groups

// see https://github.com/wikimedia/mediawiki-extensions-Auth_remoteuser

// todo: upstream 'login' support would be nice
$wgAuthRemoteuserUserUrls = [
    'logout' => '/accounts/logout/',
];
$wgAuthRemoteuserAllowUserSwitch = false;
$wgAuthRemoteuserRemoveAuthPagesAndLinks = true;
$wgAuthRemoteuserPriority = 100;

// smuggle our api response through a global
$wgKNAuthLoginData = null;
$wgAuthRemoteuserUserName = function () {
    global $wgKNAuthLoginData, $wgKNAuthVerifyURL;
    if ($wgKNAuthLoginData != null) {
        // there's a bug where this sometimes happens (on mediawiki version mismatch)
        // and causes CAS errors
        echo "warning: wgAuthRemoteuserUserName ran twice!";
        //$e = new \Exception;
        //var_dump($e->getTraceAsString());
    }
    if (!isset($_COOKIE["sessionid"])) {
        return null;
    }

    $sessionid = $_COOKIE["sessionid"];
    if (!preg_match('/^[a-z0-9]+$/', $sessionid)) {
        # Strings with these characters are used since Django 1.5. Django 1.4
        # uses 0-9a-f.
        return null;
    }
    $ch = curl_init($wgKNAuthVerifyURL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_COOKIE, "sessionid=" . $sessionid);
    $res = curl_exec($ch);
    curl_close($ch);
    $data = json_decode($res, true);
    if ($data["valid"] !== true) {
        # invalid cookie
        return null;
    }
    $wgKNAuthLoginData = $data;
    return $data["name"];
};

// called later than wgAuthRemoteuserUserName
// but the addon makes a copy of the globals when it initializes
$wgAuthRemoteuserUserPrefsForced = [
    "email" => function ($metadata) {
        global $wgKNAuthLoginData;
        return $wgKNAuthLoginData["email"];
    },
    "realname" => function ($metadata) {
        global $wgKNAuthLoginData;
        return $wgKNAuthLoginData["humanName"];
    }
];

// remove auth links for unregistered users
Hooks::register("PersonalUrls", static function (&$personalurls) {
    unset($personalurls["createaccount"]);
    if (isset($personalurls["login-private"])) {
        $personalurls["login-private"] = [
            "href" => "/accounts/login/?next=" . $_SERVER['REQUEST_URI'],
            "text" => wfMessage("pt-login")->text(),
            "active" => false,
        ];
    }
    return true;
});

// XXX: Actually does not seem to save
// but that's okay
Hooks::register("GetAutoPromoteGroups", static function (&$user, &$promote) {
    global $wgKNAuthLoginData;
    if ($wgKNAuthLoginData != null) {
      $promote = $wgKNAuthLoginData['groups'];
      return true;
    }
});
