import unittest
import riemann
from riemann import utils
from .. import helpers
from ...encoding import addresses as addr

# NB:
# How to make more of these.
# 1. Install python-bitcoinlib
# 2. Compile a script to an array of ints (same as input to bytes class)
# 3. Follow procedure below
#
# from bitcoin.core.script import CScript
# from bitcoin.wallet import CBitcoinAddress
# a = CScript(bytes.fromhex('HEX SCRIPT'))
# CBitcoinAddress.from_scriptPubKey(a.to_p2sh_scriptPubKey()
#
# For more P2PKH addresses:
# P2PKHBitcoinAddress.from_pubkey(PUBKEY_BYTES, accept_invalid=True)


class TestAddresses(unittest.TestCase):

    def tearDown(self):
        riemann.select_network('bitcoin_main')

    def test_make_p2sh_address(self):
        a = addr.make_p2sh_address('OP_IF')
        self.assertEqual(a, helpers.OP_IF_P2SH)

    def test_make_p2sh_address_msig(self):
        a = addr.make_p2sh_address(helpers.MSIG_TWO_TWO_SCRIPT)
        self.assertEqual(a, helpers.MSIG_TWO_TWO_P2SH)

    def test_make_p2wsh_address(self):
        a = addr.make_p2wsh_address(helpers.P2WSH_SCRIPT)
        self.assertEqual(a, helpers.P2WSH_ADDRESS)

    def test_make_p2pkh_address(self):
        a = addr.make_p2pkh_address(b'\x00' * 65)
        self.assertEqual(a, helpers.P2PKH_0)
        b = addr.make_p2pkh_address(b'\x11' * 65)
        self.assertEqual(b, helpers.P2PKH_1)

    def test_make_p2wpkh_address(self):
        a = addr.make_p2wpkh_address(helpers.P2WPKH_PUBKEY)
        self.assertEqual(a, helpers.P2WPKH_ADDRESS)

    def test_parse(self):
        self.assertEqual(addr.parse(helpers.OP_IF_P2SH),
                         b'\x05' + helpers.OP_IF_SCRIPT_HASH)
        self.assertEqual(addr.parse(helpers.MSIG_TWO_TWO_P2SH),
                         b'\x05' + helpers.MSIG_TWO_TWO_SCRIPT_HASH)
        self.assertEqual(addr.parse(helpers.P2WSH_ADDRESS),
                         b'\x00\x20' + helpers.P2WSH_SCRIPT_HASH)
        self.assertEqual(addr.parse(helpers.P2WPKH_ADDRESS),
                         b'\x00\x14' + helpers.P2WPKH_PKH)
        self.assertEqual(addr.parse(helpers.P2PKH_0),
                         b'\x00' + helpers.PKH_0)

        with self.assertRaises(ValueError) as context:
            addr.parse('This is not a valid address.')

        self.assertIn('Unsupported address format. Got: ',
                      str(context.exception))

    def test_parse_hash(self):
        self.assertEqual(addr.parse_hash(helpers.OP_IF_P2SH),
                         helpers.OP_IF_SCRIPT_HASH)
        self.assertEqual(addr.parse_hash(helpers.MSIG_TWO_TWO_P2SH),
                         helpers.MSIG_TWO_TWO_SCRIPT_HASH)
        self.assertEqual(addr.parse_hash(helpers.P2WSH_ADDRESS),
                         helpers.P2WSH_SCRIPT_HASH)
        self.assertEqual(addr.parse_hash(helpers.P2WPKH_ADDRESS),
                         helpers.P2WPKH_PKH)
        self.assertEqual(addr.parse_hash(helpers.P2PKH_0),
                         helpers.PKH_0)

        with self.assertRaises(ValueError) as context:
            addr.parse('bc1blahblahblah')

        self.assertIn('Unsupported address format. Got: ',
                      str(context.exception))

        # Test cash addr code
        riemann.select_network('bitcoin_cash_main')
        self.assertEqual(
            addr.parse_hash(helpers.OP_IF_P2SH),
            helpers.OP_IF_SCRIPT_HASH)

        self.assertEqual(
            addr.parse_hash(helpers.OP_IF_CASHADDR),
            helpers.OP_IF_SCRIPT_HASH)

        self.assertEqual(
            addr.parse_hash(helpers.CASHADDR_P2PKH_ADDRESS),
            utils.hash160(helpers.CASHADDR_PUBKEY))

    def test_cashaddrs(self):
        riemann.select_network('bitcoin_cash_main')

        self.assertEqual(
            addr.make_legacy_p2sh_address('OP_IF'),
            helpers.OP_IF_P2SH)

        self.assertEqual(
            addr.make_sh_address('OP_IF'),
            helpers.OP_IF_CASHADDR)

        self.assertEqual(
            addr.make_legacy_p2pkh_address(helpers.CASHADDR_PUBKEY),
            helpers.LEGACY_P2PKH_ADDRESS)

        self.assertEqual(
            addr.make_pkh_address(helpers.CASHADDR_PUBKEY),
            helpers.CASHADDR_P2PKH_ADDRESS)

    def test_from_output_script(self):

        self.assertEqual(
            addr.from_output_script(helpers.OP_IF_OUTPUT_SCRIPT),
            helpers.OP_IF_P2SH)
        self.assertEqual(
            addr.from_output_script(helpers.P2WSH_OUTPUT_SCRIPT),
            helpers.P2WSH_ADDRESS)
        self.assertEqual(
            addr.from_output_script(helpers.PKH_0_OUTPUT_SCRIPT),
            helpers.P2PKH_0)
        self.assertEqual(
            addr.from_output_script(helpers.P2WPKH_OUTPUT_SCRIPT),
            helpers.P2WPKH_ADDRESS)

        with self.assertRaises(ValueError) as context:
            addr.from_output_script(b'\x8e' * 34)
        self.assertIn(
            'Cannot parse address from script.',
            str(context.exception))

    def test_cashaddr_from_output_script(self):
        riemann.select_network('bitcoin_cash_main')
        self.assertEqual(
            addr.from_output_script(helpers.PKH_0_OUTPUT_SCRIPT),
            helpers.P2PKH_0_CASHADDR)
        self.assertEqual(
            addr.from_output_script(helpers.OP_IF_OUTPUT_SCRIPT),
            helpers.OP_IF_CASHADDR)

    def test_to_output_script(self):
        self.assertEqual(
            addr.to_output_script(helpers.OP_IF_P2SH),
            helpers.OP_IF_OUTPUT_SCRIPT)
        self.assertEqual(
            addr.to_output_script(helpers.P2WSH_ADDRESS),
            helpers.P2WSH_OUTPUT_SCRIPT)
        self.assertEqual(
            addr.to_output_script(helpers.P2PKH_0),
            helpers.PKH_0_OUTPUT_SCRIPT)
        self.assertEqual(
            addr.to_output_script(helpers.P2WPKH_ADDRESS),
            helpers.P2WPKH_OUTPUT_SCRIPT)

        with self.assertRaises(ValueError) as context:
            # Junk B58 w valid checksum
            addr.to_output_script('1111111111111111111111111111111111177fdsQ')

        self.assertIn(
            'Cannot parse output script from address.',
            str(context.exception))

    def test_cashaddr_to_output_script(self):
        riemann.select_network('bitcoin_cash_main')

        self.assertEqual(
            addr.to_output_script(helpers.OP_IF_CASHADDR),
            helpers.OP_IF_OUTPUT_SCRIPT)

        self.assertEqual(
            addr.to_output_script(helpers.P2PKH_0_CASHADDR),
            helpers.PKH_0_OUTPUT_SCRIPT)
