#!/usr/bin/env bash
set -e
# todo: host key checking for sanity
key="$(mktemp)-vm-ssh.key"
function finish {
    rm -f $key
}
cp "$(realpath $(dirname "$0"))/vm-ssh.key" "$key"
trap finish EXIT
chmod 0600 $key
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$key" root@localhost -p 2222 "$@"
