# coding=utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Test the shell_flags.py file."""

import logging

from _pytest.monkeypatch import MonkeyPatch
import pytest

from funfuzz import js

from .test_compile_shell import CompileShellTests

FUNFUZZ_TEST_LOG = logging.getLogger("funfuzz_test")
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("flake8").setLevel(logging.ERROR)


def mock_chance(i):
    """Overwrite the chance function to return True or False depending on a specific condition.

    Args:
        i (float): Intended probability between 0 < i < 1

    Returns:
        bool: True if i > 0, False otherwise.
    """
    return i > 0


class ShellFlagsTests(CompileShellTests):
    """"TestCase class for functions in shell_flags.py"""
    monkeypatch = MonkeyPatch()

    @pytest.mark.slow
    def test_add_random_arch_flags(self):
        """Test that we are able to obtain add shell runtime flags related to architecture."""
        ShellFlagsTests.monkeypatch.setattr(js.shell_flags, "chance", mock_chance)

        all_flags = js.shell_flags.add_random_arch_flags(self.test_shell_compile(), [])
        assert "--enable-avx" in all_flags
        assert "--no-sse3" in all_flags
        if js.inspect_shell.queryBuildConfiguration(self.test_shell_compile(), "arm-simulator"):
            assert "--arm-sim-icache-checks" in all_flags
        if js.inspect_shell.queryBuildConfiguration(self.test_shell_compile(), "arm-simulator"):
            assert "--arm-asm-nop-fill=1" in all_flags
        # Temporarily disabled due to bug 1523515
        # if js.inspect_shell.queryBuildConfiguration(self.test_shell_compile(), "arm-simulator"):
        #     assert "--arm-hwcap=vfp" in all_flags

    @pytest.mark.slow
    def test_add_random_ion_flags(self):
        """Test that we are able to obtain add shell runtime flags related to IonMonkey."""
        ShellFlagsTests.monkeypatch.setattr(js.shell_flags, "chance", mock_chance)

        all_flags = js.shell_flags.add_random_ion_flags(self.test_shell_compile(), [])
        assert "--cache-ir-stubs=on" in all_flags
        assert "--ion-pgo=on" in all_flags
        assert "--ion-sincos=on" in all_flags
        assert "--ion-instruction-reordering=on" in all_flags
        assert "--ion-regalloc=testbed" in all_flags
        assert '--execute="setJitCompilerOption(\\"ion.forceinlineCaches\\",1)"' in all_flags
        assert "--ion-extra-checks" in all_flags
        # assert "--ion-sink=on" in all_flags
        assert "--ion-warmup-threshold=100" in all_flags
        assert "--ion-scalar-replacement=on" in all_flags
        assert "--ion-check-range-analysis" in all_flags
        # assert "--ion-regalloc=stupid" in all_flags
        assert "--ion-range-analysis=on" in all_flags
        assert "--ion-edgecase-analysis=on" in all_flags
        assert "--ion-limit-script-size=on" in all_flags
        assert "--ion-osr=on" in all_flags
        assert "--ion-inlining=on" in all_flags
        assert "--ion-eager" in all_flags
        assert "--ion-gvn=on" in all_flags
        assert "--ion-licm=on" in all_flags

    @pytest.mark.slow
    def test_add_random_wasm_flags(self):
        """Test that we are able to obtain add shell runtime flags related to WebAssembly (wasm)."""
        ShellFlagsTests.monkeypatch.setattr(js.shell_flags, "chance", mock_chance)

        all_flags = js.shell_flags.add_random_wasm_flags(self.test_shell_compile(), [])
        assert "--wasm-compiler=baseline+ion" in all_flags
        assert "--wasm-gc" in all_flags
        assert "--test-wasm-await-tier2" in all_flags
        assert "--no-asmjs" in all_flags

    @staticmethod
    def test_basic_flag_sets():
        """Test that we are able to obtain a basic set of shell runtime flags for fuzzing."""
        important_flag_set = ["--fuzzing-safe", "--ion-offthread-compile=off", "--ion-eager"]
        assert important_flag_set in js.shell_flags.basic_flag_sets()

    def test_chance(self):
        """Test that the chance function works as intended."""
        ShellFlagsTests.monkeypatch.setattr(js.shell_flags, "chance", mock_chance)
        assert js.shell_flags.chance(0.6)
        assert js.shell_flags.chance(0.1)
        self.assertFalse(js.shell_flags.chance(0))
        self.assertFalse(js.shell_flags.chance(-0.2))

    @pytest.mark.slow
    def test_random_flag_set(self):
        """Test runtime flags related to SpiderMonkey."""
        ShellFlagsTests.monkeypatch.setattr(js.shell_flags, "chance", mock_chance)

        all_flags = js.shell_flags.random_flag_set(self.test_shell_compile())
        assert "--fuzzing-safe" in all_flags
        assert "--no-streams" in all_flags
        assert "--nursery-strings=on" in all_flags
        assert "--spectre-mitigations=on" in all_flags
        assert "--ion-offthread-compile=on" in all_flags
        assert "--no-unboxed-objects" in all_flags
        assert "--no-cgc" in all_flags
        assert "--gc-zeal=4,999" in all_flags
        assert "--no-incremental-gc" in all_flags
        assert "--no-threads" in all_flags
        assert "--no-native-regexp" in all_flags
        assert "--no-ggc" in all_flags
        assert "--no-baseline" in all_flags

    @pytest.mark.slow
    def test_shell_supports_flag(self):
        """Test that the shell does support flags as intended."""
        assert js.shell_flags.shell_supports_flag(self.test_shell_compile(), "--fuzzing-safe")
