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

"""Module with BIP32 constants."""

# Imports
from bip_utils.bip.bip32.bip32_key_net_ver import Bip32KeyNetVersions


class Bip32Const:
    """Class container for BIP32 constants."""

    # Main net key net version (xpub / xprv)
    MAIN_NET_KEY_NET_VERSIONS: Bip32KeyNetVersions = Bip32KeyNetVersions(b"\x04\x88\xb2\x1e", b"\x04\x88\xad\xe4")
    # Test net key net version (tpub / tprv)
    TEST_NET_KEY_NET_VERSIONS: Bip32KeyNetVersions = Bip32KeyNetVersions(b"\x04\x35\x87\xcf", b"\x04\x35\x83\x94")
    # Key net version for BIP32 Kholaw that uses 64-byte private keys (xpub / xprv)
    KHOLAW_KEY_NET_VERSIONS: Bip32KeyNetVersions = Bip32KeyNetVersions(b"\x04\x88\xb2\x1e", b"\x0f\x43\x31\xd4")
    