import os
import subprocess
import argparse
import math
import yaml
import re
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
            "Welcome to ESM-Tests! Automatic testing for ESM-Tools devs\n"
            + "**********************************************************\n"
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
    print("Running tests with the following configuration:")
    print("-----------------------------------------------")
    yprint(user_info)

    return user_info


def yprint(pdict):
    print(yaml.dump(pdict, default_flow_style=False))


def get_scripts():
    scripts_info = {}
    for model in os.listdir(runscripts_dir):
        scripts_info[model] = {}
        for script in os.listdir(f"{runscripts_dir}/{model}"):
            scripts_info[model][script.rstrip(".yaml")] = {}
            scripts_info[model][script.rstrip(".yaml")][
                "path"
            ] = f"{runscripts_dir}/{model}/{script}"

    return scripts_info


def read_info_from_rs(scripts_info):
    for model, scripts in scripts_info.items():
        for script, v in scripts.items():
            with open(v["path"], "r") as rs:
                runscript = yaml.load(rs, Loader=yaml.FullLoader)
            v["version"] = runscript[model]["version"]

    return scripts_info


def sh(inp_str):
    p = subprocess.Popen(inp_str.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.communicate()[0].decode('utf-8')
    return out


def comp_test(scripts_info, actually_compile):
    cd_format = re.compile("         cd (.*)")

    for model, scripts in scripts_info.items():
        for script, v in scripts.items():
            version = v["version"]
            comp_command = f"esm_master comp-{model}-{version}"
            if not os.path.isdir(f"{user_info['test_dir']}/comp/{model}"):
                os.makedirs(f"{user_info['test_dir']}/comp/{model}")
            os.chdir(f"{user_info['test_dir']}/comp/{model}")

            if os.path.isdir(f"{user_info['test_dir']}/comp/{model}/{model}-{version}"):
                v["state"] = "Directory already exists"
            else:
                if actually_compile:
                    get_command = f"esm_master get-{model}-{version}"
                    sh(get_command)
                else:
                    # Evaluate and create folders to cheat esm_master
                    out = sh(f"{comp_command} -c")
                    folders = []
                    for line in out.split("\n"):
                        if "cd" in line and "cd .." not in line:
                            found_format = cd_format.findall(line)
                            if len(found_format) > 0:
                                if ";" not in found_format[0] and "/" not in found_format[0]:
                                    folders.append(found_format[0])
                    if len(folders)==0:
                        logger.warning(f'NOT TESTING {model + version}: "cd" command not found')
                        continue
                    prim_f = folders[0]
                    folders.append(f"{model}-{version}")
                    folders = [x for x in set(folders)]
                    if os.path.isdir(prim_f):
                        shutil.move(prim_f, prim_f + "_bckp")
                    os.mkdir(prim_f)
                    for folder in folders:
                        os.mkdir(prim_f + "/" + folder)
            out = sh(comp_command)

    return scripts_info


def run_test(scripts_info, actually_run):
    # Loop through tests
    for model, scripts in scripts_info.items():
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

args = vars(parser.parse_args())
ignore_user_info = args["no_user"]
actually_compile = args["comp"]
actually_run = args["run"]

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
