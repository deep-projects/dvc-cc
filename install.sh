#!/usr/bin/env batch
pip uninstall dist/dvc_cc-0.2.0-py3-none-any.whl -y
poetry build
pip install dist/dvc_cc-0.2.0-py3-none-any.whl
