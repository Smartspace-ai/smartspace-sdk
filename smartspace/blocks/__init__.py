import inspect
from typing import cast

import smartspace.core
import smartspace.utils


def load(
    path: str | None = None,
    block_set: smartspace.core.BlockSet | None = None,
    force_reload: bool = False,
) -> smartspace.core.BlockSet:
    import importlib.util
    import pathlib
    import sys
    from os.path import dirname, isfile

    block_set = block_set or smartspace.core.BlockSet()
    if not path:
        block_set.add(smartspace.core.User)

    _path = path or dirname(__file__)
    if isfile(_path):
        file_paths = [_path]
    else:
        file_paths = [str(f) for f in pathlib.Path(_path).glob("**/*.py")]

    existing_modules = {
        m.__file__: m for m in sys.modules.values() if getattr(m, "__file__", None)
    }

    for file_path in file_paths:
        if file_path == __file__ or file_path.endswith("__main__.py"):
            continue

        if not force_reload and file_path in existing_modules:
            module = existing_modules[file_path]
        else:
            module_path = (
                file_path.removeprefix(_path).replace("/", ".")[:-3]
                if file_path != _path
                else file_path[:-3]
            )
            module_name = module_path.replace("/", ".")

            if path is None:
                module = importlib.import_module(
                    module_path, package="smartspace.blocks"
                )
            else:
                if not force_reload and module_name in sys.modules:
                    module = sys.modules[module_name]
                else:
                    spec = importlib.util.spec_from_file_location(
                        module_name, file_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        existing_modules[file_path] = module
                        spec.loader.exec_module(module)

        if not module:
            continue

        for name in dir(module):
            item = getattr(module, name)
            if (
                smartspace.utils._issubclass(item, smartspace.core.Block)
                and item != smartspace.core.Block
                and item != smartspace.core.WorkSpaceBlock
                and not inspect.isabstract(item)
            ):
                block_type = cast(type[smartspace.core.Block], item)
                block_set.add(block_type)

    return block_set
