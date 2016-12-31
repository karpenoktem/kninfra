<?php
$config->custom->appearance['friendly_attrs'] = array();
$servers = new Datastore();
$servers->newServer('ldap_pla');
$servers->setValue('server','name','My LDAP Server');
$servers->setValue('server','host','127.0.0.1');
$servers->setValue('server','base',array('{{ pillar['ldap-suffix'] }}'));
$servers->setValue('login','auth_type','session');
$servers->setValue('login','bind_id','cn=admin,{{ pillar['ldap-suffix'] }}');
?>
