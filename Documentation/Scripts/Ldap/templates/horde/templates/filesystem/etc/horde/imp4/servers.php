<?php
if ($GLOBALS['conf']['kolab']['enabled']) {
    $servers['kolab'] = array(
        'name' => 'Kolab Cyrus IMAP Server',
        'server' => $GLOBALS['conf']['kolab']['imap']['server'],
        'hordeauth' => 'full',
        'protocol' => 'imap/notls/novalidate-cert',
        'port' => $GLOBALS['conf']['kolab']['imap']['port'],
        'maildomain' => $GLOBALS['conf']['kolab']['imap']['maildomain'],
        'realm' => '',
        'preferred' => '',
        'quota' => array(
            'driver' => 'cyrus',
            'params' => array(),
        ),
        'acl' => array(
            'driver' => 'rfc2086',
        ),
    );
}
