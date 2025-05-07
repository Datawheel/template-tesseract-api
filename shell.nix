{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.python-dotenv
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.poetry
  ];
  shellHook = ''
    export POETRY_VIRTUALENVS_IN_PROJECT=true
    test -d .venv && source .venv/bin/activate
  '';
}
