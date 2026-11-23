import json
import unittest

from flux_protocol import FluxClient, FluxError, MessageType, decode, encode


class TestRoundTrip(unittest.TestCase):
    def test_scalars_and_containers(self):
        samples = [
            None,
            True,
            False,
            0,
            1,
            -1,
            127,
            128,
            -128,
            2**32,
            -2**31,
            3.14159,
            "",
            "hello",
            "日本語",
            b"",
            b"\x00\xff",
            [],
            [1, "a", None],
            {},
            {"a": 1, "b": [True, False], "c": {"d": "e"}},
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(decode(encode(sample)), sample)

    def test_string_dedup_round_trips(self):
        data = {"role": "agent", "name": "agent", "items": ["agent", "agent", "other"]}
        self.assertEqual(decode(encode(data)), data)

    def test_message_type_does_not_change_payload(self):
        data = {"function": "process_batch", "args": {"items": [1, 2, 3]}}
        blob = FluxClient().encode(data, MessageType.FUNCTION_CALL)
        self.assertEqual(FluxClient().decode(blob), data)

    def test_crc_rejects_tampering(self):
        blob = bytearray(encode({"ok": True}))
        blob[-1] ^= 0x01
        with self.assertRaises(FluxError):
            decode(bytes(blob))

    def test_bad_magic(self):
        with self.assertRaises(FluxError):
            decode(b"XXXX" + b"\x00" * 8)

    def test_unsupported_type(self):
        with self.assertRaises(FluxError):
            encode(object())

    def test_non_string_dict_key(self):
        with self.assertRaises(FluxError):
            encode({1: "nope"})

    def test_compare_sizes_keys(self):
        stats = FluxClient().compare_sizes({"function": "process_batch"})
        self.assertIn("json_bytes", stats)
        self.assertIn("flux_bytes", stats)
        self.assertIn("reduction_percent", stats)
        self.assertIsInstance(stats["reduction_percent"], float)


if __name__ == "__main__":
    unittest.main()
