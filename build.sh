#!/bin/bash

CURRENT_DIR=$(pwd)
KNOWN_BOARDS=("RPI_PICO" "RPI_PICO_W")

cd /home/damien/dev/micropython/ports/rp2 || exit 1


# Parse command line arguments for -b or --board
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -b|--board)
            BOARD="$2";
            shift
            ;;
        *)
            echo "Unknown parameter passed: $1"
            
            exit 1
            ;;
    esac
    shift
done

# shellcheck disable=SC2076
# shellcheck disable=SC2199
if [[ ! " ${KNOWN_BOARDS[@]} " =~ " ${BOARD} " ]]; then
    echo "Unknown board: ${BOARD}"
    echo "Can be one of: ${KNOWN_BOARDS[*]}"
    exit 1
fi

MANIFEST_FILE="$CURRENT_DIR/boards/${BOARD}/manifest.py"

echo "Building for board: ${BOARD}"
echo "Using manifest: ${MANIFEST_FILE}"

make FROZEN_MANIFEST="$MANIFEST_FILE" BOARD="$BOARD" submodules
make FROZEN_MANIFEST="$MANIFEST_FILE" BOARD="$BOARD" clean
make FROZEN_MANIFEST="$MANIFEST_FILE" BOARD="$BOARD"

cd "$CURRENT_DIR" || exit 1