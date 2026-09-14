# Local decision audit

Every valid API or web evaluation emits one schema-1.0 Pydantic event through
an AuditSink. JsonlAuditSink appends UTF-8 JSON plus a newline synchronously
to logs/audit.jsonl. MemoryAuditSink is used by tests and the Golden Dataset.
The service remains callable without a sink and performs no log writes.

The event contains context (channel, internal scenario ID, application/build,
policy and canonical corpus hash), pseudonymized input, deterministic decision
and candidate criteria, citation IDs and fidelity counts, cost and processing
latency. The full contract is defined in src/trustreply/audit.py.
It never contains question text, draft text, excerpts or matching words.

The default key is random and stays in process memory. For stable local
fingerprints, set TRUSTREPLY_AUDIT_HMAC_KEY to a private random value in the
PowerShell environment before starting Uvicorn. Do not commit it. There is no
automatic .env loading and no key-rotation manager. Without that variable,
fingerprints change on server restart/reload; trace IDs still identify records.
HMAC uses casefolded, whitespace-normalized UTF-8 text; this is pseudonymization,
not anonymization. Logs contain document IDs and require local access control.

Optionally identify the tested build before launching:

```powershell
$env:TRUSTREPLY_BUILD_REVISION = git rev-parse HEAD
.\.venv\Scripts\uvicorn.exe trustreply.app:app --app-dir src --reload
```

The revision describes the commit only; it does not certify uncommitted changes.
Open the demo, submit a question or click an example, then inspect:

```powershell
Get-Content .\logs\audit.jsonl -Tail 1 | ConvertFrom-Json | Format-List
```

Match trace_id to the page or X-Trace-ID header. The browser uses POST and
stays on `/`. Old manually constructed question URLs can still enter access
logs; POST cannot erase historical browser/proxy logs. GET no longer evaluates.
Invalid input and the initial empty page produce no decision event.

If writing fails, the result is still returned, with an audit_write_failed
operational error containing only its trace ID. Such an event may be lost;
there is no retry or durable acknowledgement. Event/schema validation errors
are not swallowed as transport failures.

Use one server process: the shared sink locks threads, not multiple workers.
There is no fsync durability guarantee, immutable storage, rotation or automatic
retention. A crash can leave a partial final line. Logs are local and ignored by
Git; they are not synchronized between PCs. Processing latency excludes event
construction and disk append; actual response time includes both and slow disk
can delay it. No zero-overhead guarantee is claimed.

Fidelity remains the existing extractive check against returned cited excerpts
and known document IDs, not semantic entailment or independent excerpt integrity
verification. Audit records report those checks; they add no new generation
guarantee or LLM call.
