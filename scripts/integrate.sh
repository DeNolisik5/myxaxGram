#!/usr/bin/env bash
#
# Assembles the myxaxGram source tree inside CI:
#
#   Cherrygram (pinned) + exteraless plugin runtime (pinned) + Chaquopy fork
#   + this repository's overlay and patches.
#
# Nothing here is committed to the myxaxGram repository: the checkout is built
# from scratch on every run so upstream stays reproducible and the public repo
# only carries the integration code.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="${BUILD_ROOT:-$REPO_DIR/build-src}"
SRC="$BUILD_ROOT/app"

CHERRY_REPO="${CHERRY_REPO:-https://github.com/arsLan4k1390/Cherrygram.git}"
CHERRY_SHA="${CHERRY_SHA:-3050af6d948acc27db446f6cd27a8e200b205c1b}"

EL_REPO="${EL_REPO:-https://github.com/exteraless/exteraless.git}"
EL_SHA="${EL_SHA:-c83765c4151d50ba514325ddf0a3262769729dc6}"

CHAQUOPY_REPO="${CHAQUOPY_REPO:-https://github.com/exteraless/chaquopy.git}"
CHAQUOPY_SHA="${CHAQUOPY_SHA:-eab341a401913ac50254ff20e9efeebeaae872ef}"

log() { printf '\n=== %s ===\n' "$*"; }

fetch_pinned() {
    local dir="$1" repo="$2" sha="$3"
    rm -rf "$dir"
    mkdir -p "$dir"
    git -C "$dir" init -q
    git -C "$dir" remote add origin "$repo"
    git -C "$dir" fetch -q --depth 1 origin "$sha"
    git -C "$dir" checkout -q FETCH_HEAD
}

log "Cherrygram $CHERRY_SHA"
fetch_pinned "$SRC" "$CHERRY_REPO" "$CHERRY_SHA"

log "Cherrygram submodules"
# Telegram keeps most of its native dependencies in submodules. If the shallow
# fetch is rejected by a mirror, retry with full history for those paths.
if ! git -C "$SRC" submodule update --init --recursive --depth 1 --jobs 4; then
    git -C "$SRC" submodule update --init --recursive --jobs 4
fi

log "exteraless plugin runtime $EL_SHA"
EL_DIR="$BUILD_ROOT/exteraless"
fetch_pinned "$EL_DIR" "$EL_REPO" "$EL_SHA"

log "Chaquopy fork $CHAQUOPY_SHA"
CHQ_DIR="$BUILD_ROOT/chaquopy-src"
fetch_pinned "$CHQ_DIR" "$CHAQUOPY_REPO" "$CHAQUOPY_SHA"

log "Copying plugin sources"
EL_MAIN="$EL_DIR/TMessagesProj/src/main"
DST_MAIN="$SRC/TMessagesProj/src/main"

mkdir -p "$DST_MAIN/java/app" "$DST_MAIN/java/com/exteragram/messenger"
rm -rf "$DST_MAIN/java/app/exteraless"
cp -R "$EL_MAIN/java/app/exteraless" "$DST_MAIN/java/app/exteraless"

rm -rf "$DST_MAIN/java/com/exteragram/messenger/plugins"
cp -R "$EL_MAIN/java/com/exteragram/messenger/plugins" \
      "$DST_MAIN/java/com/exteragram/messenger/plugins"

mkdir -p "$DST_MAIN/java/com/exteragram/messenger/preferences"
cp "$EL_MAIN/java/com/exteragram/messenger/preferences/BasePreferencesActivity.java" \
   "$DST_MAIN/java/com/exteragram/messenger/preferences/BasePreferencesActivity.java"

rm -rf "$DST_MAIN/python"
cp -R "$EL_MAIN/python" "$DST_MAIN/python"

# Optional subsystems that drag in the whole exteraless app: drawer/menu
# injection and the AI code review. The plugin core does not need them.
rm -rf "$DST_MAIN/java/app/exteraless/plugins/menus"
rm -f  "$DST_MAIN/java/app/exteraless/plugins/ui/components/PluginAiReview.java" \
       "$DST_MAIN/java/app/exteraless/plugins/ui/components/PluginReviewTools.java"

log "Applying overlay"
cp -R "$REPO_DIR/overlay/TMessagesProj/." "$SRC/TMessagesProj/"

log "Applying Chaquopy runtime sources"
rm -rf "$SRC/TMessagesProj/chaquopy"
mkdir -p "$SRC/TMessagesProj/chaquopy"
cp -R "$CHQ_DIR/exteraless" "$SRC/TMessagesProj/chaquopy/exteraless"
mkdir -p "$SRC/TMessagesProj/chaquopy/product"
cp -R "$CHQ_DIR/product/runtime" "$SRC/TMessagesProj/chaquopy/product/runtime"

log "Patching Cherrygram"
python3 "$REPO_DIR/scripts/patch_cherrygram.py" "$SRC"

log "Checking for forbidden names"
NEEDLE="$(printf 'Nar%szany' 'e')"
if grep -rIl --exclude-dir=.git -- "$NEEDLE" "$SRC" "$REPO_DIR/overlay" \
        "$REPO_DIR/scripts" "$REPO_DIR/.github" 2>/dev/null | head -n 1 | grep -q .; then
    echo "error: forbidden name found:" >&2
    grep -rIl --exclude-dir=.git -- "$NEEDLE" "$SRC" "$REPO_DIR/overlay" \
        "$REPO_DIR/scripts" "$REPO_DIR/.github" >&2
    exit 1
fi

chmod +x "$SRC/gradlew"

log "Source tree ready: $SRC"
