# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Imports
import binascii
import ecdsa
import ed25519_blake2b
import unittest
from ecdsa.ecdsa import generator_256, generator_secp256k1
from ecdsa import ellipticcurve
from nacl import signing
from bip_utils import (
    EllipticCurveGetter, EllipticCurveTypes,
    Ed25519, Ed25519Point, Ed25519PublicKey, Ed25519PrivateKey,
    Ed25519Blake2b, Ed25519Blake2bPublicKey, Ed25519Blake2bPrivateKey,
    Nist256p1, Nist256p1Point, Nist256p1PublicKey, Nist256p1PrivateKey,
    Secp256k1, Secp256k1Point, Secp256k1PublicKey, Secp256k1PrivateKey,
    Sr25519, Sr25519Point, Sr25519PublicKey, Sr25519PrivateKey
)

# ed25519 order and generator
ED25519_ORDER = 0x1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3ED
ED25519_GENERATOR_X = 15112221349535400772501151409588531511454012693041857206046113283949847762202
ED25519_GENERATOR_Y = 46316835694926478169428394003475163141307993866256225615783033603165251855960

# Tests for ECDSA invalid public keys
TEST_VECT_ECDSA_PUB_KEY_INVALID = [
    # Private key
    b"132750b8489385430d8bfa3871ade97da7f5d5ef134a5c85184f88743b526e38",
    # Compressed public key with valid length but wrong version
    b"019efbcb2db9ee44cb12739e9350e19e5f1ce4563351b770096f0e408f93400c70",
    # Compressed public key with invalid length
    b"029efbcb2db9ee44cb12739e9350e19e5f1ce4563351b770096f0e408f93400c7000",
    # Uncompressed public key with valid length but wrong version
    b"058ccab10df42f89efaf13ca23a96f8b2063d881601c195b354f6f49c3b5978dd4e17e3a1b1505fcb5e7d13b042fa5c8eff83c1efe17d8a56e3cf3fa9250cb80fe",
    # Uncompressed public key with invalid length
    b"04fd87569e9af6015d9d938c67c68fcdf5440d3c235eccbc1195a1924bba90e5e1954cb6d841054791ac227a8c11f79f77d24a20b238402c5424c8e436bb49",
]

# Tests for ed25519 invalid public keys
TEST_VECT_ED25519_PUB_KEY_INVALID = [
    # Public key with valid length but wrong version
    b"01e9b6062841bb977ad21de71ec961900633c26f21384e015b014a637a61499547",
    # Public keys with invalid length
    b"00e9b6062841bb977ad21de71ec961900633c26f21384e015b014a637a6149954711",
    b"00e9b6062841bb977ad21de71ec961900633c26f21384e015b014a637a6149",
]

# Tests for nist256p1 invalid public keys
TEST_VECT_NIST256P1_PUB_KEY_INVALID = TEST_VECT_ECDSA_PUB_KEY_INVALID
# Tests for secp256k1 invalid public keys
TEST_VECT_SECP256K1_PUB_KEY_INVALID = TEST_VECT_ECDSA_PUB_KEY_INVALID

# Tests for sr25519 invalid public keys
TEST_VECT_SR25519_PUB_KEY_INVALID = [
    # Public keys with invalid length
    b"e9b6062841bb977ad21de71ec961900633c26f21384e015b014a637a6149954711",
    b"e9b6062841bb977ad21de71ec961900633c26f21384e015b014a637a614995",
]

# Tests for ed25519 invalid private keys
TEST_VECT_ED25519_PRIV_KEY_INVALID = [
    # Private keys with invalid length
    b"132750b8489385430d8bfa3871ade97da7f5d5ef134a5c85184f88743b526e",
    b"132750b8489385430d8bfa3871ade97da7f5d5ef134a5c85184f88743b526e71d0",
]

# Tests for nist256p1 invalid private keys
TEST_VECT_NIST256P1_PRIV_KEY_INVALID = TEST_VECT_ED25519_PRIV_KEY_INVALID
# Tests for secp256k1 invalid private keys
TEST_VECT_SECP256K1_PRIV_KEY_INVALID = TEST_VECT_ED25519_PRIV_KEY_INVALID

# Tests for sr25519 invalid private keys
TEST_VECT_SR25519_PRIV_KEY_INVALID = [
    # Private keys with invalid length
    b"2ec306fc1c5bc2f0e3a2c7a6ec6014ca4a0823a7d7d42ad5e9d7f376a1c36c0d14a2ddb1ef1df4adba49f3a4d8c0f6205117907265f09a53ccf07a4e8616df",
    b"2ec306fc1c5bc2f0e3a2c7a6ec6014ca4a0823a7d7d42ad5e9d7f376a1c36c0d14a2ddb1ef1df4adba49f3a4d8c0f6205117907265f09a53ccf07a4e8616dfd802",
]

# Some valid ed25519 keys
TEST_ED25519_COMPR_PUB_KEY_BYTES = b"007d5ea03ab150169176f66df6f6f67afe70b4d9e8b06fa6b46cd74bab1ca5e75c"
TEST_ED25519_UNCOMPR_PUB_KEY_BYTES = TEST_ED25519_COMPR_PUB_KEY_BYTES
TEST_ED25519_PRIV_KEY_BYTES = b"63326e09d412622906496bdde342b4a60410b3f48db5e74a27bfc1b0b044f80b"

TEST_ED25519_PUB_KEY = Ed25519PublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
TEST_ED25519_PRIV_KEY = Ed25519PrivateKey.FromBytes(binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))

TEST_ED25519_BLAKE2B_PUB_KEY = Ed25519Blake2bPublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
TEST_ED25519_BLAKE2B_PRIV_KEY = Ed25519Blake2bPrivateKey.FromBytes(binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))

# Some valid nist256p1 keys and points
TEST_NIST256P1_COMPR_PUB_KEY_BYTES = b"038ea003d38b3f2043e681f06f56b3864d28d73b4f243aee90ed04a28dbc058c5b"
TEST_NIST256P1_UNCOMPR_PUB_KEY_BYTES = b"048ea003d38b3f2043e681f06f56b3864d28d73b4f243aee90ed04a28dbc058c5b465656d4dd23293a66bbbd3cc07cf6e5b1cd3b81d8e3da4eed050ac0ab2094b9"
TEST_NIST256P1_PRIV_KEY_BYTES = b"e44c51393e98a691439f74c2060138fa2bcefae59ab277bd81907c93fb16fce1"
TEST_NIST256P1_POINT = {"x": 64511146437640532869164237123971144495620316712208575072439516305921182895195,
                        "y": 31814447537382586537576639307337099269020393742089100496617531967175387026617}
TEST_NIST256P1_POINT_ADD = {"x": 101370444989464769337019234113187919586549255451863198632358447242825043882751,
                            "y": 96679656738774927550763413778994915607472627190911082265431331813273377117362}
TEST_NIST256P1_POINT_MUL = TEST_NIST256P1_POINT_ADD
TEST_NIST256P1_POINT_BYTES = "8ea003d38b3f2043e681f06f56b3864d28d73b4f243aee90ed04a28dbc058c5b465656d4dd23293a66bbbd3cc07cf6e5b1cd3b81d8e3da4eed050ac0ab2094b9"

TEST_NIST256P1_PUB_KEY = Nist256p1PublicKey.FromBytes(binascii.unhexlify(TEST_NIST256P1_COMPR_PUB_KEY_BYTES))
TEST_NIST256P1_PRIV_KEY = Nist256p1PrivateKey.FromBytes(binascii.unhexlify(TEST_NIST256P1_PRIV_KEY_BYTES))

# Some valid secp256k1 keys and points
TEST_SECP256K1_COMPR_PUB_KEY_BYTES = b"02c3d01cb07697dc5105013bea2e73a896b6019ec3c5ea2b97dba14ae4456439f4"
TEST_SECP256K1_UNCOMPR_PUB_KEY_BYTES = b"04c3d01cb07697dc5105013bea2e73a896b6019ec3c5ea2b97dba14ae4456439f4ec9654b17e30a8a5232078201ecf5cc702dfbb70266aecf16b1f81d85e6b9942"
TEST_SECP256K1_PRIV_KEY_BYTES = b"e1d36931d581b4dcae0bb03929adcfb5ab0cdc0f4886ff6c5098591636ace214"
TEST_SECP256K1_POINT = {"x": 88568707669548495476516508095445138344657010992834487537871095020828542384628,
                        "y": 107011443857260681605663973889402727500845015180707970416758298978829074143554}
TEST_SECP256K1_POINT_ADD = {"x": 36055427468220068554092197997262360511679559617381195682414059417211150654731,
                            "y": 35614013837322639151401845680153599308855232143046454444952007884320857835400}
TEST_SECP256K1_POINT_MUL = TEST_SECP256K1_POINT_ADD
TEST_SECP256K1_POINT_BYTES = "c3d01cb07697dc5105013bea2e73a896b6019ec3c5ea2b97dba14ae4456439f4ec9654b17e30a8a5232078201ecf5cc702dfbb70266aecf16b1f81d85e6b9942"

TEST_SECP256K1_PUB_KEY = Secp256k1PublicKey.FromBytes(binascii.unhexlify(TEST_SECP256K1_COMPR_PUB_KEY_BYTES))
TEST_SECP256K1_PRIV_KEY = Secp256k1PrivateKey.FromBytes(binascii.unhexlify(TEST_SECP256K1_PRIV_KEY_BYTES))

# Some valid sr25519 keys
TEST_SR25519_COMPR_PUB_KEY_BYTES = b"66933bd1f37070ef87bd1198af3dacceb095237f803f3d32b173e6b425ed7972"
TEST_SR25519_UNCOMPR_PUB_KEY_BYTES = TEST_SR25519_COMPR_PUB_KEY_BYTES
TEST_SR25519_PRIV_KEY_BYTES = b"2ec306fc1c5bc2f0e3a2c7a6ec6014ca4a0823a7d7d42ad5e9d7f376a1c36c0d14a2ddb1ef1df4adba49f3a4d8c0f6205117907265f09a53ccf07a4e8616dfd8"

TEST_SR25519_PUB_KEY = Sr25519PublicKey.FromBytes(binascii.unhexlify(TEST_SR25519_COMPR_PUB_KEY_BYTES))
TEST_SR25519_PRIV_KEY = Sr25519PrivateKey.FromBytes(binascii.unhexlify(TEST_SR25519_PRIV_KEY_BYTES))

#
# Tests
#
class EccTests(unittest.TestCase):
    # Test elliptic curve getter
    def test_elliptic_curve_getter(self):
        self.assertTrue(EllipticCurveGetter.FromType(EllipticCurveTypes.ED25519) is Ed25519)
        self.assertTrue(EllipticCurveGetter.FromType(EllipticCurveTypes.ED25519_BLAKE2B) is Ed25519Blake2b)
        self.assertTrue(EllipticCurveGetter.FromType(EllipticCurveTypes.NIST256P1) is Nist256p1)
        self.assertTrue(EllipticCurveGetter.FromType(EllipticCurveTypes.SECP256K1) is Secp256k1)
        self.assertTrue(EllipticCurveGetter.FromType(EllipticCurveTypes.SR25519) is Sr25519)
        self.assertRaises(TypeError, EllipticCurveGetter.FromType, 0)

    # Test Ed25519 class
    def test_ed25519(self):
        # Curve
        self.assertEqual(Ed25519.Name(), "Ed25519")
        self.assertEqual(Ed25519.Order(), ED25519_ORDER)
        self.assertEqual(Ed25519.Generator().X(), ED25519_GENERATOR_X)
        self.assertEqual(Ed25519.Generator().Y(), ED25519_GENERATOR_Y)
        self.assertTrue(Ed25519.PointClass() is Ed25519Point)
        self.assertTrue(Ed25519.PublicKeyClass() is Ed25519PublicKey)
        self.assertTrue(Ed25519.PrivateKeyClass() is Ed25519PrivateKey)

        # Public key
        self.assertRaises(TypeError, Ed25519PublicKey, 0)
        self.assertTrue(Ed25519PublicKey.FromPoint(Ed25519Point.FromCoordinates(0, 0)) is None)
        self.assertEqual(Ed25519PublicKey.CurveType(), EllipticCurveTypes.ED25519)
        self.assertEqual(Ed25519PublicKey.CompressedLength(), 33)
        self.assertEqual(Ed25519PublicKey.UncompressedLength(), 33)

        # From compressed
        pub_key = Ed25519PublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), signing.VerifyKey))
        self.assertTrue(pub_key.Point() is None)
        # From uncompressed
        pub_key = Ed25519PublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), signing.VerifyKey))
        self.assertTrue(pub_key.Point() is None)

        # Private key
        self.assertRaises(TypeError, Ed25519PrivateKey, 0)
        self.assertEqual(Ed25519PrivateKey.CurveType(), EllipticCurveTypes.ED25519)
        self.assertEqual(Ed25519PrivateKey.Length(), 32)

        priv_key = Ed25519PrivateKey.FromBytes(binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))
        self.assertTrue(isinstance(priv_key.UnderlyingObject(), signing.SigningKey))
        self.assertEqual(priv_key.Raw().ToBytes(), binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))

        # Point
        self.__test_dummy_point(Ed25519Point)

    # Test Ed25519-Blake2b class
    def test_ed25519_blake2b(self):
        # Curve
        self.assertEqual(Ed25519Blake2b.Name(), "Ed25519-Blake2b")
        self.assertEqual(Ed25519Blake2b.Order(), ED25519_ORDER)
        self.assertEqual(Ed25519Blake2b.Generator().X(), ED25519_GENERATOR_X)
        self.assertEqual(Ed25519Blake2b.Generator().Y(), ED25519_GENERATOR_Y)
        self.assertTrue(Ed25519Blake2b.PointClass() is Ed25519Point)
        self.assertTrue(Ed25519Blake2b.PublicKeyClass() is Ed25519Blake2bPublicKey)
        self.assertTrue(Ed25519Blake2b.PrivateKeyClass() is Ed25519Blake2bPrivateKey)

        # Public key
        self.assertRaises(TypeError, Ed25519Blake2bPublicKey, 0)
        self.assertTrue(Ed25519Blake2bPublicKey.FromPoint(Ed25519Point.FromCoordinates(0, 0)) is None)
        self.assertEqual(Ed25519Blake2bPublicKey.CurveType(), EllipticCurveTypes.ED25519_BLAKE2B)
        self.assertEqual(Ed25519Blake2bPublicKey.CompressedLength(), 33)
        self.assertEqual(Ed25519Blake2bPublicKey.UncompressedLength(), 33)

        # From compressed
        pub_key = Ed25519Blake2bPublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ed25519_blake2b.VerifyingKey))
        self.assertTrue(pub_key.Point() is None)
        # From uncompressed
        pub_key = Ed25519Blake2bPublicKey.FromBytes(binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_ED25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ed25519_blake2b.VerifyingKey))
        self.assertTrue(pub_key.Point() is None)

        # Private key
        self.assertRaises(TypeError, Ed25519Blake2bPrivateKey, 0)
        self.assertEqual(Ed25519Blake2bPrivateKey.CurveType(), EllipticCurveTypes.ED25519_BLAKE2B)
        self.assertEqual(Ed25519Blake2bPrivateKey.Length(), 32)

        priv_key = Ed25519Blake2bPrivateKey.FromBytes(binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))
        self.assertTrue(isinstance(priv_key.UnderlyingObject(), ed25519_blake2b.SigningKey))
        self.assertEqual(priv_key.Raw().ToBytes(), binascii.unhexlify(TEST_ED25519_PRIV_KEY_BYTES))

    # Test Nist256p1 class
    def test_nist256p1(self):
        # Curve
        self.assertEqual(Nist256p1.Name(), "Nist256p1")
        self.assertEqual(Nist256p1.Order(), generator_256.order())
        self.assertEqual(Nist256p1.Generator().X(), generator_256.x())
        self.assertEqual(Nist256p1.Generator().Y(), generator_256.y())
        self.assertTrue(Nist256p1.PointClass() is Nist256p1Point)
        self.assertTrue(Nist256p1.PublicKeyClass() is Nist256p1PublicKey)
        self.assertTrue(Nist256p1.PrivateKeyClass() is Nist256p1PrivateKey)

        #
        # Public key
        #
        self.assertRaises(TypeError, Nist256p1PublicKey, 0)
        self.assertEqual(Nist256p1PublicKey.CurveType(), EllipticCurveTypes.NIST256P1)
        self.assertEqual(Nist256p1PublicKey.CompressedLength(), 33)
        self.assertEqual(Nist256p1PublicKey.UncompressedLength(), 65)

        # From compressed
        pub_key = Nist256p1PublicKey.FromBytes(binascii.unhexlify(TEST_NIST256P1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ecdsa.VerifyingKey))
        # From uncompressed
        pub_key = Nist256p1PublicKey.FromBytes(binascii.unhexlify(TEST_NIST256P1_UNCOMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ecdsa.VerifyingKey))

        # From point
        pub_key = Nist256p1PublicKey.FromPoint(Nist256p1Point.FromCoordinates(TEST_NIST256P1_POINT["x"], TEST_NIST256P1_POINT["y"]))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_NIST256P1_UNCOMPR_PUB_KEY_BYTES))

        #
        # Private key
        #
        self.assertRaises(TypeError, Nist256p1PrivateKey, 0)
        self.assertEqual(Nist256p1PrivateKey.CurveType(), EllipticCurveTypes.NIST256P1)
        self.assertEqual(Nist256p1PrivateKey.Length(), 32)

        priv_key = Nist256p1PrivateKey.FromBytes(binascii.unhexlify(TEST_NIST256P1_PRIV_KEY_BYTES))
        self.assertTrue(isinstance(priv_key.UnderlyingObject(), ecdsa.SigningKey))
        self.assertEqual(priv_key.Raw().ToBytes(), binascii.unhexlify(TEST_NIST256P1_PRIV_KEY_BYTES))

        #
        # Point
        #
        self.assertRaises(TypeError, Nist256p1Point, 0)

        point = pub_key.Point()
        self.assertTrue(isinstance(point.UnderlyingObject(), ellipticcurve.PointJacobi))
        self.assertEqual(point.X(), TEST_NIST256P1_POINT["x"])
        self.assertEqual(point.Y(), TEST_NIST256P1_POINT["y"])
        self.assertEqual(point.ToBytes().ToHex(), TEST_NIST256P1_POINT_BYTES)

        # Addition
        point_add = point + point
        self.assertEqual(point_add.X(), TEST_NIST256P1_POINT_ADD["x"])
        self.assertEqual(point_add.Y(), TEST_NIST256P1_POINT_ADD["y"])

        # Multiplication
        point_mul = point * 2
        self.assertEqual(point_mul.X(), TEST_NIST256P1_POINT_MUL["x"])
        self.assertEqual(point_mul.Y(), TEST_NIST256P1_POINT_MUL["y"])

        # Reverse multiplication
        point_mul = 2 * point
        self.assertEqual(point_mul.X(), TEST_NIST256P1_POINT_MUL["x"])
        self.assertEqual(point_mul.Y(), TEST_NIST256P1_POINT_MUL["y"])

        # From bytes
        point = Nist256p1Point.FromBytes(binascii.unhexlify(TEST_NIST256P1_POINT_BYTES))
        self.assertEqual(point.X(), TEST_NIST256P1_POINT["x"])
        self.assertEqual(point.Y(), TEST_NIST256P1_POINT["y"])
        self.assertEqual(point.ToBytes().ToHex(), TEST_NIST256P1_POINT_BYTES)

    # Test Secp256k1 class
    def test_secp256k1(self):
        # Curve
        self.assertEqual(Secp256k1.Name(), "Secp256k1")
        self.assertEqual(Secp256k1.Order(), generator_secp256k1.order())
        self.assertEqual(Secp256k1.Generator().X(), generator_secp256k1.x())
        self.assertEqual(Secp256k1.Generator().Y(), generator_secp256k1.y())
        self.assertTrue(Secp256k1.PointClass() is Secp256k1Point)
        self.assertTrue(Secp256k1.PublicKeyClass() is Secp256k1PublicKey)
        self.assertTrue(Secp256k1.PrivateKeyClass() is Secp256k1PrivateKey)

        #
        # Public key
        #

        self.assertRaises(TypeError, Secp256k1PublicKey, 0)
        self.assertEqual(Secp256k1PublicKey.CurveType(), EllipticCurveTypes.SECP256K1)
        self.assertEqual(Secp256k1PublicKey.CompressedLength(), 33)
        self.assertEqual(Secp256k1PublicKey.UncompressedLength(), 65)

        # From compressed
        pub_key = Secp256k1PublicKey.FromBytes(binascii.unhexlify(TEST_SECP256K1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ecdsa.VerifyingKey))
        # From uncompressed
        pub_key = Secp256k1PublicKey.FromBytes(binascii.unhexlify(TEST_SECP256K1_UNCOMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), ecdsa.VerifyingKey))

        # From point
        pub_key = Secp256k1PublicKey.FromPoint(Secp256k1Point.FromCoordinates(TEST_SECP256K1_POINT["x"], TEST_SECP256K1_POINT["y"]))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_SECP256K1_UNCOMPR_PUB_KEY_BYTES))

        #
        # Private key
        #
        self.assertRaises(TypeError, Secp256k1PrivateKey, 0)
        self.assertEqual(Secp256k1PrivateKey.CurveType(), EllipticCurveTypes.SECP256K1)
        self.assertEqual(Secp256k1PrivateKey.Length(), 32)

        priv_key = Secp256k1PrivateKey.FromBytes(binascii.unhexlify(TEST_SECP256K1_PRIV_KEY_BYTES))
        self.assertTrue(isinstance(priv_key.UnderlyingObject(), ecdsa.SigningKey))
        self.assertEqual(priv_key.Raw().ToBytes(), binascii.unhexlify(TEST_SECP256K1_PRIV_KEY_BYTES))

        #
        # Point
        #
        self.assertRaises(TypeError, Secp256k1Point, 0)

        point = pub_key.Point()
        self.assertTrue(isinstance(point.UnderlyingObject(), ellipticcurve.PointJacobi))
        self.assertEqual(point.X(), TEST_SECP256K1_POINT["x"])
        self.assertEqual(point.Y(), TEST_SECP256K1_POINT["y"])
        self.assertEqual(point.ToBytes().ToHex(), TEST_SECP256K1_POINT_BYTES)

        # Addition
        point_add = point + point
        self.assertEqual(point_add.X(), TEST_SECP256K1_POINT_ADD["x"])
        self.assertEqual(point_add.Y(), TEST_SECP256K1_POINT_ADD["y"])

        # Multiplication
        point_mul = point * 2
        self.assertEqual(point_mul.X(), TEST_SECP256K1_POINT_MUL["x"])
        self.assertEqual(point_mul.Y(), TEST_SECP256K1_POINT_MUL["y"])

        # Reverse multiplication
        point_mul = 2 * point
        self.assertEqual(point_mul.X(), TEST_SECP256K1_POINT_MUL["x"])
        self.assertEqual(point_mul.Y(), TEST_SECP256K1_POINT_MUL["y"])

        # From bytes
        point = Secp256k1Point.FromBytes(binascii.unhexlify(TEST_SECP256K1_POINT_BYTES))
        self.assertEqual(point.X(), TEST_SECP256K1_POINT["x"])
        self.assertEqual(point.Y(), TEST_SECP256K1_POINT["y"])
        self.assertEqual(point.ToBytes().ToHex(), TEST_SECP256K1_POINT_BYTES)

    # Test Sr25519 class
    def test_sr25519(self):
        # Curve
        self.assertEqual(Sr25519.Name(), "Sr25519")
        self.assertEqual(Sr25519.Order(), 0)
        self.assertEqual(Sr25519.Generator().X(), 0)
        self.assertEqual(Sr25519.Generator().Y(), 0)
        self.assertTrue(Sr25519.PointClass() is Sr25519Point)
        self.assertTrue(Sr25519.PublicKeyClass() is Sr25519PublicKey)
        self.assertTrue(Sr25519.PrivateKeyClass() is Sr25519PrivateKey)

        # Public key
        self.assertRaises(TypeError, Sr25519PublicKey, 0)
        self.assertTrue(Sr25519PublicKey.FromPoint(Sr25519Point.FromCoordinates(0, 0)) is None)
        self.assertEqual(Sr25519PublicKey.CurveType(), EllipticCurveTypes.SR25519)
        self.assertEqual(Sr25519PublicKey.CompressedLength(), 32)
        self.assertEqual(Sr25519PublicKey.UncompressedLength(), 32)

        # From compressed
        pub_key = Sr25519PublicKey.FromBytes(binascii.unhexlify(TEST_SR25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_SR25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_SR25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), bytes))
        self.assertTrue(pub_key.Point() is None)
        # From uncompressed
        pub_key = Sr25519PublicKey.FromBytes(binascii.unhexlify(TEST_SR25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawCompressed().ToBytes(), binascii.unhexlify(TEST_SR25519_COMPR_PUB_KEY_BYTES))
        self.assertEqual(pub_key.RawUncompressed().ToBytes(), binascii.unhexlify(TEST_SR25519_UNCOMPR_PUB_KEY_BYTES))
        self.assertTrue(isinstance(pub_key.UnderlyingObject(), bytes))
        self.assertTrue(pub_key.Point() is None)

        # Private key
        self.assertRaises(TypeError, Sr25519PrivateKey, 0)
        self.assertEqual(Sr25519PrivateKey.CurveType(), EllipticCurveTypes.SR25519)
        self.assertEqual(Sr25519PrivateKey.Length(), 64)

        priv_key = Sr25519PrivateKey.FromBytes(binascii.unhexlify(TEST_SR25519_PRIV_KEY_BYTES))
        self.assertTrue(isinstance(priv_key.UnderlyingObject(), bytes))
        self.assertEqual(priv_key.Raw().ToBytes(), binascii.unhexlify(TEST_SR25519_PRIV_KEY_BYTES))

        # Point
        self.__test_dummy_point(Sr25519Point)

    # Test invalid public keys
    def test_invalid_pub_keys(self):
        for test in TEST_VECT_ED25519_PUB_KEY_INVALID:
            self.assertRaises(ValueError, Ed25519PublicKey.FromBytes, binascii.unhexlify(test))
            self.assertRaises(ValueError, Ed25519Blake2bPublicKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Ed25519PublicKey.IsValidBytes(binascii.unhexlify(test)))
            self.assertFalse(Ed25519Blake2bPublicKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_NIST256P1_PUB_KEY_INVALID:
            self.assertRaises(ValueError, Nist256p1PublicKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Nist256p1PublicKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_SECP256K1_PUB_KEY_INVALID:
            self.assertRaises(ValueError, Secp256k1PublicKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Secp256k1PublicKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_SR25519_PUB_KEY_INVALID:
            self.assertRaises(ValueError, Sr25519PublicKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Sr25519PublicKey.IsValidBytes(binascii.unhexlify(test)))

    # Test invalid private keys
    def test_invalid_priv_keys(self):
        for test in TEST_VECT_ED25519_PRIV_KEY_INVALID:
            self.assertRaises(ValueError, Ed25519PrivateKey.FromBytes, binascii.unhexlify(test))
            self.assertRaises(ValueError, Ed25519Blake2bPrivateKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Ed25519PrivateKey.IsValidBytes(binascii.unhexlify(test)))
            self.assertFalse(Ed25519Blake2bPrivateKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_NIST256P1_PRIV_KEY_INVALID:
            self.assertRaises(ValueError, Nist256p1PrivateKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Nist256p1PrivateKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_SECP256K1_PRIV_KEY_INVALID:
            self.assertRaises(ValueError, Secp256k1PrivateKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Secp256k1PrivateKey.IsValidBytes(binascii.unhexlify(test)))

        for test in TEST_VECT_SR25519_PRIV_KEY_INVALID:
            self.assertRaises(ValueError, Sr25519PrivateKey.FromBytes, binascii.unhexlify(test))
            self.assertFalse(Sr25519PrivateKey.IsValidBytes(binascii.unhexlify(test)))

    # Test for DummyPoint
    def __test_dummy_point(self, point_cls):
        self.assertRaises(TypeError, point_cls, 0)
        self.assertTrue(point_cls.FromBytes(b"") is None)

        point = point_cls.FromCoordinates(1, 2)

        self.assertTrue(point.UnderlyingObject() is None)
        self.assertEqual(point.X(), 1)
        self.assertEqual(point.Y(), 2)
        self.assertTrue(point.ToBytes() is None)
        self.assertTrue((point + point) is None)
        self.assertTrue((point * 1) is None)
        self.assertTrue((1 * point) is None)
