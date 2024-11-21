#!/usr/bin/env bash

set -euo pipefail -o errtrace
shopt -s inherit_errexit nullglob

on_error() {
	declare exit_code=$? cmd=$BASH_COMMAND
	echo "Failing with code ${exit_code} at ${*} in command: ${cmd}" >&2
	exit "$exit_code"
}

print_help() {
cat << EOF
Handle continuous integration tasks.

Options:
	-h|--help	Show this message

Subcommands:
	update-requirements		Update test requirements files
	test VARIANT			Run specified test variant
EOF
}

# shellcheck disable=SC2034
update_requirements_cmd() {
	declare selected=${1:-} i
	declare -a env1 env2 env3 env4
	# Some contrib extensions don't specify required Sphinx version in dependencies, yet fail on setup
	env1=(
		"Sphinx>=4,<5"
		"sphinxcontrib-applehelp<=1.0.5"
		"sphinxcontrib-devhelp<=1.0.2"
		"sphinxcontrib-htmlhelp<=2.0.1"
		"sphinxcontrib-serializinghtml<=1.1.5"
		"sphinxcontrib-qthelp<=1.0.3"
	)
	env2=("Sphinx>=5,<6")
	# ruamel.yaml deprecated compose_all in 0.18
	env3=("Sphinx>=5,<6" "ruamel.yaml>=0.17,<0.18")
	env4=("Sphinx>=6,<7")
	env5=("Sphinx>=7,<8")
	for i in {1..5}; do
		if [ -n "$selected" ] && [ "$i" != "$selected" ]; then
			continue
		fi
		declare -n constraints="env${i}"
		python3 -m venv --clear venv
		./venv/bin/pip install ".[test]" "${constraints[@]}"
		./venv/bin/pip freeze --exclude "sphinxcontrib-autoyaml" >"tests/requirements-${i}.txt"
		if [ "$selected" = "$i" ]; then
			break
		fi
	done
}

test_cmd() {
	declare env=$1
	python3 -m venv --clear venv
	./venv/bin/pip install --no-deps -r "tests/requirements-${env}.txt" .
	./venv/bin/python -m tests -v
}

main() {
	trap 'on_error ${BASH_SOURCE[0]}:${LINENO}' ERR

	declare subcommand
	subcommand=$1
	shift
	case "$subcommand" in
	update-requirements)
		update_requirements_cmd "$@"
		;;
	test)
		test_cmd "$@"
		;;
	-h|--help)
		print_help
		;;
	*)
		print_help
		echo "Unknown command: ${subcommand}" >&2
		return 1
	esac
}

main "$@"
