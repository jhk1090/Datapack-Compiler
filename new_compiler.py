from lark import Lark, Token
from logger import L
import os
import shutil
from transform import DatapackGenerater, error_as_txt, modify_file_data
from consts import planet_parser, NEW_LINE
import datetime
import sys

  
logger = L()


datapack_versions = {
    "1.20.4": "26",
    "1.20.6": "41",
    "1.21": "48",
    "1.21.1": "48",
    "1.21.2": "57",
    "1.21.3": "57",
    "1.21.4": "61"
}

# 네임스페이스/functions, tick.json, load.json 삭제 후 재생성
def make_basic_files(version, file_dir, namespace = "pack"):
    logger.debug("make_basic_files", f"version: {version}, file_dir: {file_dir}, namespace: {namespace}")

    function_folder = "function"
    if version[:4] == "1.20": function_folder = "functions"

    function_folder_dir = file_dir + f"{namespace}/data/{namespace}/{function_folder}"
    tag_folder_dir = file_dir + f"{namespace}/data/minecraft/tags/{function_folder}"

    # if os.path.exists(file_dir + f"{namespace}/data/{namespace}/{function_folder}"): shutil.rmtree(file_dir + f"{namespace}/data/{namespace}/{function_folder}")
    if os.path.exists(function_folder_dir): shutil.rmtree(function_folder_dir)

    if not os.path.exists(tag_folder_dir): os.makedirs(tag_folder_dir)
    if not os.path.exists(function_folder_dir): os.makedirs(function_folder_dir)

    file = open(file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/load.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:load\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/tick.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:tick\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/{function_folder}/load.mcfunction", "w+")
    file.write(f"\
# This data pack was compiled with the 40planet's compiler.\n\
# https://github.com/alexmonkey05/Datapack-Compiler\n\n")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/{function_folder}/tick.mcfunction", "w+")
    file.close()
    file = open(file_dir + f"{namespace}/pack.mcmeta", "w+")
    file.write('{ "pack": {"pack_format": ' + datapack_versions[version] + ', "description": "by 40planet"} }')
    file.close()


def generate_datapack(filename, version, result_dir = "./", namespace = "pack"):
    # 파일 경로 가공
    result_dir = result_dir.strip()
    namespace = namespace.strip()
    if result_dir == "" or namespace == "":
        logger.critical("\n\nresult directory and namespace can not be empty string\n")
        return
    if result_dir[-1] != "/" and result_dir[-1] != "\\":
        result_dir += "/"

    # 데이터팩 기본 경로 만들기
    make_basic_files(version, result_dir, namespace)

    # 파일 경로 가공
    if len(filename) < 7 or filename[-7:] != ".planet": filename += ".planet"

    # .planet 파일 존재 확인
    if not os.path.isfile(filename):
        raise ValueError(error_as_txt(None, f"\"{filename}\" does not exist", filename, "", "fdsa"))


    # 파싱
    now = datetime.datetime.now()
    parser_tree = None
    with open(filename, "r", encoding="utf-8") as file:
        logger.debug("open_file", f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")
        
        now = datetime.datetime.now()
        file_data = modify_file_data(file.read())

    parser_tree = planet_parser.parse(file_data + "\n")
    logger.debug("parse_file",f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")

    # make_basic_files("1.21", "./", "pack")

    # 트랜스폼
    now = datetime.datetime.now()
    # print(parser_tree.pretty())
    datapack_generator = DatapackGenerater(version, result_dir, namespace, filename)
    datapack_generator.transform(parser_tree)
    logger.debug("interprete_file", f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")
    return parser_tree

import argparse
values = ["1.20.4", "1.20.6", "1.21", "1.21.1", "1.21.2", "1.21.3", "1.21.4"]
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='comet_compiler',
                    description='Compile .planet files')
    parser.add_argument('--cli', action='store_true')      # option that takes a value
    parser.add_argument('-p', '--planet')
    parser.add_argument('-v', '--version')
    parser.add_argument('-d', '--dist')
    parser.add_argument('-n', '--name')
    args = parser.parse_args()
    if args.cli:
        logger.log("===============================================")
        logger.log("  ██████╗ ██████╗ ███╗   ███╗███████╗████████╗ ")
        logger.log(" ██╔════╝██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝ ")
        logger.log(" ██║     ██║   ██║██╔████╔██║█████╗     ██║    ")
        logger.log(" ██║     ██║   ██║██║╚██╔╝██║██╔══╝     ██║    ")
        logger.log(" ╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗   ██║    ")
        logger.log("  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝    ")
        logger.log("===============================================")

        now = datetime.datetime.now()

        v = args.version
        if v not in values or v == "":
            logger.critical(f"Invalid version: {v} / Required version: {values}")
            sys.exit(0)
        p = args.planet
        d = args.dist
        if p == None:
            logger.critical("planet file(-p / --planet) is required")
            sys.exit(0)
        if d == None:
            logger.critical("dist folder(-d / --dist) is required")
            sys.exit(0)
        n = args.name
        if n == None: 
            n = "pack"
            logger.info("namespace", f"namespace is not defined, using default namespace: {logger.prGreen(n)}")
        
        try:
            interprete_result = generate_datapack(p, v, d, n)
        except ValueError as err:
            print(err)
            sys.exit()
            logger.critical(err)
        took = int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000
        logger.log(f"Done! Took {logger.prYello(took)}s")


        sys.exit(0)

    import eel
    import tkinter
    from tkinter import filedialog

    eel.init("web");

    @eel.expose
    def event(name, dir, version, namespace):
        try:
            generate_datapack(name, version, dir, namespace)
            return "success"
        except BaseException as error:
            return str(error)
        

    @eel.expose
    def select_planet_file():
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        result = filedialog.askopenfile(
            title="파일 선택창",
            filetypes=(('planet files', '*.planet'), ('all files', '*.*'))
        )
        if result:
            return result.name
        else:
            return ""

    @eel.expose
    def select_folder():
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        directory_path = filedialog.askdirectory()
        return directory_path


    import webbrowser
    @eel.expose
    def open_folder(path):
        webbrowser.open(f"file:///{path}")

    print("The compiler is hosted on http://localhost:8000!")
    eel.start('index.html', size=(600, 800), mode="default")  # Start
