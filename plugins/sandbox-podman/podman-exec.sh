#!/usr/bin/env bash
# Run one command inside the task container on behalf of DSH (argv[0] of every command sandbox-podman confines).
#
#   podman-exec.sh RUNTIME CONTAINER WORKDIR [--user=USER] [--umask=MODE] [KEY=VALUE ...] -- PROGRAM [ARGS ...]
#
# --user runs the command as that container user (a name also gets its groups); --umask sets its umask. Stopping a
# command still runs as the container's default user, which may signal the command's processes.
# The command runs in its own session (setsid) and records its process-group id in the container's /tmp. When DSH
# stops the command (tool timeout, cancellation) it signals this script on the host; the trap then kills the whole
# process group INSIDE the container: stopping only the host-side `podman exec` client would leave it running there.
# The exit status is the command's own; 125 with an "Error: " line on stderr is podman failing to run it.
set -u
runtime="$1" container="$2" workdir="$3"
shift 3
user_args=() mask=""
while [[ $# -gt 0 && "$1" == --* && "$1" != "--" ]]; do
  case "$1" in
    --user=*) user_args=(--user "${1#--user=}") ;;
    --umask=*) mask="${1#--umask=}" ;;
    *) echo "podman-exec.sh: unknown option $1" >&2; exit 2 ;;
  esac
  shift
done
env_args=()
while [[ $# -gt 0 && "$1" != "--" ]]; do env_args+=(-e "$1"); shift; done
[[ $# -gt 0 ]] && shift
id="$(od -An -N8 -tx8 /dev/urandom | tr -d ' \n')"
pidfile="/tmp/.dsh-exec-$id.pid"

"$runtime" exec -w "$workdir" "${user_args[@]}" "${env_args[@]}" "$container" \
  setsid -w bash -c 'if [ -n "$1" ]; then umask "$1"; fi; shift; echo $$ > "$0"; exec "$@"' "$pidfile" "$mask" "$@" &
child=$!

stop() {
  "$runtime" exec "$container" bash -c 'p="$(cat "$1" 2>/dev/null)" && kill -KILL -- "-$p" 2>/dev/null; rm -f "$1"' \
    _ "$pidfile" >/dev/null 2>&1
  kill "$child" 2>/dev/null
  exit 143
}
trap stop TERM INT HUP

wait "$child"
