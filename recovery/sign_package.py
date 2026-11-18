#!/usr/bin/env python3
"""Run the unchanged Vetro signer with existing project certificates; no TV access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-name", default="vetro-integration-SIGNED.wgt")
    args = parser.parse_args()
    if not re.fullmatch(r"vetro-[a-zA-Z0-9-]+\.wgt", args.output_name):
        parser.error("Choose a vetro-*.wgt filename inside dist")
    repo = Path(__file__).resolve().parents[1]
    project = repo.parent
    private = project / "recovery/private"
    profile = private / "apps2samsung/Certificate/Jelly2Sams - Partner"
    output = repo / "dist" / args.output_name
    if output.exists() or output.is_symlink():
        raise SystemExit("Signed output already exists; preserve it instead of overwriting")
    for name in ("author.p12", "distributor.p12", "password.txt"):
        if not (profile / name).is_file() or (profile / name).is_symlink():
            raise SystemExit("Expected local signing material is missing or a symlink")
    password = (profile / "password.txt").read_text().strip()
    if not password:
        raise SystemExit("Empty certificate password")
    env = {key: value for key, value in os.environ.items() if key in ("HOME", "LANG", "LC_ALL")}
    env.update({
        "PATH": "/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
        "TMPDIR": str(private / "tool-tmp"),
        "OPENSSL_CONF": str(private / "offline-tmp/openssl.cnf"),
        "AUTHOR_P12": str(profile / "author.p12"),
        "DIST_P12": str(profile / "distributor.p12"),
        "AUTHOR_PW": password, "DIST_PW": password,
        "OUT": str(output),
    })
    # No passwords in command arguments, logs or result manifests.
    os.umask(0o077)
    result = subprocess.run([
        "/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node",
        str(repo / "rooting/build.cjs")], cwd=str(repo), env=env,
        capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise SystemExit("Vetro signing failed (exit %d); preserve private files for diagnosis" % result.returncode)
    output.chmod(0o600)
    print(json.dumps({"file": output.name, "bytes": output.stat().st_size,
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                      "signed_by_upstream_builder": True, "tv_contacted": False}))


if __name__ == "__main__":
    main()
