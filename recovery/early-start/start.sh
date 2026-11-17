#!/bin/sh
# One ordinary service-launch request as the TV owner, never a new root daemon.
base=/home/owner/share/vetro-early-start-trial
[ -f "$base/.trial-owned" ] || exit 0
printf 'uptime ' >> "$base/attempt.log"
cat /proc/uptime >> "$base/attempt.log"
/usr/bin/app_launcher -s vetrotvapp.svc >> "$base/attempt.log" 2>&1
result=$?
printf '\nlauncher_request_exit %s\n' "$result" >> "$base/attempt.log"
exit "$result"
