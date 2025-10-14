#!/usr/bin/env python

from argparse import ArgumentParser
from dataclasses import dataclass
import os
import re
from textwrap import dedent

import requests
from bs4 import BeautifulSoup

PYTHON_DOWNLOADS_URL = "https://www.python.org/downloads/"
README_PATH = "README.md"
LONESNAKE_SCRIPT_PATH = "lonesnake"
LONESNAKE_KIT_SCRIPT_PATH = os.path.join("helpers", "lonesnake-kit")


@dataclass(frozen=True, order=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def minor_version(self) -> str:
        return f"{self.major}.{self.minor}"


def main() -> None:
    parser = ArgumentParser(description="Manage lonesnake script versions.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "current-prog-version", help="Get the PROG_VERSION from lonesnake script"
    )
    subparsers.add_parser(
        "next-prog-version",
        help=(
            "Get the next PROG_VERSION by adding 1 minor version to existing "
            "PROG_VERSION from lonesnake script"
        ),
    )
    subparsers.add_parser(
        "is-new-update-available",
        help=(
            "Check if new updates are available on python.org compared to "
            "lonesnake script patch block"
        ),
    )
    subparsers.add_parser(
        "overwrite-latest-patch-block",
        help="Overwrite the latest patch block in lonesnake script",
    )
    overwrite_prog_version_parser = subparsers.add_parser(
        "overwrite-prog-version",
        help="Overwrite the PROG_VERSION in lonesnake and lonesnake-kit and README",
    )
    overwrite_prog_version_parser.add_argument("prog_version")

    args = parser.parse_args()
    if args.command == "current-prog-version":
        lonesnake_prog_version = find_prog_version(LONESNAKE_SCRIPT_PATH)
        print(lonesnake_prog_version)
    elif args.command == "next-prog-version":
        lonesnake_prog_version = find_prog_version(LONESNAKE_SCRIPT_PATH)
        print(
            SemanticVersion(
                major=lonesnake_prog_version.major,
                minor=lonesnake_prog_version.minor + 1,
                patch=lonesnake_prog_version.patch,
            )
        )
    elif args.command == "is-new-update-available":
        pythondotorg_versions = collect_pythondotorg_versions()
        lonesnake_versions = collect_lonesnake_versions(LONESNAKE_SCRIPT_PATH)
        required_updates = determine_required_cpython_patch_updates(
            pythondotorg_versions, lonesnake_versions
        )

        if len(required_updates) >= 1:
            print(
                "The following CPython version updates can be applied to the "
                "lonesnake script:"
            )
            for update in required_updates:
                print(f"- minor {update[0]}: {update[1].patch} => {update[2].patch}")
        else:
            print("NO UPDATE AVAILABLE")
    elif args.command == "overwrite-latest-patch-block":
        pythondotorg_versions = collect_pythondotorg_versions()
        overwrite_latest_patch_block(LONESNAKE_SCRIPT_PATH, pythondotorg_versions)
    elif args.command == "overwrite-prog-version":
        new_prog_version = parse_prog_version(args.prog_version)
        overwrite_scripts_prog_version(
            LONESNAKE_SCRIPT_PATH,
            LONESNAKE_KIT_SCRIPT_PATH,
            new_prog_version,
        )
        overwrite_readme_prog_version(README_PATH, new_prog_version)
    else:
        parser.print_help()


def extract_versions(html_content: str) -> list[SemanticVersion]:
    soup = BeautifulSoup(html_content, "html.parser")
    download_list_widget = soup.find("div", class_="row download-list-widget")
    version_container = download_list_widget.find(
        "ol", class_="list-row-container menu"
    )
    version_spans = version_container.find_all("span", class_="release-number")

    return sorted(
        [pythondotorg_version_to_semantic(span.text) for span in version_spans]
    )


def pythondotorg_version_to_semantic(version_string: str) -> SemanticVersion:
    pattern = re.compile(r"Python (\d+)\.(\d+)\.(\d+)")
    version_match = pattern.search(version_string)
    if not version_match:
        raise ValueError(f"Invalid version string format: {version_string}")
    major, minor, patch = map(int, version_match.groups())
    return SemanticVersion(major=major, minor=minor, patch=patch)


def parse_prog_version(version_string) -> SemanticVersion:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_string)
    if not match:
        raise RuntimeError(
            f"Invalid version format: {version_string}. Expected format: X.Y.Z"
        )

    return SemanticVersion(
        int(match.group(1)), int(match.group(2)), int(match.group(3))
    )


def get_latest_patch_versions(
    versions: list[SemanticVersion],
) -> dict[str, SemanticVersion]:
    latest_versions: dict[str, SemanticVersion] = {}

    for version in versions:
        if (
            version.minor_version not in latest_versions
            or version.patch > latest_versions[version.minor_version].patch
        ):
            latest_versions[version.minor_version] = version

    return latest_versions


def collect_pythondotorg_versions():
    downloads_html_response = requests.get(PYTHON_DOWNLOADS_URL)
    downloads_html_response.raise_for_status()

    all_versions = extract_versions(downloads_html_response.text)
    supported_versions = [
        version for version in all_versions if version.major == 3 and version.minor >= 7
    ]
    return get_latest_patch_versions(supported_versions)


def find_prog_version(filepath: str) -> SemanticVersion:
    with open(filepath, "r") as file:
        for line in file:
            prog_version_match = re.search(
                r'readonly PROG_VERSION="(\d+)\.(\d+)\.(\d+)"', line
            )
            if prog_version_match:
                major, minor, patch = map(int, prog_version_match.groups())
                return SemanticVersion(major=major, minor=minor, patch=patch)

    raise ValueError("Version line not found in the file")


def collect_lonesnake_versions(
    lonesnake_script_path: str,
) -> dict[str, SemanticVersion]:
    pattern = re.compile(r'readonly LATEST_PATCH_CP3(\d{1,2})="(\d+)"')
    minor_to_patch = {}
    with open(lonesnake_script_path) as lonesnake_script_file:
        for line in lonesnake_script_file:
            latest_patch_match = pattern.match(line.strip())
            if latest_patch_match:
                minor_version_code = latest_patch_match.group(1)
                patch_version = int(latest_patch_match.group(2))
                minor_version_number = int(minor_version_code)
                minor_version_str = f"3.{minor_version_number}"
                cpython_version = SemanticVersion(
                    major=3, minor=minor_version_number, patch=patch_version
                )
                minor_to_patch[minor_version_str] = cpython_version

    return minor_to_patch


def overwrite_latest_patch_block(
    lonesnake_script_path: str, pythondotorg_patch_versions: dict[str, SemanticVersion]
) -> None:
    latest_patch_block = dedent(
        f"""
        # Latest patch version number for each supported Python minor version
        readonly LATEST_PATCH_CP37="{pythondotorg_patch_versions['3.7'].patch}"
        readonly LATEST_PATCH_CP38="{pythondotorg_patch_versions['3.8'].patch}"
        readonly LATEST_PATCH_CP39="{pythondotorg_patch_versions['3.9'].patch}"
        readonly LATEST_PATCH_CP310="{pythondotorg_patch_versions['3.10'].patch}"
        readonly LATEST_PATCH_CP311="{pythondotorg_patch_versions['3.11'].patch}"
        readonly LATEST_PATCH_CP312="{pythondotorg_patch_versions['3.12'].patch}"
        readonly LATEST_PATCH_CP313="{pythondotorg_patch_versions['3.13'].patch}"
        readonly LATEST_PATCH_CP314="{pythondotorg_patch_versions['3.14'].patch}"
    """
    ).strip()

    # Replace the old block with the new block
    pattern = (
        r"# Latest patch version number for each supported Python minor version\n"
        r'(readonly LATEST_PATCH_CP\d+="\d+"\n)+'
    )

    with open(lonesnake_script_path, "r+") as lonesnake_script_file:
        lonesnake_script_content = lonesnake_script_file.read()
        lonesnake_script_file.truncate(0)
        lonesnake_script_file.seek(0)
        updated_content = re.sub(
            pattern, f"{latest_patch_block}\n", lonesnake_script_content
        )
        lonesnake_script_file.write(updated_content)


def determine_required_cpython_patch_updates(
    pythondotorg_versions: dict[str, SemanticVersion],
    lonesnake_versions: dict[str, SemanticVersion],
) -> list[tuple[str, SemanticVersion, SemanticVersion]]:
    required_updates = []
    for minor_version, lonesnake_version in lonesnake_versions.items():
        if minor_version not in pythondotorg_versions:
            raise RuntimeError(
                f"Could not find minor version '{minor_version}' in python.org "
                f"patch versions: {pythondotorg_versions}"
            )

        pythondotorg_version = pythondotorg_versions[minor_version]

        if pythondotorg_version > lonesnake_version:
            required_updates.append(
                (minor_version, lonesnake_version, pythondotorg_version)
            )

    return required_updates


def overwrite_scripts_prog_version(
    lonesnake_script_path: str,
    lonesnake_kit_script_path: str,
    new_lonesnake_prog_version: SemanticVersion,
) -> None:
    for script_path in [lonesnake_script_path, lonesnake_kit_script_path]:
        with open(script_path, "r+") as script_file:
            lonesnake_script_content = script_file.read()
            script_file.truncate(0)
            script_file.seek(0)
            script_file.write(
                re.sub(
                    r"readonly PROG_VERSION=\"[0-9]+.[0-9]+.[0-9]+\"",
                    f'readonly PROG_VERSION="{new_lonesnake_prog_version}"',
                    lonesnake_script_content,
                )
            )


def overwrite_readme_prog_version(
    readme_path: str, new_lonesnake_prog_version: SemanticVersion
) -> None:
    github_repo_raw_prefix = "https://raw.githubusercontent.com/pwalch/lonesnake"
    with open(readme_path, "r+") as readme_file:
        readme_content = readme_file.read()
        readme_file.truncate(0)
        readme_file.seek(0)
        readme_file.write(
            re.sub(
                rf"{github_repo_raw_prefix}/[0-9]+.[0-9]+.[0-9]+",
                rf"{github_repo_raw_prefix}/{new_lonesnake_prog_version}",
                readme_content,
            )
        )


if __name__ == "__main__":
    main()
