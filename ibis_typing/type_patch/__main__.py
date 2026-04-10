"""Apply type-patches to ibis .py modules."""

import logging

from . import patched_modules


def write_patched_modules():
    for writer in patched_modules.get_patched_module_writers():
        writer.write_patched_module()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    write_patched_modules()
