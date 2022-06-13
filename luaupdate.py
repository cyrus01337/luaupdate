#!/usr/bin/env python3
"""
CLI Luau installer and updater

TODO: types
TODO: create install script that adds it to path
"""
import argparse
import json
import os
import pathlib
import stat
import shutil
import subprocess
import sys
import zipfile

import distro
import requests

LATEST_RELEASE = "https://api.github.com/repos/Roblox/luau/releases/latest"
CACHE_DIRECTORY = pathlib.Path(".cache/")
CACHE_SETTINGS = CACHE_DIRECTORY /  ".settings.json"
PARSER = argparse.ArgumentParser(prog="luaupdate", description="CLI Luau installer and updater")


def set_ownership_of(path):
    full_path = str(path)
    sudo_user = os.environ.get("SUDO_USER", os.environ["USER"])

    shutil.chown(full_path, sudo_user)


def set_as_executable(path):
    path_stat = path.stat()

    path.chmod(path_stat.st_mode | stat.S_IXOTH | stat.S_IXGRP | stat.S_IXOTH)


def get_cache_settings():
    settings = {}

    CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    set_ownership_of(CACHE_DIRECTORY)


    if CACHE_SETTINGS.exists():
        with CACHE_SETTINGS.open("r") as fh:
            settings = json.load(fh)
    else:
        with CACHE_SETTINGS.open("w") as fh:
            json.dump(settings, fh)

    return settings


def set_cache_settings(settings = None, **kwargs):
    settings = settings or get_cache_settings()

    for setting, value in kwargs.items():
        settings[setting] = value

    with CACHE_SETTINGS.open("w") as fh:
        json.dump(settings, fh)


def resolve_asset_name_from_os_name(version):
    platform = None

    match sys.platform:
        case "linux" | "linux2":
            name, _, _ = distro.linux_distribution(full_distribution_name=False)

            if name == "ubuntu":
                platform = name

        case "darwin":
            platform = "macos"

        case "win32":
            platform = "windows"

    if platform:
        return f"luau-{platform}.zip"


def get_asset_url(assets, name):
    for asset in assets:
        if asset["name"] == name:
            return asset["browser_download_url"]

    return None


def maybe_fetch_asset(payload, *, version):
    directory = CACHE_DIRECTORY / version
    assets = payload["assets"]
    zipball_url = payload["zipball_url"]
    name = resolve_asset_name_from_os_name(version)
    url = get_asset_url(assets, name) or zipball_url
    fetched_zipball = url == zipball_url
    file = directory / "luau-source.zip" if fetched_zipball else directory / os.path.basename(url)

    if file.exists():
        return file, None

    response = requests.request("GET", url)

    directory.mkdir(parents=True, exist_ok=True)
    set_ownership_of(directory)

    with file.open("wb", encoding=response.encoding) as fh:
        fh.write(response.content)

    set_ownership_of(file)
    set_as_executable(file)

    return file, fetched_zipball


def get_installation_directory():
    bin = None
    sudo_user = None
    commands = []
    path = os.environ["PATH"]

    match sys.platform:
        case "linux" | "linux2" | "darwin":
            sudo_user = os.environ.get("SUDO_USER", os.environ["USER"])
            home = os.path.expanduser(f"~{sudo_user}")
            bin = pathlib.Path(home, "bin/")

        case "win32":
            commands = ["setx", "-x", f"{path};{bin}"]
            bin = pathlib.Path(os.environ["PROGRAMFILESX86"], "luau")

    bin_path = str(bin)

    if not (bin.exists() or bin_path in path):
        bin.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(commands, shell=True)
        set_ownership_of(bin)

    return bin


def compile_from_source(destination):
    pass


def main():
    args = PARSER.parse_args()
    settings = get_cache_settings()
    response = requests.request("GET", LATEST_RELEASE)
    payload = response.json()
    latest_version = payload["tag_name"]

    if latest_version == settings.get("version", None):
        return 1

    asset, is_zipball = maybe_fetch_asset(payload, version=latest_version)
    directory = get_installation_directory() or asset.parent

    with zipfile.ZipFile(asset, "r") as zip_fh:
        for name in zip_fh.namelist():
            path = directory / name

            with path.open("wb")
        # zip_fh.extractall(directory)

    if is_zipball:
        compile_from_source(directory)

    set_cache_settings(settings, version=latest_version)

    return 0


if __name__ == "__main__":
    main()
