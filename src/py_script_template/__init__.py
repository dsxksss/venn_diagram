import argparse
import logging
import sys
import os
import toml
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from typing import Dict
from .utils import set_logging_default_config, set_progress_value


def get_cli_argument(config_path: str) -> Dict:
    """
    从TOML配置文件中读取并解析命令行参数。
    """
    config = toml.load(config_path)
    parser = argparse.ArgumentParser(description=config.get("description", "CLI Tool"))

    for arg, details in config.get("arguments", {}).items():
        parser.add_argument(
            f"--{arg}",
            required=details.get("required", False),
            choices=details.get("choices"),
            default=details.get("default"),
            help=details.get("help"),
            type=eval(details.get("type", "str")),
        )

    parsed_args = parser.parse_args(sys.argv[1:])
    return vars(parsed_args)


def read_file(file_path, case_sensitive):
    with open(file_path, "r") as f:
        lines = f.read().splitlines()
    return set(line if case_sensitive else line.lower() for line in lines)


def create_venn_diagram(args):
    labels = args["labels"].split(",")
    input_file1 = args["input_file1"]
    input_file2 = args["input_file2"]
    output_name = args["output_name"]
    img_name = args["img_name"]
    format = args["format"]
    case_sensitive = args["case_sensitive"].lower() == "yes"
    save_dir = args["save_dir"]

    if len(labels) != 2:
        raise ValueError("labels and input_files must have the same length")

    data_sets = [read_file(file, case_sensitive) for file in [input_file1, input_file2]]

    if len(data_sets) == 2:
        venn = venn2(data_sets, set_labels=labels)
    elif len(data_sets) == 3:
        venn = venn3(data_sets, set_labels=labels)
    else:
        raise ValueError("This script supports only 2 or 3 sets for Venn diagrams")

    intersection = set.intersection(*data_sets)

    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, output_name)
    with open(output_path, "w") as f:
        for item in intersection:
            f.write(f"{item}\n")

    print(f"Intersection data saved to: {output_path}")

    if format == "all":
        jpg_path = os.path.join(save_dir, f"{img_name}.jpg")
        png_path = os.path.join(save_dir, f"{img_name}.png")
        plt.savefig(jpg_path)
        plt.savefig(png_path)
        print(f"Venn diagram saved to: {jpg_path} and {png_path}")
    else:
        img_path = os.path.join(save_dir, f"{img_name}.{format}")
        plt.savefig(img_path)
        print(f"Venn diagram saved to: {img_path}")


def main() -> int:
    try:
        # 获取当前脚本的文件路径
        script_path = __file__

        # 获取当前脚本所在的目录
        script_dir = os.path.dirname(script_path)
        
        set_progress_value(5)
        set_logging_default_config()

        config_file = os.path.join(script_dir, "..", "..", "cli_config.toml")
        arguments = get_cli_argument(config_file)
        set_progress_value(45)

        logging.debug(f"Input Arguments: {arguments}")
        set_progress_value(80)
        create_venn_diagram(arguments)
        set_progress_value(100)
        return 0
    except Exception as e:
        sys.stderr.write(f"{e}")
        return 100
