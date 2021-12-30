#!/usr/bin/env python3

import subprocess


def run_shell_cmd_with_output(cmd):
    popen = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True,
                             universal_newlines=True,
                             shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        print("ERROR WHILE RUNNING COMMAND: " + cmd)
        raise subprocess.CalledProcessError(return_code, cmd)


def run_command(cmd):
    """" Run a command, via the shell.
        Print output in realtime and retut
    """
    for path in run_shell_cmd_with_output(cmd):
        print(path, end="", flush=True)
    return 0

if __name__ == "__main__":
    import sys

    cmd = "echo 'Local Test'"
    # cmd = ' '.join(sys.argv[1:])
    print("Running: " + cmd)
    run_command(cmd)
