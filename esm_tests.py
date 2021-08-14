import os
import subprocess
import argparse
import math
import yaml
import pprint


def user_config():
    # Check for user configuration file
    script_dir = os.path.dirname(os.path.realpath(__file__))
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
        if not answers["account"] or answers["account"]=="None":
            answers["account"] = None
        answers["test_dir"] = input(
            "In which directory would you like to run the tests? "
        )
        with open(user_config, "w") as uc:
            out = yaml.dump(answers)
            uc.write(out)

    # Load the user info
    with open(user_config) as uc:
        user_info =  yaml.load(uc, Loader=yaml.FullLoader)
    print("Running tests with the following configuration:")
    print("-----------------------------------------------")
    print(yaml.dump(user_info, default_flow_style=False))
    print()

    return user_info


# Parsing
parser = argparse.ArgumentParser(
    description="Automatic testing for ESM-Tools devs"
)
parser.add_argument("-n", "--no-user", default=False, help="Avoid loading user config", action="store_true")
parser.add_argument("-c", "--no-comp", default=False, help="Do not compile", action="store_true")
parser.add_argument("-r", "--no-run", default=False, help="Do not run", action="store_true")

args = vars(parser.parse_args())
ignore_user_info = args["no_user"]
actually_compile = not args["no_comp"]
actually_run = not args["no_run"]


# Get user info for testing
if not ignore_user_info:
    user_info = user_config()
else:
    user_info = None

print(user_info)
print(actually_compile)
print(actually_run)


# Gather tests
# Input












































































































































































