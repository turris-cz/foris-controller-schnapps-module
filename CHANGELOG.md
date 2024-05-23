# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Changed
- build project using hatchling
- dependencies updates
- tests: Use tox to run tests and linter checks instead of using deprecated
  setuptools integration for such tasks.
- setup.py: Drop the unnecessary egg suffix in VCS links.
- setup.py: Remove obsolete setuptools keywords (`tests_require`,
  `setup_requires`, `dependency_links`, ...).
- tox: Use shared `tox.ini` for foris-controller and modules.
- Migrate CHANGELOG to Keep a Changelog style.

## [0.5] - 2020-11-25

- Add ability to perform factory reset

## [0.4] - 2020-04-21

- Raise description text length limit to 1024

## [0.3] - 2020-01-30

- Added "rollback" snapshot type to schema
- Limit snapshot description to 50 characters
- Fix snapshots types in schema and expand tests for these types

## [0.2] - 2019-12-05

- Handle a situation when module is triggered on a system without root btrfs

## [0.1] - 2019-11-30

- initial functionality
