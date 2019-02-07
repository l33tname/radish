# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import os
import sys
import tempfile

import pytest

from radish.main import main


@pytest.mark.parametrize(
    "given_featurefiles, given_cli_args, expected_exitcode, expected_output",
    [
        (["unicode"], [], 0, "unicode"),
        (["german"], [], 0, "german"),
    ],
    ids=[
        "Unicode Characters in Feature File",
        "German Keywords",
    ],
)
def test_main_cli_calls(
    given_featurefiles,
    given_cli_args,
    expected_exitcode,
    expected_output,
    featurefiledir,
    radishdir,
    outputdir,
):
    """
    Test calling main CLI
    """
    # given
    if "-m" not in given_cli_args and "--marker" not in given_cli_args:
        given_cli_args.extend(["--marker", "test-marker"])

    if "-b" not in given_cli_args and "--basedir" not in given_cli_args:
        given_cli_args.extend(["-b", radishdir])
    else:
        # fixup basedir paths
        base_dir_idx = [
            i for i, x in enumerate(given_cli_args) if x in ("-b", "--basedir")
        ]
        for idx in base_dir_idx:
            given_cli_args[idx + 1] = os.path.join(radishdir, given_cli_args[idx + 1])

    featurefiles = [
        os.path.join(featurefiledir, x + ".feature") for x in given_featurefiles
    ]
    cli_args = featurefiles + given_cli_args

    expected_output_file = os.path.join(outputdir, expected_output + ".txt")
    if os.name == 'nt':
        expected_output_file_win = os.path.join(outputdir, expected_output + "-win.txt")
        if os.path.exists(expected_output_file_win):
            expected_output_file = expected_output_file_win

    with open(expected_output_file, "r", encoding="utf8") as output_file:
        expected_output_string = output_file.read()

    # when
    original_stdout = sys.stdout

    with tempfile.TemporaryFile(mode="w+") as tmp_stdout:
        # patch sys.stdout
        sys.stdout = tmp_stdout

        try:
            actual_exitcode = main(args=cli_args)
        except SystemExit as exc:
            actual_exitcode = exc.code
        finally:
            tmp_stdout.seek(0)
            actual_output = tmp_stdout.read()
            # restore stdout
            sys.stdout = original_stdout

    # patch featurefile paths in actual output
    feature_parent_dir = os.path.abspath(os.path.join(featurefiledir, ".."))
    for featurefile in featurefiles:
        rel_featurefile = os.path.relpath(featurefile, feature_parent_dir)
        actual_output = actual_output.replace(featurefile, rel_featurefile)
    # then
    #if actual_output != expected_output_string:
    #    expected_output_file_win = os.path.join(outputdir, expected_output + "-win.txt")
    #    with open(expected_output_file_win, 'w', encoding="utf8") as file_win:
    #        file_win.write(actual_output)
    assert actual_output == expected_output_string
    assert actual_exitcode == expected_exitcode
