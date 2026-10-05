# Synthetic PostgreSQL restore rehearsal

IMPLEMENTED and locally TESTED: the script accepts only a loopback fixture connection. It creates two uniquely named databases, applies actual Alembic migrations, and seeds two synthetic organizations with the same SKU but different inventory quantities and audit events. It backs up with custom-format pg_dump, mutates the source after the backup, and restores into the separate empty target using pg_restore with a single transaction and exit-on-error.

It compares every restored table/row to the pre-backup snapshot, confirms later source changes are absent, and verifies the restored nonnegative quantity constraint still rejects invalid inventory. Both temporary databases and the temporary backup are removed; the supplied fixture database is never overwritten or dropped. The report contains a backup hash and counts, no credentials, user data or database dump.

Local October5 result: twelve tables, nine rows, exact snapshot match, post-backup source mutation excluded, constraint enforced, temporary databases removed. Dump/restore/check portion elapsed0.909seconds in this one tiny fixture. This is not an RTO, RPO, performance guarantee, RDS recovery, point-in-time recovery, encrypted/offsite backup, production permission or disaster-recovery claim. Hosted execution of this newly added CI step remains pending.

Prerequisites: PostgreSQL fixture credentials in TEST_POSTGRES_URL, permission to create/drop temporary databases, matching-or-newer pg_dump/pg_restore clients, and the project test environment installed. Set PYTHONPATH=apps/api and run `python scripts/verify_postgres_restore.py`. Do not run with production credentials or substitute a nonlocal endpoint. The script deliberately does not infer a default database URL.

Production gates remain: documented recovery point/objectives, least-privilege production roles, backup encryption and retention, offsite copy, RDS snapshot/PITR policies, real workload size, recovery-owner signoff, application/authentication verification after restore, and a timed operational rehearsal.
