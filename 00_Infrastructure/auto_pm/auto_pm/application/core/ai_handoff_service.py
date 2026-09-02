"""AI skill handoff contract and transactional inbox service.

The inbox is a short-lived execution message. It is deliberately not a
second project ledger: only the PM workflow may consume a handoff and write
the result to PM_SESSION or cockpit feedback.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


class HandoffError(RuntimeError):
    """Base error for invalid or unsafe handoff operations."""


class HandoffValidationError(HandoffError, ValueError):
    """Raised when a request or closure result violates handoff.v1."""


class HandoffConflictError(HandoffError):
    """Raised when an idempotency key is reused with different content."""


class HandoffNotFoundError(HandoffError):
    """Raised when a requested handoff does not exist."""


class AiHandoffService:
    """Create, inspect, and atomically consume ``handoff.v1`` messages."""

    SCHEMA_VERSION = "handoff.v1"
    REQUIRED_FIELDS = ("request_id", "project_id", "executor_skill", "summary")
    ALLOWED_EXECUTOR_SKILLS = frozenset({"fullstack-engineer", "plc-electrical-engineer"})
    ALLOWED_STATUSES = frozenset({"pending", "in_progress", "completed", "failed", "consumed"})
    STATUS_ORDER = ("pending", "in_progress", "completed", "failed", "consumed")
    REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{2,79}$")
    LOCK_STALE_SECONDS = 300
    RESULT_FIELDS = (
        "summary",
        "changed_files",
        "verification",
        "risks",
        "next_actions",
        "watchouts",
        "read_first",
        "artifacts",
        "chg_updates",
        "product_impact",
        "pm_closure",
    )

    DEFAULT_VERIFICATION = {
        "lint_result": "",
        "test_result": "",
        "other_checks": [],
        "not_run": [],
    }
    DEFAULT_PRODUCT_IMPACT = {
        "hypothesis_id": "",
        "impact_type": "general",
        "engineering_signal": "",
        "verification_mode": "code_static",
        "validation_stage": "",
        "needs_user_validation": False,
        "assumption_affected": "",
        "observable_signal": "",
    }
    DEFAULT_PM_CLOSURE = {
        "required": True,
        "suggested_event": "iteration",
        "suggested_status": "pending_review",
    }

    def __init__(self, workspace_root: str | Path) -> None:
        self._workspace_root = Path(workspace_root).resolve()

    @property
    def inbox_dir(self) -> Path:
        return self._workspace_root / ".auto-pm" / "handoffs"

    @property
    def failure_dir(self) -> Path:
        """Return the ignored evidence directory for failed Saga attempts."""
        return self._workspace_root / ".auto-pm" / "reports" / "dogfood" / "handoff-saga"

    def create_request(
        self,
        project_id: str,
        executor_skill: str,
        summary: str,
        *,
        goal: str = "",
        mode: str = "execution",
        specs: list[str] | None = None,
        read_first: list[str] | None = None,
        request_id: str = "",
        skill_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a pending request, or return the same request idempotently."""
        self._validate_scalar(project_id, "project_id")
        if executor_skill not in self.ALLOWED_EXECUTOR_SKILLS:
            raise HandoffValidationError(f"executor_skill 不受支持: {executor_skill}")
        self._validate_scalar(summary, "summary")
        if mode not in {"grooming", "execution"}:
            raise HandoffValidationError("mode 必须是 grooming 或 execution")

        resolved_request_id = request_id or self._new_request_id()
        self._validate_request_id(resolved_request_id)
        generated_at = datetime.now(UTC).isoformat()
        context = dict(skill_context or {})
        context.setdefault("goal", goal)
        context.setdefault("mode", mode)
        context.setdefault("injected_specs", list(specs or []))
        context.setdefault("baseline_documents", list(read_first or []))

        payload: dict[str, Any] = {
            "schema_version": self.SCHEMA_VERSION,
            "request_id": resolved_request_id,
            "project_id": project_id,
            "executor_skill": executor_skill,
            "summary": summary,
            "status": "pending",
            "mode": mode,
            "goal": goal,
            "generated_at": generated_at,
            "created_by": "pm-workflow",
            "skill_context": context,
            "idempotency_key": resolved_request_id,
            "changed_files": [],
            "risks": [],
            "next_actions": [],
            "watchouts": [],
            "read_first": list(read_first or []),
            "artifacts": [],
            "chg_updates": [],
            "verification": self._copy_default(self.DEFAULT_VERIFICATION),
            "product_impact": self._copy_default(self.DEFAULT_PRODUCT_IMPACT),
            "pm_closure": self._copy_default(self.DEFAULT_PM_CLOSURE),
        }

        path = self._path_for_request(resolved_request_id)
        with self._transaction_lock():
            if path.exists():
                existing = self._read_valid(path)
                if existing is None:
                    raise HandoffConflictError(f"交接文件已存在但不可读取: {path.name}")
                if self._same_request(existing, payload):
                    existing["file"] = str(path)
                    return existing
                raise HandoffConflictError(f"request_id 已存在且内容不同: {resolved_request_id}")
            self._write_atomic(path, payload)
        payload["file"] = str(path)
        return payload

    def list_pending(self, project_id: str = "") -> list[dict[str, Any]]:
        """Return valid pending handoffs, newest first, optionally by project."""
        return self.list_requests(project_id=project_id, status="pending")

    def list_requests(
        self,
        project_id: str = "",
        status: str = "",
    ) -> list[dict[str, Any]]:
        """Return valid inbox records, including consumed records when requested."""
        if not self.inbox_dir.is_dir():
            return []
        if status and status not in self.ALLOWED_STATUSES:
            raise HandoffValidationError(f"不支持的 handoff status: {status}")

        handoffs: list[dict[str, Any]] = []
        for path in sorted(self.inbox_dir.glob("*.json")):
            payload = self._read_valid(path)
            if payload is None:
                continue
            if status and payload.get("status", "pending") != status:
                continue
            if project_id and payload.get("project_id") != project_id:
                continue
            payload["file"] = str(path)
            handoffs.append(payload)
        return sorted(
            handoffs,
            key=lambda item: str(item.get("closed_at") or item.get("generated_at") or ""),
            reverse=True,
        )

    def queue_snapshot(self, project_id: str = "", *, limit: int = 10) -> dict[str, Any]:
        """Return a read-only aggregate view of the handoff inbox."""
        if limit < 1 or limit > 100:
            raise HandoffValidationError("queue limit 必须在 1 到 100 之间")

        requests = self.list_requests(project_id=project_id)
        counts = dict.fromkeys(self.STATUS_ORDER, 0)
        failure_by_request: dict[str, int] = {}
        failure_total = 0
        for request in requests:
            status = str(request.get("status", "pending"))
            if status in counts:
                counts[status] += 1
            request_id = str(request.get("request_id", ""))
            events = self.list_failure_events(request_id)
            if events:
                failure_by_request[request_id] = len(events)
                failure_total += len(events)

        return {
            "schema_version": "handoff.queue.v1",
            "project_id": project_id,
            "as_of": datetime.now(UTC).isoformat(),
            "read_only": True,
            "total": len(requests),
            "status_counts": counts,
            "failure_events": {
                "total": failure_total,
                "by_request": failure_by_request,
            },
            "latest": requests[:limit],
        }

    def get_pending(self, request_id: str) -> dict[str, Any] | None:
        """Return one valid pending handoff by request id."""
        payload = self.get_request(request_id)
        if payload is None or payload.get("status", "pending") != "pending":
            return None
        return payload

    def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Return one valid handoff regardless of its lifecycle status."""
        self._validate_request_id(request_id)
        path = self._find_request_path(request_id)
        payload = self._read_valid(path)
        if payload is not None and payload.get("request_id") == request_id:
            payload["file"] = str(path)
            return payload
        return None

    def preflight_close(
        self,
        request_id: str,
        *,
        result: Mapping[str, Any] | None = None,
        idempotency_key: str = "",
        expected_project_id: str = "",
        expected_executor_skill: str = "",
    ) -> dict[str, Any]:
        """Validate a close without changing the handoff or PM ledgers."""
        self._validate_request_id(request_id)
        with self._transaction_lock():
            path = self._find_request_path(request_id)
            current = self._read_valid(path)
            if current is None:
                raise HandoffNotFoundError(f"找不到有效 handoff: {request_id}")
            self._validate_expected_identity(
                current,
                project_id=expected_project_id,
                executor_skill=expected_executor_skill,
            )
            merged, effective_key, fingerprint = self._prepare_close_payload(
                current,
                result or {},
                idempotency_key,
            )
            if current.get("status") == "consumed":
                old_closure = current.get("closure")
                if isinstance(old_closure, dict) and (
                    old_closure.get("idempotency_key") == effective_key
                    and old_closure.get("fingerprint") == fingerprint
                ):
                    return {
                        "ok": True,
                        "already_consumed": True,
                        "request_id": request_id,
                        "project_id": current["project_id"],
                        "fingerprint": fingerprint,
                        "idempotency_key": effective_key,
                        "file": str(path),
                    }
                raise HandoffConflictError(
                    f"handoff 已消费，不能使用不同结果重复关闭: {request_id}"
                )
            self._validate_closure(merged)
            return {
                "ok": True,
                "already_consumed": False,
                "request_id": request_id,
                "project_id": current["project_id"],
                "executor_skill": current["executor_skill"],
                "fingerprint": fingerprint,
                "idempotency_key": effective_key,
                "file": str(path),
            }

    def list_failure_events(self, request_id: str) -> list[dict[str, Any]]:
        """Read failure evidence for one request without changing runtime state."""
        self._validate_request_id(request_id)
        path = self.failure_dir / f"{request_id}.json"
        if not path.is_file():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            return []
        events = payload.get("events") if isinstance(payload, dict) else None
        return list(events) if isinstance(events, list) else []

    def retry_close(
        self,
        request_id: str,
        *,
        result: Mapping[str, Any] | None = None,
        idempotency_key: str = "",
        actor: str = "pm-workflow",
    ) -> dict[str, Any]:
        """Retry a failed close using the same idempotent close protocol."""
        return self.close_request(
            request_id,
            result=result,
            idempotency_key=idempotency_key,
            actor=actor,
        )

    def close_request(
        self,
        request_id: str,
        *,
        result: Mapping[str, Any] | None = None,
        idempotency_key: str = "",
        actor: str = "pm-workflow",
    ) -> dict[str, Any]:
        """Validate and atomically consume one handoff.

        A repeated close with the same semantic result is idempotent. A
        different result or idempotency key is rejected instead of silently
        overwriting an already-consumed message.
        """
        self._validate_request_id(request_id)
        if not actor.strip():
            raise HandoffValidationError("actor 不能为空")
        try:
            with self._transaction_lock():
                path = self._find_request_path(request_id)
                current = self._read_valid(path)
                if current is None:
                    raise HandoffNotFoundError(f"找不到有效 handoff: {request_id}")

                merged, effective_key, fingerprint = self._prepare_close_payload(
                    current,
                    result or {},
                    idempotency_key,
                )
                old_closure = current.get("closure")
                if current.get("status") == "consumed":
                    if isinstance(old_closure, dict) and (
                        old_closure.get("idempotency_key") == effective_key
                        and old_closure.get("fingerprint") == fingerprint
                    ):
                        current["file"] = str(path)
                        return current
                    raise HandoffConflictError(
                        f"handoff 已消费，不能使用不同结果重复关闭: {request_id}"
                    )

                self._validate_closure(merged)
                now = datetime.now(UTC).isoformat()
                merged.update(
                    {
                        "schema_version": self.SCHEMA_VERSION,
                        "status": "consumed",
                        "closed_at": now,
                        "consumed_at": now,
                        "closed_by": actor,
                        "idempotency_key": effective_key,
                        "closure": {
                            "idempotency_key": effective_key,
                            "fingerprint": fingerprint,
                            "closed_by": actor,
                        },
                    }
                )
                self._write_atomic(path, merged)
            merged["file"] = str(path)
            return merged
        except HandoffError as error:
            self._record_failure(request_id, error, phase="preflight")
            raise
        except OSError as error:
            self._record_failure(request_id, error, phase="commit")
            raise HandoffError(f"handoff 写入失败，可安全重试: {request_id}") from error

    def validate_product_impact(self, product_impact: dict[str, Any]) -> dict[str, Any]:
        """Validate product_impact against anti-emptiness rules."""
        hypothesis_id = str(product_impact.get("hypothesis_id", "")).strip()
        signal = str(product_impact.get("engineering_signal", "")).strip()

        warnings: list[str] = []
        if not hypothesis_id:
            warnings.append("缺少 hypothesis_id（未关联产品假设）")
        if not signal:
            warnings.append("缺少 engineering_signal（未描述具体物理/交互可观测信号）")
        elif len(signal) < 8 and any(
            kw in signal for kw in ("优化", "完成", "修改", "修复", "改进")
        ):
            warnings.append("engineering_signal 过于泛化（缺乏具体物理量/交互量）")

        return {"valid": len(warnings) == 0, "warnings": warnings}

    def _read_valid(self, path: Path) -> dict[str, Any] | None:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
            payload = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        if any(not str(payload.get(field, "")).strip() for field in self.REQUIRED_FIELDS):
            return None
        return self._normalize_payload(payload)

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        normalized["schema_version"] = str(
            payload.get("schema_version", self.SCHEMA_VERSION) or self.SCHEMA_VERSION
        )
        normalized["status"] = str(payload.get("status", "pending") or "pending")
        normalized["mode"] = str(payload.get("mode", "execution") or "execution")
        normalized["changed_files"] = self._normalize_list(payload.get("changed_files"))
        normalized["risks"] = self._normalize_list(payload.get("risks"))
        normalized["next_actions"] = self._normalize_list(payload.get("next_actions"))
        normalized["watchouts"] = self._normalize_list(payload.get("watchouts"))
        normalized["read_first"] = self._normalize_list(payload.get("read_first"))
        normalized["artifacts"] = self._normalize_list(payload.get("artifacts"))
        normalized["chg_updates"] = self._normalize_list(payload.get("chg_updates"))
        normalized["verification"] = self._normalize_mapping(
            payload.get("verification"), self.DEFAULT_VERIFICATION
        )

        pi = self._normalize_mapping(payload.get("product_impact"), self.DEFAULT_PRODUCT_IMPACT)
        # Bidirectional aliases preserve compatibility with earlier payloads.
        if not pi["hypothesis_id"] and pi.get("assumption_affected"):
            pi["hypothesis_id"] = str(pi["assumption_affected"])
        if not pi.get("assumption_affected") and pi["hypothesis_id"]:
            pi["assumption_affected"] = pi["hypothesis_id"]
        if not pi["engineering_signal"] and pi.get("observable_signal"):
            pi["engineering_signal"] = str(pi["observable_signal"])
        if not pi.get("observable_signal") and pi["engineering_signal"]:
            pi["observable_signal"] = pi["engineering_signal"]

        normalized["product_impact"] = pi
        normalized["pm_closure"] = self._normalize_mapping(
            payload.get("pm_closure"), self.DEFAULT_PM_CLOSURE
        )
        return normalized

    def _merge_result(
        self,
        current: dict[str, Any],
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        merged = self._normalize_payload(dict(current))
        for field in self.RESULT_FIELDS:
            if field not in result:
                continue
            value = result[field]
            if field in {
                "changed_files",
                "risks",
                "next_actions",
                "watchouts",
                "read_first",
                "artifacts",
                "chg_updates",
            }:
                merged[field] = self._normalize_list(value)
            elif field in {"verification", "product_impact", "pm_closure"}:
                defaults: Mapping[str, Any]
                if field == "verification":
                    defaults = self.DEFAULT_VERIFICATION
                elif field == "product_impact":
                    defaults = self.DEFAULT_PRODUCT_IMPACT
                else:
                    defaults = self.DEFAULT_PM_CLOSURE
                merged[field] = self._normalize_mapping(value, defaults)
            elif str(value).strip():
                merged[field] = str(value).strip()
        return merged

    def _prepare_close_payload(
        self,
        current: dict[str, Any],
        result: Mapping[str, Any],
        idempotency_key: str,
    ) -> tuple[dict[str, Any], str, str]:
        merged = self._merge_result(current, result)
        effective_key = str(
            idempotency_key or current.get("idempotency_key") or current["request_id"]
        ).strip()
        if not effective_key:
            raise HandoffValidationError("idempotency_key 不能为空")
        fingerprint = self._fingerprint(self._closure_projection(merged))
        return merged, effective_key, fingerprint

    def _validate_expected_identity(
        self,
        payload: Mapping[str, Any],
        *,
        project_id: str,
        executor_skill: str,
    ) -> None:
        if project_id and payload.get("project_id") != project_id:
            raise HandoffConflictError(
                f"项目不匹配: 期望 {project_id}，实际 {payload.get('project_id')}"
            )
        if executor_skill and payload.get("executor_skill") != executor_skill:
            raise HandoffConflictError(
                f"执行技能不匹配: 期望 {executor_skill}，实际 {payload.get('executor_skill')}"
            )

    def _validate_closure(self, payload: Mapping[str, Any]) -> None:
        if not str(payload.get("summary", "")).strip():
            raise HandoffValidationError("关闭 handoff 必须提供 summary")
        verification = payload.get("verification")
        evidence: list[Any] = []
        if isinstance(verification, Mapping):
            evidence.extend(
                value
                for key in ("lint_result", "test_result", "other_checks")
                if (value := verification.get(key))
            )
        evidence.extend(payload.get("artifacts") or [])
        if not evidence:
            raise HandoffValidationError("关闭 handoff 必须提供至少一项验证证据")
        changed_files = payload.get("changed_files") or []
        chg_updates = payload.get("chg_updates") or []
        if changed_files and not chg_updates:
            raise HandoffValidationError(
                "存在 changed_files 时必须提供 chg_updates，禁止无变更单收口"
            )

    def _closure_projection(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "request_id": payload.get("request_id"),
            "project_id": payload.get("project_id"),
            "executor_skill": payload.get("executor_skill"),
            "summary": payload.get("summary"),
            **{field: payload.get(field) for field in self.RESULT_FIELDS},
        }

    def _same_request(
        self,
        existing: Mapping[str, Any],
        requested: Mapping[str, Any],
    ) -> bool:
        fields = (
            "project_id",
            "executor_skill",
            "summary",
            "mode",
            "goal",
            "skill_context",
        )
        return all(existing.get(field) == requested.get(field) for field in fields)

    def _path_for_request(self, request_id: str) -> Path:
        self._validate_request_id(request_id)
        return self.inbox_dir / f"{request_id}.json"

    def _find_request_path(self, request_id: str) -> Path:
        """Resolve canonical paths and legacy files whose names differ."""
        path = self._path_for_request(request_id)
        if path.is_file():
            return path
        for candidate in sorted(self.inbox_dir.glob("*.json")):
            payload = self._read_valid(candidate)
            if payload is not None and payload.get("request_id") == request_id:
                return candidate
        return path

    def _new_request_id(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        return f"AI-{timestamp}-{uuid.uuid4().hex[:8].upper()}"

    def _validate_request_id(self, request_id: str) -> None:
        if not self.REQUEST_ID_RE.fullmatch(request_id):
            raise HandoffValidationError("request_id 包含非法字符或长度不合法")

    def _validate_scalar(self, value: str, field: str) -> None:
        if not str(value).strip():
            raise HandoffValidationError(f"{field} 不能为空")
        if any(char in str(value) for char in ("/", "\\", "..")):
            raise HandoffValidationError(f"{field} 包含非法路径字符")

    def _normalize_list(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def _normalize_mapping(
        self,
        value: Any,
        defaults: Mapping[str, Any],
    ) -> dict[str, Any]:
        normalized = self._copy_default(defaults)
        if isinstance(value, Mapping):
            for key in defaults:
                if key in value:
                    normalized[key] = value[key]
        return normalized

    def _copy_default(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(json.dumps(value, ensure_ascii=False)))

    def _fingerprint(self, value: Mapping[str, Any]) -> str:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8", errors="replace")
        return hashlib.sha256(encoded).hexdigest()

    @contextmanager
    def _transaction_lock(self) -> Iterator[None]:
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.inbox_dir / ".handoff.lock"
        descriptor: int | None = None
        for _ in range(100):
            try:
                descriptor = os.open(
                    lock_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                os.write(descriptor, str(os.getpid()).encode("ascii"))
                break
            except FileExistsError:
                try:
                    if time.time() - lock_path.stat().st_mtime > self.LOCK_STALE_SECONDS:
                        lock_path.unlink()
                        continue
                except OSError:
                    pass
                time.sleep(0.05)
        if descriptor is None:
            raise HandoffError("获取 handoff 事务锁超时")

        try:
            yield
        finally:
            try:
                os.close(descriptor)
            finally:
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass

    def _write_atomic(self, path: Path, payload: Mapping[str, Any]) -> None:
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self.inbox_dir / f".{path.name}.{uuid.uuid4().hex}.tmp"
        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
                errors="replace",
                newline="\n",
            ) as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, path)
        finally:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass

    def _record_failure(self, request_id: str, error: Exception, *, phase: str) -> None:
        """Persist retry evidence without masking the original failure."""
        try:
            self.failure_dir.mkdir(parents=True, exist_ok=True)
            path = self.failure_dir / f"{request_id}.json"
            existing: dict[str, Any] = {
                "schema_version": "handoff.failure.v1",
                "request_id": request_id,
                "events": [],
            }
            if path.is_file():
                try:
                    loaded = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                    if isinstance(loaded, dict):
                        existing.update(loaded)
                except (OSError, json.JSONDecodeError):
                    pass
            events = existing.get("events")
            if not isinstance(events, list):
                events = []
            events.append(
                {
                    "event_id": uuid.uuid4().hex,
                    "request_id": request_id,
                    "occurred_at": datetime.now(UTC).isoformat(),
                    "phase": phase,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "retryable": True,
                }
            )
            existing["events"] = events
            temp_path = self.failure_dir / f".{path.name}.{uuid.uuid4().hex}.tmp"
            try:
                with temp_path.open(
                    "w",
                    encoding="utf-8",
                    errors="replace",
                    newline="\n",
                ) as stream:
                    json.dump(existing, stream, ensure_ascii=False, indent=2)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp_path, path)
            finally:
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass
        except (OSError, TypeError, ValueError):
            return
