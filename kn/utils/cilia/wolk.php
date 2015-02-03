<?php
// Called by wolk.py to apply synchronize users/groups with owncloud.
// Reads instructions from stdin.
// wolk.py makes sure we are executed with CWD ~owncloud

$data = json_decode(fgets(STDIN), TRUE);

require_once 'lib/base.php'; # CWD ~owncloud

if($data['type'] === 'apply_changes') {
        $changes = $data['changes'];
        foreach($changes['addUser'] as $user) {
                echo("Adding user {$user[0]}\n");
                OC_User::createUser($user[0], openssl_random_pseudo_bytes(10));
                // TODO set realname ($user[1])
        }
        foreach($changes['addGroup'] as $group) {
                echo("Adding group {$group}\n");
                OC_Group::createGroup($group);
        }
        foreach($changes['addUserToGroup'] as $user_group) {
                list($user, $group) = $user_group;
                echo("$Adding {$user} to {$group}\n");
                OC_Group::addToGroup($user, $group);
        }
        // TODO removeUserFromGroup
} else {
        die('unknown action');
}

OC_App::loadApps();


?>
