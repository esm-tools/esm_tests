import os
import sys
import subprocess
import argparse
import math
import yaml
import re
import shutil
from loguru import logger
from esm_runscripts import color_diff


def user_config():
    # Check for user configuration file
    user_config = f"{script_dir}/user_config.yaml"
    print()
    if not os.path.isfile(user_config):
        # Make the user configuration file
        answers = {}
        print(
            "{bs}Welcome to ESM-Tests! Automatic testing for ESM-Tools devs\n"
            + "**********************************************************{be}\n"
            + "Please answer the following questions. If you ever need to change the "
            + "configuration, you can do that in the the esm_tests/user_config.yaml\n"
        )
        answers["account"] = input(
            "What account will you be using for testing? (default: None) "
        )
        if not answers["account"] or answers["account"] == "None":
            answers["account"] = None
        answers["test_dir"] = input(
            "In which directory would you like to run the tests? "
        )
        with open(user_config, "w") as uc:
            out = yaml.dump(answers)
            uc.write(out)

    # Load the user info
    with open(user_config, "r") as uc:
        user_info = yaml.load(uc, Loader=yaml.FullLoader)
    print(f"{bs}Running tests with the following configuration:{be}")
    print(f"{bs}-----------------------------------------------{be}")
    yprint(user_info)

    return user_info


def yprint(pdict):
    print(yaml.dump(pdict, default_flow_style=False))


def get_scripts():
    scripts_info = {}
    ns = 0
    for model in os.listdir(runscripts_dir):
        scripts_info[model] = {}
        for script in os.listdir(f"{runscripts_dir}/{model}"):
            if script != "config.yaml" and ".swp" not in script:
                scripts_info[model][script.rstrip(".yaml")] = {}
                scripts_info[model][script.rstrip(".yaml")][
                    "path"
                ] = f"{runscripts_dir}/{model}/{script}"
                ns += 1
    scripts_info["general"] = {"num_scripts": ns}
    return scripts_info


def read_info_from_rs(scripts_info):
    for model, scripts in scripts_info.items():
        if model == "general":
            continue
        for script, v in scripts.items():
            with open(v["path"], "r") as rs:
                runscript = yaml.load(rs, Loader=yaml.FullLoader)
            v["version"] = runscript[model]["version"]

    return scripts_info


def sh(inp_str):
    p = subprocess.Popen(
        inp_str.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out = p.communicate()[0].decode("utf-8")
    return out


def comp_test(scripts_info, actually_compile):
    cd_format = re.compile("         cd (.*)")

    c = 0
    for model, scripts in scripts_info.items():
        if model == "general":
            continue
        for script, v in scripts.items():
            c += 1
            progress = round(c / scripts_info["general"]["num_scripts"] * 100, 1)
            version = v["version"]
            comp_command = f"esm_master comp-{model}-{version} --no-motd"
            general_model_dir = f"{user_info['test_dir']}/comp/{model}"
            model_dir = f"{user_info['test_dir']}/comp/{model}/{model}-{version}"
            logger.info(f"\tCOMPILING ({progress}%) {model}-{version}:")
            if not os.path.isdir(general_model_dir):
                os.makedirs(general_model_dir)
            os.chdir(general_model_dir)

            if os.path.isdir(model_dir):
                v["state"] = "Directory already exists"
                logger.info(f"\t\tDirectory already exists, skipping")
                out = ""
            else:
                # Gets the source code if actual compilation is required
                if actually_compile:
                    get_command = f"esm_master get-{model}-{version} --no-motd"
                    logger.info("\t\tDownloading")
                    out = sh(get_command)
                # For no compilation trick esm_master into thinking that the source code has been downloaded
                else:
                    # Evaluate and create folders to trick esm_master
                    out = sh(f"{comp_command} -c")
                    folders = []
                    for line in out.split("\n"):
                        if "cd" in line and "cd .." not in line:
                            found_format = cd_format.findall(line)
                            if len(found_format) > 0:
                                if (
                                    ";" not in found_format[0]
                                    and "/" not in found_format[0]
                                ):
                                    folders.append(found_format[0])
                    if len(folders) == 0:
                        logger.warning(
                            f'NOT TESTING {model + version}: "cd" command not found'
                        )
                        continue
                    prim_f = folders[0]
                    folders.append(f"{model}-{version}")
                    folders = [x for x in set(folders)]
                    os.mkdir(prim_f)
                    for folder in folders:
                        os.mkdir(prim_f + "/" + folder)

                # Compile
                if actually_compile:
                    logger.info("\t\tCompiling")
                else:
                    logger.info("\t\tWritting compilation scripts")
                out = sh(comp_command)

                # Write output file
                with open(f"{model_dir}/comp.out", "w") as o:
                    o.write(out)

                # Move and cleanup files
                if not actually_compile:
                    for f in os.listdir(general_model_dir):
                        if "comp-" in f:
                            shutil.move(f"{general_model_dir}/{f}", model_dir)
                        if f == "dummy_script.sh":
                            os.remove(f"{general_model_dir}/{f}")

            # Checks
            success = check("comp", model, version, out, script, v)
            if success:
                logger.info("\t\tSuccess!")
                v["state"] = "success"

    return scripts_info


def check(mode, model, version, out, script, v):
    success = True
    # Load config
    with open(f"{os.path.dirname(v['path'])}/config.yaml", "r") as c:
        config_test = yaml.load(c, Loader=yaml.FullLoader)
    config_test = config_test[mode]
    # Check for files that should exist
    if mode == "comp":
        actually_do = actually_compile
    elif mode == "run":
        actually_do = actually_run
    if actually_do:
        # Check for errors in the output
        errors = config_test.get("actual", {}).get("errors", [])
        if mode == "comp":
            errors.append("errors occurred!")
        for error in errors:
            if error in out:
                logger.error("\t\tError during compilation!")
                success = False
        # Check if files exist
        files_checked = exist_files(
            config_test.get("actual", {}).get("files", []),
            f"{user_info['test_dir']}/{mode}/{model}/{model}-{version}",
        )
        success = success and files_checked
    # Compare scripts with previous, if existing

    return success


def exist_files(files, path):
    files_checked = True
    for f in files:
        if not os.path.isfile(f"{path}/{f}"):
            logger.error(f"\t\t'{f}' does not exist!")
            files_checked = False
    return files_checked


def run_test(scripts_info, actually_run):
    # Loop through tests
    for model, scripts in scripts_info.items():
        if model == "general":
            continue
        for script, v in scripts.items():
            if actually_compile:
                check = ""
            else:
                check = "-c"
            # Export test variables
            export_vars = [
                f"ESM_TESTING_DIR={user_info['test_dir']}/{model}/",
                f"MODEL_DIR=something",
            ]
            for var in export_vars:
                print(var)
            run_command = f"esm_runscripts {v['path']} -e {script} --open-run {check}"
            print(run_command)


# Parsing
parser = argparse.ArgumentParser(description="Automatic testing for ESM-Tools devs")
parser.add_argument(
    "-n",
    "--no-user",
    default=False,
    help="Avoid loading user config",
    action="store_true",
)
parser.add_argument(
    "-c", "--comp", default=False, help="Perform compilation", action="store_true"
)
parser.add_argument(
    "-r", "--run", default=False, help="Run the scripts", action="store_true"
)
parser.add_argument(
    "-d", "--delete", default=False, help="Delete previous tests", action="store_true"
)


args = vars(parser.parse_args())
ignore_user_info = args["no_user"]
actually_compile = args["comp"]
actually_run = args["run"]
delete_tests = args["delete"]

# Bold strings
bs = "\033[1m"
be = "\033[0m"

script_dir = os.path.dirname(os.path.realpath(__file__))
runscripts_dir = f"{script_dir}/runscripts/"
current_dir = os.getcwd()

# Predefined for later
user_scripts = dict(comp={}, run={})


# Get user info for testing
if not ignore_user_info:
    user_info = user_config()
else:
    user_info = None

logger.debug(f"User info: {user_info}")
logger.debug(f"Actually compile: {actually_compile}")
logger.debug(f"Actually run: {actually_run}")

# Delete previous tests
if delete_tests:
    logger.debug("Deleting previous tests")
    if os.path.isdir(f"{user_info['test_dir']}/comp/"):
        shutil.rmtree(f"{user_info['test_dir']}/comp/")
    if os.path.isdir(f"{user_info['test_dir']}/run/"):
        shutil.rmtree(f"{user_info['test_dir']}/run/")

# Gather scripts
scripts_info = get_scripts()

# Cut down info with user_scripts

# Complete scripts_info
scripts_info = read_info_from_rs(scripts_info)


# Compile
comp_test(scripts_info, actually_compile)

# Run
run_test(scripts_info, actually_compile)


yprint(scripts_info)
