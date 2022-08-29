import os
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

    @mock.patch.dict('os.environ', {
        'SPP_PROBE_CONFIG_FILE': '%s/resources/base-config.yml' % os.path.dirname(__file__)
    })
    def test_config_from_env(self):
        spp = SourcePlusPlus()
        self.assertEqual("spp-platform", spp.probe_config["spp"]["platform_host"])
        self.assertEqual(12800, spp.probe_config["spp"]["platform_port"])
        self.assertEqual(True, spp.probe_config["spp"]["verify_host"])
        self.assertEqual(False, spp.probe_config["spp"]["ssl_enabled"])
        self.assertEqual("spp-platform:11800", spp.probe_config["skywalking"]["collector"]["backend_service"])
        self.assertEqual("tutorial-jvm", spp.probe_config["skywalking"]["agent"]["service_name"])
        self.assertEqual("WARN", spp.probe_config["skywalking"]["logging"]["level"])

    @mock.patch.dict('os.environ', {
        'SPP_PROBE_CONFIG_FILE': '%s/resources/extended-config.yml' % os.path.dirname(__file__)
    })
    def test_config_from_env_extended(self):
        spp = SourcePlusPlus()
        self.assertEqual("spp-platform", spp.probe_config["spp"]["platform_host"])
        self.assertEqual(12800, spp.probe_config["spp"]["platform_port"])
        self.assertEqual(False, spp.probe_config["spp"]["quiet_mode"])
        self.assertEqual(False, spp.probe_config["spp"]["verify_host"])
        self.assertIsNotNone(spp.probe_config["spp"]["platform_certificate"])
        self.assertIsNotNone(spp.probe_config["spp"]["probe_id"])
        self.assertEqual(True, spp.probe_config["spp"]["ssl_enabled"])
        self.assertEqual("INFO", spp.probe_config["skywalking"]["logging"]["level"])
        self.assertEqual("spp", spp.probe_config["skywalking"]["agent"]["service_name"])
        self.assertEqual("spp-platform:11801", spp.probe_config["skywalking"]["collector"]["backend_service"])
        self.assertEqual(False, spp.probe_config["skywalking"]["plugin"]["toolkit"]["log"]["transmit_formatted"])
