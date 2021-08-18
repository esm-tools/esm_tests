import os
import sys
import subprocess
import argparse
import math
import yaml
import re
import shutil
import time
import glob

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
    # Load test info
    test_config = f"{script_dir}/test_config.yaml"
    if os.path.isfile(test_config):
        with open(test_config, "r") as t:
            test_info = yaml.load(t, Loader=yaml.FullLoader)
    else:
        test_info = {}
    if len(test_info)>0:
        test_all = False
    else:
        test_all = True
    for model in os.listdir(runscripts_dir):
        if test_all or test_info.get(model, False):
            scripts_info[model] = {}
            for script in os.listdir(f"{runscripts_dir}/{model}"):
                if test_all or isinstance(test_info.get(model), str) or script in test_info.get(model, []):
                    if script != "config.yaml" and ".swp" not in script:
                        scripts_info[model][script.replace(".yaml", "")] = {}
                        scripts_info[model][script.replace(".yaml", "")][
                            "path"
                        ] = f"{runscripts_dir}/{model}/{script}"
                        scripts_info[model][script.replace(".yaml", "")]["state"] = {}
                        ns += 1
    scripts_info["general"] = {"num_scripts": ns}
    return scripts_info


def read_info_from_rs(scripts_info):
    new_loader = create_env_loader()
    for model, scripts in scripts_info.items():
        if model == "general":
            continue
        for script, v in scripts.items():
            # runscript = esm_parser.yaml_file_to_dict(v["path"])
            with open(v["path"], "r") as rs:
                runscript = yaml.load(rs, Loader=yaml.SafeLoader)
            v["version"] = runscript[model]["version"]

    return scripts_info


def create_env_loader(tag="!ENV", loader=yaml.SafeLoader):
    # Necessary to ignore !ENV variables
    def constructor_env_variables(loader, node):
        return ""

    loader.add_constructor(tag, constructor_env_variables)
    return loader


def sh(inp_str, env_vars=[]):
    ev = ""
    for v in env_vars:
        ev += f"export {v}; "
    inp_str = f"{ev}{inp_str}"
    p = subprocess.Popen(
        inp_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
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
                v["action"] = {"comp": "Directory already exists"}
                logger.info(f"\t\tDirectory already exists, skipping")
                with open(f"{model_dir}/comp.out") as o:
                    out = o.read()
            else:
                # Gets the source code if actual compilation is required
                if actually_compile:
                    get_command = f"esm_master get-{model}-{version} --no-motd"
                    logger.info("\t\tDownloading")
                    out = sh(get_command)
                    if "Traceback (most recent call last):" in out:
                        logger.error(f"\t\t\tProblem downloading!\n\n{out}")
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

    return scripts_info


def check(mode, model, version, out, script, v):
    success = True
    mode_name = {"comp": "compilation", "submission": "submission", "run": "runtime"}
    # Load config
    with open(f"{os.path.dirname(v['path'])}/config.yaml", "r") as c:
        config_test = yaml.load(c, Loader=yaml.FullLoader)
    if mode == "submission":
        config_mode = "run"
    else:
        config_mode = mode
    if config_mode not in config_test:
        logger.error(
            f"Missing '{mode}' section in '{os.path.dirname(v['path'])}/config.yaml'!"
        )
    config_test = config_test[config_mode]
    # Check for files that should exist
    if mode == "comp":
        actually_do = actually_compile
    elif mode == "run":
        actually_do = actually_run
    elif mode == "submission":
        # Do not perform the file checks before the simulation is finished
        actually_do = False
    # Check for errors during submission
    if mode == "submission":
        errors = config_test.get("actual", {}).get("errors", [])
        errors.append("Traceback (most recent call last):")
        for error in errors:
            if error in out:
                logger.error(f"\t\tError during {mode_name[mode]}!\n\n{out}")
                success = False
        v["state"][mode] = success
    # Check for missing files and errors during an actual operation (not a check)
    if actually_do:
        # Check for errors in the output
        errors = config_test.get("actual", {}).get("errors", [])
        if mode == "comp":
            errors.append("errors occurred!")
            subfolder = f"{model}-{version}"
        if mode == "run":
            subfolder = script
        for error in errors:
            if error in out:
                logger.error(f"\t\tError during {mode_name[mode]}!\n\n{out}")
                success = False
        if mode != "run":
            v["state"][mode] = success
        # Check if files exist
        files_checked = exist_files(
            config_test.get("actual", {}).get("files", []),
            f"{user_info['test_dir']}/{mode}/{model}/{subfolder}",
        )
        v["state"][f"{mode}_files"] = files_checked
        success = success and files_checked
    # Compare scripts with previous, if existing

    return success


def exist_files(files, path):
    files_checked = True
    for f in files:
        if "*" in f:
            listing = glob.glob(f"{path}/{f}")
            if len(listing) == 0:
                logger.error(f"\t\tNo files following the pattern '{f}' were created!")
                files_checked = False
        else:
            if not os.path.isfile(f"{path}/{f}"):
                logger.error(f"\t\t'{f}' does not exist!")
                files_checked = False
    return files_checked


def run_test(scripts_info, actually_run):
    c = 0
    submitted = []
    # Loop through tests
    for model, scripts in scripts_info.items():
        if model == "general":
            continue
        for script, v in scripts.items():
            c += 1
            progress = round(c / scripts_info["general"]["num_scripts"] * 100, 1)
            version = v["version"]
            runscript_path = v["path"]
            general_run_dir = f"{user_info['test_dir']}/run/{model}/"
            run_dir = f"{general_run_dir}/{script}"
            model_dir = f"{user_info['test_dir']}/comp/{model}/{model}-{version}"
            logger.info(f"\tSUBMITTING ({progress}%) {model}/{script}:")
            if not os.path.isdir(general_run_dir):
                os.makedirs(general_run_dir)

            # Check if the simulation exists
            if os.path.isdir(run_dir):
                v["action"]["submission"] = "Directory already exists"
                logger.info(f"\t\tDirectory already exists, skipping")
                with open(f"{run_dir}/run.out", "r") as o:
                    out = o.read()
                if actually_run:
                    submitted.append((model, script))
            else:
                os.chdir(os.path.dirname(runscript_path))

                if actually_run:
                    check_flag = ""
                else:
                    check_flag = "-c"
                # Export test variables
                env_vars = [
                    f"ACCOUNT='{user_info['account']}'",
                    f"ESM_TESTING_DIR='{general_run_dir}'",
                    f"MODEL_DIR='{model_dir}'",
                ]
                run_command = (
                    f"esm_runscripts {v['path']} -e {script} --open-run {check_flag}"
                )
                out = sh(run_command, env_vars)

                # Write output file
                with open(f"{run_dir}/run.out", "w") as o:
                    o.write(out)

                if actually_run:
                    submitted.append((model, script))

            # Check submission
            success = check("submission", model, version, out, script, v)

    # Check if simulations are finished
    total_sub = len(submitted)
    subc = 1
    if total_sub > 0:
        logger.info(
            "\nWaiting for submitted runs to finish... You can choose to cancel the "
            + "script now and come back to it at a later state with the same command "
            + "you submitted it, but remember to remove the '-d' so that nothing is "
            + "deleted and this script can be resumed from where it was."
        )
    infoc = 10
    while submitted:
        cc = 0
        finished_runs = []
        for model, script in submitted:
            v = scripts_info[model][script]
            progress = round(subc / total_sub * 100, 1)
            exp_dir = f"{user_info['test_dir']}/run/{model}/{script}/"
            exp_dir_scripts = f"{exp_dir}/scripts/"
            for f in os.listdir(exp_dir_scripts):
                if "monitoring_file" in f and ".out" in f:
                    with open(f"{exp_dir_scripts}/{f}") as m:
                        monitoring_out = m.read()
                        if (
                            "Reached the end of the simulation, quitting"
                            in monitoring_out
                        ):
                            logger.info(
                                f"\tRUN FINISHED ({progress}%) {model}/{script}"
                            )
                            logger.info(f"\t\tSuccess!")
                            finished_runs.append(cc)
                            subc += 1
                            v["state"]["run_finished"] = True
                            success = check("run", model, version, "", script, v)
                        elif "ERROR:" in monitoring_out:
                            logger.info(
                                f"\tRUN FINISHED ({progress}%) {model}/{script}"
                            )
                            logger.error(f"\t\tSimulation crashed!")
                            finished_runs.append(cc)
                            subc += 1
                            v["state"]["run_finished"] = False
                            success = check("run", model, version, "", script, v)
            if not keep_run_folders:
                folders_to_remove = ["run_", "restart", "outdata", "input", "forcing", "unknown"]
                logger.debug(f"\t\tDeleting {folders_to_remove}")
                for folder in os.listdir(exp_dir):
                    for fr in folders_to_remove:
                        if fr in folder:
                            shutil.rmtree(f"{exp_dir}/{folder}")
                            continue
            # append to finished runs
            cc += 1
        for indx in finished_runs[::-1]:
            del submitted[indx]

        if infoc == 10 and len(submitted) > 0:
            infoc = 0
            runs = ""
            for model, script in submitted:
                runs += f"\t- {model}/{script}\n"
            logger.info(f"\nWaiting for the following runs to finish:\n{runs}")
        else:
            infoc += 1
        if len(submitted) > 0:
            time.sleep(30)

    return scripts_info


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
    "-r",
    "--run",
    default=False,
    help="Compile and run the scripts",
    action="store_true",
)
parser.add_argument(
    "-d", "--delete", default=False, help="Delete previous tests", action="store_true"
)
parser.add_argument(
    "-k",
    "--keep",
    default=False,
    help="Keep run_, outdata and restart folders for runs",
    action="store_true",
)


args = vars(parser.parse_args())
ignore_user_info = args["no_user"]
actually_compile = args["comp"]
actually_run = args["run"]
if actually_run:
    actually_compile = True
delete_tests = args["delete"]
keep_run_folders = args["keep"]

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

# Delete previous tests TODO: do this only for the scripts that are gonna be run
if delete_tests:
    logger.debug("Deleting previous tests")
    if os.path.isdir(f"{user_info['test_dir']}/comp/"):
        shutil.rmtree(f"{user_info['test_dir']}/comp/")
    if os.path.isdir(f"{user_info['test_dir']}/run/"):
        shutil.rmtree(f"{user_info['test_dir']}/run/")

# Gather scripts
scripts_info = get_scripts()

# TODO: Cut down info with user_scripts

# Complete scripts_info
scripts_info = read_info_from_rs(scripts_info)


# Compile
comp_test(scripts_info, actually_compile)

# Run
run_test(scripts_info, actually_run)

# TODO: run comparisons if they exist and print a file

# TODO: final output display

# TODO: Do you want to save your compared files?
yprint(scripts_info)
