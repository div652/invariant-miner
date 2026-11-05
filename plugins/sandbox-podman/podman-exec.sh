#!/usr/bin/env bash
# Run one command inside the task container on behalf of DSH (argv[0] of every command sandbox-podman confines).
#
#   podman-exec.sh RUNTIME CONTAINER WORKDIR [KEY=VALUE ...] -- PROGRAM [ARGS ...]
#
# The command runs in its own session (setsid) and records its process-group id in the container's /tmp. When DSH
# stops the command (tool timeout, cancellation) it signals this script on the host; the trap then kills the whole
# process group INSIDE the container: stopping only the host-side `podman exec` client would leave it running there.
# The exit status is the command's own; 125 with an "Error: " line on stderr is podman failing to run it.
set -u
runtime="$1" container="$2" workdir="$3"
shift 3
env_args=()
while [[ $# -gt 0 && "$1" != "--" ]]; do env_args+=(-e "$1"); shift; done
[[ $# -gt 0 ]] && shift
id="$(od -An -N8 -tx8 /dev/urandom | tr -d ' \n')"
pidfile="/tmp/.dsh-exec-$id.pid"

"$runtime" exec -w "$workdir" "${env_args[@]}" "$container" \
  setsid -w bash -c 'echo $$ > "$0"; exec "$@"' "$pidfile" "$@" &
child=$!

stop() {
  "$runtime" exec "$container" bash -c 'p="$(cat "$1" 2>/dev/null)" && kill -KILL -- "-$p" 2>/dev/null; rm -f "$1"' \
    _ "$pidfile" >/dev/null 2>&1
  kill "$child" 2>/dev/null
  exit 143
}
trap stop TERM INT HUP

wait "$child"
