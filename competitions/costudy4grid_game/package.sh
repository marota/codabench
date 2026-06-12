#!/usr/bin/env bash
# Copyright (c) 2025-2026, RTE (https://www.rte-france.com)
# SPDX-License-Identifier: MPL-2.0
#
# Build the uploadable Codabench competition bundle for Co-Study4Grid Game Mode.
# Produces dist/costudy4grid_game_bundle.zip containing competition.yaml, the
# markdown pages, the logo, and the zipped program/data folders referenced by
# competition.yaml.
set -euo pipefail
cd "$(dirname "$0")"

DIST="dist"
rm -rf "$DIST"
mkdir -p "$DIST"

echo "Zipping program/data folders…"
( cd scoring_program && zip -qr "../$DIST/scoring_program.zip" . -x '*/__pycache__/*' )
( cd ingestion_program && zip -qr "../$DIST/ingestion_program.zip" . -x '*/__pycache__/*' )
( cd reference_data && zip -qr "../$DIST/reference_data.zip" . )
( cd starting_kit && zip -qr "../$DIST/starting_kit.zip" . )

echo "Assembling bundle…"
cp competition.yaml overview.md evaluation.md data.md terms.md "$DIST/"
[ -f logo.png ] && cp logo.png "$DIST/"

( cd "$DIST" && zip -qr "costudy4grid_game_bundle.zip" \
    competition.yaml overview.md evaluation.md data.md terms.md \
    $( [ -f logo.png ] && echo logo.png ) \
    scoring_program.zip ingestion_program.zip reference_data.zip starting_kit.zip )

echo "Bundle ready: $DIST/costudy4grid_game_bundle.zip"
