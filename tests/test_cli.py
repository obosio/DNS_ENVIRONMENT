from __future__ import annotations

import unittest
from argparse import Namespace
from unittest.mock import call, patch

from dns_environment.cli import cmd_inspect
from dns_environment.inspector import (
    EXTERNAL_AUTHORITATIVE_SERVERS,
    FORWARD_ZONES,
    REVERSE_ZONES,
    InspectionReport,
)


class InspectorCliTests(unittest.TestCase):
    @patch("dns_environment.cli.inspect_zones")
    def test_reverse_zones_are_checked_only_in_external_view(
        self, mock_inspect_zones
    ) -> None:
        mock_inspect_zones.side_effect = [InspectionReport(), InspectionReport()]

        result = cmd_inspect(Namespace(reverse=True))

        self.assertEqual(result, 0)
        self.assertEqual(
            mock_inspect_zones.call_args_list,
            [
                call(zones=list(FORWARD_ZONES)),
                call(
                    zones=list(REVERSE_ZONES),
                    servers=EXTERNAL_AUTHORITATIVE_SERVERS,
                ),
            ],
        )
