import datetime
import os
from pathlib import Path

core_modules = ["sys", "os", "inspect", "pathlib"]
hera_modules = list(filter(lambda m: ".py" in m and "__" not in m, os.listdir(Path(os.getcwd()) / "src" / "hera")))

with open(Path(os.getcwd()) / "scripts" / "init_helper.py", "w+") as init_helper:
    init_helper.write("from hera import models\n")

    for module in hera_modules:
        curated_module = module.replace(".py", "")
        init_helper.write(f"from hera import {curated_module}\n")

    for module in core_modules:
        init_helper.write(f"import {module}\n")

    init_helper.write("models_final_imports = []\n")
    init_helper.write("models_members = set([m[0] for m in inspect.getmembers(models) if inspect.isclass(m[1])])\n")
    init_helper.write(f"hera_modules = {[m.replace('.py','') for m in hera_modules]}\n".replace("'", ""))
    init_helper.write(f"str_hera_modules = {[m.replace('.py','') for m in hera_modules]}\n")
    init_helper.write("all_hera_modules = []\n")
    init_helper.write("member_mapping = {}\n")
    init_helper.write("for hera_module, str_hera_module in zip(hera_modules, str_hera_modules):\n")
    init_helper.write(
        "    members = set(list(filter(lambda m: m[0] == '__all__', inspect.getmembers(hera_module)))[0][1])\n"
    )
    init_helper.write("    all_hera_modules.extend(members)\n")
    init_helper.write("    member_mapping[str_hera_module] = members\n")
    init_helper.write("diff = models_members.difference(set(all_hera_modules))\n")
    init_helper.write("models_final_imports.extend(list(diff))\n")
    init_helper.write("with open(pathlib.Path(os.getcwd()) / 'src' / 'hera' / '__init__.py', 'w+') as init_file:\n")
    init_helper.write(
        f"    init_file.write('# [DO NOT EDIT] generated via `make init` on: {datetime.datetime.now()}\\n')\n"
    )
    init_helper.write("    str_imports = ', '.join(models_final_imports)\n")
    init_helper.write("    init_file.write(f'from hera.models import {str_imports}\\n')\n")
    init_helper.write("    for str_hera_module in str_hera_modules:\n")
    init_helper.write("        imports = ', '.join(member_mapping[str_hera_module])\n")
    init_helper.write("        init_file.write(f'from hera.{str_hera_module} import {imports}\\n')\n")
    init_helper.write("    init_file.write('__version__ = version\\n')\n")
    init_helper.write("    init_file.write(\"__version_info__ = version.split('.')\")\n")
