from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Any

import yaml

DISPOSITIONS = {
    "dedicated_exception",
    "migration_candidate",
    "owner_decision_required",
    "preserve_pending_dedicated_cutover",
    "active_shared_endpoint",
    "retirement_pending",
}
ACCESS_CLASSES = {
    "public_standard_service",
    "public_native_protocol",
    "restricted_admin",
    "internal_only",
    "network_identity",
    "mixed_service_identity",
    "unresolved",
    "retired",
}


class ReconciliationValidationError(ValueError):
    pass


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReconciliationValidationError(f"{field} must be a mapping")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReconciliationValidationError(f"{field} must be a list")
    return value


def require_text(entry: dict[str, Any], field: str, service: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ReconciliationValidationError(
            f"{service}: {field} must be non-empty text"
        )
    return value


def validate_reconciliation(document: Any) -> dict[str, int]:
    if isinstance(document, dict) and "reconciliation" in document and "metadata" not in document:
        reconciliation = require_mapping(document.get("reconciliation"), "reconciliation")
    else:
        reconciliation = require_mapping(document, "reconciliation")
    metadata = require_mapping(reconciliation.get("metadata"), "metadata")
    counts = require_mapping(metadata.get("counts"), "metadata.counts")
    access_class_policy = require_mapping(
        metadata.get("access_class_policy"), "metadata.access_class_policy"
    )
    serials = require_mapping(reconciliation.get("zone_serials"), "zone_serials")
    services = require_list(reconciliation.get("services"), "services")
    aliases = require_mapping(reconciliation.get("aliases"), "aliases")

    if metadata.get("live_changes_authorized") is not False:
        raise ReconciliationValidationError(
            "metadata.live_changes_authorized must remain false for this audit"
        )
    if len(serials) != 7:
        raise ReconciliationValidationError("zone_serials must contain seven zones")
    if counts.get("reconciled_public_addresses") != len(services):
        raise ReconciliationValidationError(
            "metadata count does not match reconciled services"
        )
    if set(access_class_policy) != ACCESS_CLASSES:
        raise ReconciliationValidationError(
            "metadata.access_class_policy must document every supported access class"
        )

    seen_addresses: set[str] = set()
    forward_addresses = 0
    disposition_counts: dict[str, int] = {}
    for index, raw_service in enumerate(services):
        service = require_mapping(raw_service, f"services[{index}]")
        address = require_text(service, "public_address", f"services[{index}]")
        ipaddress.ip_address(address)
        if address in seen_addresses:
            raise ReconciliationValidationError(
                f"{address}: public address is duplicated"
            )
        seen_addresses.add(address)

        names = require_list(service.get("dns_a_names"), f"{address}.dns_a_names")
        if any(not isinstance(name, str) or not name for name in names):
            raise ReconciliationValidationError(
                f"{address}: dns_a_names must contain non-empty names"
            )
        if names:
            forward_addresses += 1
        ptr_name = service.get("ptr_name")
        if ptr_name is not None and (
            not isinstance(ptr_name, str) or not ptr_name.strip()
        ):
            raise ReconciliationValidationError(
                f"{address}: ptr_name must be null or non-empty text"
            )

        disposition = require_text(service, "disposition", address)
        if disposition not in DISPOSITIONS:
            raise ReconciliationValidationError(
                f"{address}: unknown disposition {disposition}"
            )
        disposition_counts[disposition] = (
            disposition_counts.get(disposition, 0) + 1
        )
        for field in (
            "observed_site",
            "router_assignment",
            "nat_summary",
            "role",
        ):
            require_text(service, field, address)
        access_class = require_text(service, "access_class", address)
        if access_class not in ACCESS_CLASSES:
            raise ReconciliationValidationError(
                f"{address}: unknown access_class {access_class}"
            )
        high_port_eligible = service.get("high_port_migration_eligible")
        if not isinstance(high_port_eligible, bool):
            raise ReconciliationValidationError(
                f"{address}: high_port_migration_eligible must be boolean"
            )
        if high_port_eligible and access_class != "restricted_admin":
            raise ReconciliationValidationError(
                f"{address}: only restricted_admin services may be high-port migration candidates"
            )
        migration_eligible = service.get("migration_eligible")
        if migration_eligible not in {True, False, "conditional"}:
            raise ReconciliationValidationError(
                f"{address}: migration_eligible must be true, false, or conditional"
            )
        blockers = require_list(service.get("blockers"), f"{address}.blockers")
        if any(
            not isinstance(blocker, str) or not blocker.strip()
            for blocker in blockers
        ):
            raise ReconciliationValidationError(
                f"{address}: blockers must contain non-empty entries"
            )

    dedicated_mail = require_mapping(aliases.get("dedicated_mail"), "aliases.dedicated_mail")
    mail_targets = require_list(dedicated_mail.get("targets"), "aliases.dedicated_mail.targets")
    mail_aliases = require_list(dedicated_mail.get("aliases"), "aliases.dedicated_mail.aliases")
    if len(mail_targets) != 3 or len(mail_aliases) != 12:
        raise ReconciliationValidationError(
            "aliases.dedicated_mail must contain three targets and 12 aliases"
        )

    apex_dependencies = require_mapping(
        aliases.get("apex_dependencies"), "aliases.apex_dependencies"
    )
    if set(apex_dependencies) != {
        "aero.com.ar",
        "polodesalud.com.ar",
    }:
        raise ReconciliationValidationError(
            "aliases.apex_dependencies must cover aero and polodesalud"
        )

    require_mapping(aliases.get("unresolved_targets"), "aliases.unresolved_targets")
    retired_targets = require_mapping(
        aliases.get("retired_targets"), "aliases.retired_targets"
    )
    if "services.aero.com.ar" not in retired_targets:
        raise ReconciliationValidationError(
            "aliases.retired_targets must cover services.aero.com.ar"
        )

    if counts.get("unique_forward_addresses") != forward_addresses:
        raise ReconciliationValidationError(
            "unique_forward_addresses does not match services with A records"
        )
    return {
        "services": len(services),
        "forward_addresses": forward_addresses,
        **disposition_counts,
    }


def load_reconciliation(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {"reconciliation": data}
