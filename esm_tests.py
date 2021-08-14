import os
import subprocess
import argparse
import math
import yaml


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


def comp_test(scripts_info, actually_compile):
    for model, scripts in scripts_info.items():
        for script, v in scripts.items():
            # Change directory v["path"]
            if actually_compile:
                get_command = f"esm_master get-{model}-{v['version']}"
                # run command
                check = ""
            else:
                check = "-c"
            comp_command = f"esm_master comp-{model}-{v['version']} {check}"
            # run command


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

# Predefined for later
user_scripts = dict(comp={}, run={})


# Get user info for testing
if not ignore_user_info:
    user_info = user_config()
else:
    user_info = None

print(user_info)
print(actually_compile)
print(actually_run)


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
