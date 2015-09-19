import os
import re
import signal
import sys
from contextlib import contextmanager
from subprocess import PIPE
from subprocess import Popen

from tests.lib.testing import REGULAR_SIGNALS


@contextmanager
def spawn_print_signals():
    proc = Popen(
        ('dumb-init', sys.executable, '-m', 'tests.lib.print_signals'),
        stdout=PIPE,
    )

    match = re.match(b'^ready \(pid: ([0-9]+)\)\n$', proc.stdout.readline())
    pid = int(match.group(1))
    yield proc
    proc.kill()
    os.kill(pid, signal.SIGKILL)


def assert_receives_signals(proc):
    for signum in REGULAR_SIGNALS:
        proc.send_signal(signum)
        assert proc.stdout.readline() == '{0}\n'.format(signum).encode('ascii')


def test_proxies_signals(both_debug_modes, both_setsid_modes):
    with spawn_print_signals() as proc:
        assert_receives_signals(proc)


def test_proxies_signals_with_suspend(both_debug_modes, both_setsid_modes):
    with spawn_print_signals() as proc:
        assert_receives_signals(proc)

        proc.send_signal(signal.SIGTSTP)
        proc.send_signal(signal.SIGCONT)
#        assert proc.stdout.readline() == b'20\n'
#        assert proc.stdout.readline() == b'18\n'

#        assert_receives_signals(proc)
