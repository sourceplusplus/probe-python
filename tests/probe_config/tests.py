import unittest
from unittest import mock

from sourceplusplus.SourcePlusPlus import SourcePlusPlus


class TestSum(unittest.TestCase):

    def test_default_config(self):
        spp = SourcePlusPlus()
        self.assertEqual("localhost", spp.probe_config["spp"]["platform_host"])
        self.assertEqual(12800, spp.probe_config["spp"]["platform_port"])
        self.assertEqual(True, spp.probe_config["spp"]["verify_host"])
        self.assertEqual(True, spp.probe_config["spp"]["ssl_enabled"])
        self.assertIsNotNone(spp.probe_config["spp"]["probe_id"])
        self.assertEqual("localhost:11800", spp.probe_config["skywalking"]["collector"]["backend_service"])
        self.assertEqual("spp", spp.probe_config["skywalking"]["agent"]["service_name"])

    @mock.patch.dict('os.environ', {'SPP_PROBE_CONFIG_FILE': 'resources/base-config.yml'})
    def test_config_from_env(self):
        spp = SourcePlusPlus()
        self.assertEqual("spp-platform", spp.probe_config["spp"]["platform_host"])
        self.assertEqual(12800, spp.probe_config["spp"]["platform_port"])
        self.assertEqual(True, spp.probe_config["spp"]["verify_host"])
        self.assertEqual(False, spp.probe_config["spp"]["ssl_enabled"])
        self.assertEqual("spp-platform:11800", spp.probe_config["skywalking"]["collector"]["backend_service"])
        self.assertEqual("tutorial-jvm", spp.probe_config["skywalking"]["agent"]["service_name"])
        self.assertEqual("WARN", spp.probe_config["skywalking"]["logging"]["level"])

