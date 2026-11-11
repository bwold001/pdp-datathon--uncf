# Analysis v2 snapshots and replay

This implements the data-access foundation for [issue #48](https://github.com/bwold001/pdp-datathon--uncf/issues/48). All test data is synthetic. V2 HTTP routes and provider integration remain later work; the existing v1 endpoints keep their contracts.

## Transaction ownership

`analytics/data_access.py` owns one read transaction per execution. SQLite opens an explicitly selected existing file with `mode=ro`, begins a transaction and attaches the existing cancellation handler. PostgreSQL starts a read-only repeatable-read transaction and sets the remaining statement timeout before every query. Connections and cursors stay on the worker thread that opened the snapshot. Run the entire batch in that worker rather than dispatching individual steps to separate threads.

The snapshot exposes `named` and `positional` connection views of the same transaction. Each view supports `execute()` and `cursor()`; named fetches return dictionaries and positional fetches return tuples. Row factories are selected per cursor. Question-mark bindings in trusted owner SQL are translated for PostgreSQL while preserving quoted text and comments. This interface is for fixed calculation-owner queries, not model-authored SQL.

Pass `snapshot.positional` to `run_measure` and `read_answers`. Pass `snapshot=snapshot` to the public DFW list/detail, Credit momentum, Gateway courses, Student paths and filter-options wrappers. Those wrappers borrow the connection without closing it. Their existing path-based calls still work and own one local transaction for the whole page. `measures/data_access.py` contains only dependency-free protocols; measures do not import the analytics service.

Use `service.for_snapshot(snapshot)` for legacy catalog, clarification and analysis calls within a plan. These calls borrow the named view. A database error propagates to the outer snapshot owner rather than allowing a bound legacy adapter to mask an unusable transaction. Standalone SQLite and Playground's configured SQLite/PostgreSQL factories use the same implementation. An explicitly configured Playground source never falls back to the standalone extract.

`run_snapshot_steps` is an internal sequential execution primitive, not a public plan executor. It accepts up to four uniquely named trusted callbacks. A database failure or deadline stops subsequent callbacks, preserves completed in-memory results, and returns only after rollback and close. Its execution ID and UTC start/completion times are unique execution evidence. Its result is **internal**: the later facade must enforce dependencies, map typed outcomes, apply plan-wide disclosure to the actual returned set, and construct safe receipts before serializing anything. Ordinary unavailable/suppressed calculation results remain completed steps.

Page calculations retain the Explorer's `UNCF_MIN_STUDENTS` setting while borrowing a snapshot. The default of 1 shows small synthetic groups; an explicit setting of 10 still hides groups below 10. The DFW list still requires 10 final grades per listed course, and gateway course pairs still require 10 students. These eligibility cutoffs are separate from the configurable display threshold.

## Loaded data identity

The existing loader refresh transaction writes a nullable JSON `load_run.build_manifest` alongside all normalized rows. It contains schema version 1, a fresh load-generation UUID, a pipeline digest and a normalization digest. Pipeline identity includes implementation files, model package declaration and transformation runtime versions. Mapping, fixing and validation record the code/configuration identities they actually consumed in their staging metadata; loading `--staging` uses that evidence rather than pretending today's mapping/fixes built yesterday's artifacts. Loader rules and error-row policy are also included.

Legacy staged artifacts and fixed sample tables can have a blank manifest. V1 reads continue to work, but v2 requires a fresh complete pipeline run and reports `version_unavailable` for missing build evidence. Regenerate/reload through the documented loader; do not invent identity from file modification time. The committed sample `load_run.csv` deliberately carries no claim of a certified pipeline build.

Snapshot identity hashes the sorted logical `data_provider` source names/hashes together with generation, pipeline and normalization metadata, all read inside the execution transaction. Provider surrogate IDs, filesystem paths and load timestamps are excluded from the fingerprint. The safe identity includes a separately normalized UTC load timestamp. A reload changes the snapshot reference even when source bytes are identical. Copying the same loaded database between services preserves its identity; rebuilding under a different pipeline does not.

Supported refreshes use the loader's atomic transaction boundary. Do not edit normalized rows or replace a live SQLite file underneath a request outside that boundary. The manifest identifies loader generations, not arbitrary out-of-band database mutations. Preview verification of future API/chat transports must compare their snapshot and pipeline stamps before claiming parity.

## Reproducible computation

`make_replay_spec` exports the exact resolved `ExecutablePlan`, snapshot reference, operation/feature/method and catalog versions, executable implementation version, normalization and coverage digests, configuration/disclosure versions, and plan-level disclosure context. Required references are explicit; the caller must resolve them from its approved registry/configuration before calling. This helper does not attest to an arbitrary caller's version labels.

The versioned canonical encoding sorts object keys and declared sets while preserving step/comparison order and dependency meaning. Fingerprints exclude execution IDs, timestamps and durations. `step_fingerprint` includes the whole plan fingerprint so a sibling or dependency that changes disclosure cannot reuse an isolated step's key. Future cache keys must use these stable computation inputs; no exploration-result cache is added here.

`validate_replay` requires the exact available snapshot and original versions/configuration. An overwritten generation produces `snapshot_unavailable`; mismatching computation versions/configuration produce `version_unavailable`. It also rejects a corrupted exported fingerprint. No historical snapshot or implementation archive is added.

## Verification

Run the root `.venv` tests and `make check-fast`, then `make check` before publication. The snapshot tests use real SQLite transactions, a concurrent committed reload, independently specified retention/credit values, every page wrapper, timeout and failure cleanup, fingerprint changes and replay refusals. Loader tests verify stage identity and atomic rollback of rows plus metadata. Playground server tests verify its configured source and v1 compatibility.

`analytics/tests/test_snapshots_postgres.py` runs a disposable-schema integration case when `PDP_TEST_POSTGRES_URL` is configured; `PDP_REQUIRE_POSTGRES=1` makes an absent environment fail. It exercises real named/positional cursors, legacy analysis, a page reader, source-stamp equality and read-only repeatable-read setup. A skipped PostgreSQL test means backend parity remains unverified. No preview/API stamp check or live-provider evaluation is claimed by these internal tests.
