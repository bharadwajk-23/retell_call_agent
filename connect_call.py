#!/usr/bin/env python3
"""
Standalone script to place an outbound call via Retell AI.
Run from project root:

  set RETELL_API_KEY=...
  set RETELL_AGENT_ID=...
  set RETELL_FROM_NUMBER=+1...

  python connect_call.py +14155550101
"""

from __future__ import annotations

import argparse
import os
import sys

_BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

import config  # noqa: E402 — loads backend/.env
from retell_service import trigger_outbound_call  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Retell AI outbound phone call.")
    parser.add_argument("phone", help="Destination number (E.164)")
    parser.add_argument("--patient-name", default="Demo Patient")
    parser.add_argument("--provider-name", default="Dr Demo")
    parser.add_argument("--missed-days", type=int, default=0)
    args = parser.parse_args()

    if not config.RETELL_API_KEY and not config.RETELL_MOCK_CALLS:
        print("Error: RETELL_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    from_number = config.RETELL_FROM_NUMBER
    if not from_number and not config.RETELL_MOCK_CALLS:
        print("Error: RETELL_FROM_NUMBER is not set.", file=sys.stderr)
        sys.exit(1)
    if not from_number:
        from_number = "+10000000000"

    result = trigger_outbound_call(
        phone_number=args.phone,
        from_number=from_number,
        patient_name=args.patient_name,
        provider_name=args.provider_name,
        exercise_missed_days=args.missed_days,
        agent_id=config.RETELL_AGENT_ID or None,
    )

    if not result:
        print("Failed to create call.", file=sys.stderr)
        sys.exit(2)

    call_id = getattr(result, "call_id", None)
    print(f"Call created: call_id={call_id!r}")


if __name__ == "__main__":
    main()
