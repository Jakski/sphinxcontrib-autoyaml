#!/usr/bin/env bash

set -euo pipefail -o errtrace
shopt -s inherit_errexit nullglob

on_error() {
	declare exit_code=$? cmd=$BASH_COMMAND
	echo "Failing with code ${exit_code} at ${*} in command: ${cmd}" >&2
	exit "$exit_code"
}

restore_lockfile() {
	if [ -e poetry.lock.save ]; then
		echo "Restoring original poetry.lock file..."
		mv poetry.lock.save poetry.lock
	fi
}

restore_pyproject() {
	if [ -e pyproject.toml.save ]; then
		echo "Restoring original pyproject.toml file..."
		mv pyproject.toml.save pyproject.toml
	fi
}

on_exit() {
	restore_lockfile
	restore_pyproject
}

ensure_poetry() {
	if which poetry >/dev/null; then
		return 0
	fi
	echo "Ensuring Poetry is installed..."
	mkdir -p "${HOME}/.local/lib"
	declare poetry_venv_path
	poetry_venv_path="${HOME}/.local/lib/poetry_venv"
	if [ ! -e "$poetry_venv_path" ]; then
		python3 -m venv --upgrade-deps  "$poetry_venv_path"
	fi
	if [ ! -e "${poetry_venv_path}/bin/poetry" ]; then
		"${poetry_venv_path}/bin/pip" install "poetry==1.3.2"
	fi
	mkdir -p "${HOME}/.local/bin"
	ln -sf "${poetry_venv_path}/bin/poetry" "${HOME}/.local/bin/poetry"
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

# Poetry doesn't implement `--constraint` flag like pip. Yet we want to ensure
# that tests run always with the same dependency versions.
update_requirements_cmd() {
	cp pyproject.toml pyproject.toml.save
	cp poetry.lock poetry.lock.save
	declare sphinx_version
	for sphinx_version in 3 4 5; do
		poetry add --lock "Sphinx@^${sphinx_version}"
		poetry export --with dev --output "requirements-sphinx${sphinx_version}.txt"
		cp poetry.lock.save poetry.lock
	done
	rm poetry.lock.save
	mv pyproject.toml.save pyproject.toml
}

test_cmd() {
	declare requirements=$1
	declare wheel_file
	for wheel_file in ./dist/*.whl; do
		rm "$wheel_file"
	done
	poetry install --verbose
	poetry build --format wheel
	python3 -m venv --clear venv
	./venv/bin/pip install --no-deps -r "requirements-${requirements}.txt"
	./venv/bin/pip install --no-deps ./dist/*.whl
	./venv/bin/python -m tests -v
}

main() {
	trap 'on_error ${BASH_SOURCE[0]}:${LINENO}' ERR
	trap on_exit EXIT
	ensure_poetry

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
