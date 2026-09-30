# ADR-001: Modular monolith first

Status: Accepted (design)

Ops Intelligence starts as one FastAPI deployable with explicit module boundaries. Service extraction is deferred until measured scaling, ownership, or failure-isolation needs justify it.
