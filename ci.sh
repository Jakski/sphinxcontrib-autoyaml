#!/usr/bin/env sh

set -euo pipefail

on_exit() {
	local code=$?
	if [ "$code" != 0 ]; then
		printf "%s\n" "Failed with exit code: ${code}" >&2
	fi
}

trap on_exit EXIT

for_all_scenarios() {
	local pyver envnum
	for pyver in 3-10 3-11 3-14; do
		for envnum in 1 2 3 4 5; do
			if [ "$pyver" = "3-14" ]; then
				# Older versions depend on imghdr,
				# which has been removed from standard library
				case "$envnum" in
				4|5) ;;
				*) continue ;;
				esac
			fi
			export MISE_ENV="py${pyver}"
			export ENV_NUMBER="$envnum"
			printf "%s\n" \
				"Python: ${pyver}" \
				"Environment: ${envnum}"
			"$@"
		done
	done
}

main() {
	local action="$1"; shift
	case "$action" in
	run-tests) for_all_scenarios mise run test ;;
	update-lockfiles) for_all_scenarios mise run update-test-lockfile ;;
	esac
}

main "$@"
