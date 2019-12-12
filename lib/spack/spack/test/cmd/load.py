# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os
from spack.main import SpackCommand


load = SpackCommand('load')
unload = SpackCommand('unload')
install = SpackCommand('install')
location = SpackCommand('location')


def test_load(install_mockery, mock_fetch, mock_archive, mock_packages):
    """Test that the commands generated by load add the specified prefix
    inspections

    CMAKE_PREFIX_PATH is the only prefix inspection guaranteed for fake
    packages, since it keys on the prefix instead of a subdir."""
    install('mpileaks')

    sh_out = load('--sh', 'mpileaks')
    csh_out = load('--csh', 'mpileaks')

    sh_out_test = 'export CMAKE_PREFIX_PATH=%s' % location(
        '-i', 'mpileaks').strip()
    assert sh_out_test in sh_out

    csh_out_test = 'setenv CMAKE_PREFIX_PATH %s' % location(
        '-i', 'mpileaks').strip()
    assert csh_out_test in csh_out


def test_load_recursive(install_mockery, mock_fetch, mock_archive,
                        mock_packages):
    """Test that the '-r' option to the load command prepends dependency prefix
    inspections in post-order"""
    install('mpileaks')

    sh_out = load('--sh', '-r', 'mpileaks')
    csh_out = load('--csh', '-r', 'mpileaks')

    sh_out_test = 'export CMAKE_PREFIX_PATH=%s:%s' % (
        location('-i', 'mpileaks').strip(),
        location('-i', 'callpath').strip())
    assert sh_out_test in sh_out

    csh_out_test = 'setenv CMAKE_PREFIX_PATH %s:%s' % (
        location('-i', 'mpileaks').strip(),
        location('-i', 'callpath').strip())
    assert csh_out_test in csh_out


def test_load_includes_run_env(install_mockery, mock_fetch, mock_archive,
                               mock_packages):
    """Tests that environment changes from the package's
    `setup_run_environment` method are added to the user environment in
    addition to the prefix inspections"""
    install('mpileaks')

    sh_out = load('--sh', 'mpileaks')
    csh_out = load('--csh', 'mpileaks')

    assert 'export FOOBAR=mpileaks' in sh_out
    assert 'setenv FOOBAR mpileaks' in csh_out


def test_unload(install_mockery, mock_fetch, mock_archive, mock_packages,
                working_env):
    """Tests that any variables set in the user environment are undone by the
    unload command"""
    install('mpileaks')
    os.environ['FOOBAR'] = 'mpileaks'  # Set so unload has something to do

    sh_out = unload('--sh', 'mpileaks')
    csh_out = unload('--csh', 'mpileaks')

    assert 'unset FOOBAR' in sh_out
    assert 'unsetenv FOOBAR' in csh_out
