#!/bin/bash
# Train seeds 1 and 2 in sequence for each seed, two seeds in parallel.
# Usage: bash train_seeds.sh <seed>
# E.g.: bash train_seeds.sh 1 &   bash train_seeds.sh 2 &
set -e

SEED="$1"
if [[ -z "$SEED" ]]; then
    echo "Usage: $0 <seed>"
    exit 1
fi

NODR_DIR="/home/nur/build_nodr/src/rl/environments/l2f/dr_sac"
COMPLEX_DIR="/home/nur/build_complex/src/rl/environments/l2f/dr_sac"
LOG="/home/nur/train_seed${SEED}.log"

exec > >(tee -a "$LOG") 2>&1

echo "=============================="
echo "Seed $SEED training started: $(date)"
echo "=============================="

# ---- Step 1: NODR training ----
echo "[NODR] seed=$SEED starting..."
cd "$NODR_DIR"
"$NODR_DIR/rl_environments_l2f_dr_sac" "$SEED"
echo "[NODR] seed=$SEED done."

# Find the latest seed directory for this seed
NODR_SEED_DIR=$(find "$NODR_DIR/experiments" -type d -name "$(printf '%04d' $SEED)" | sort | tail -1)
echo "[NODR] Seed dir: $NODR_SEED_DIR"

ACTOR_PATH=$(find "$NODR_SEED_DIR/steps" -name "checkpoint.h5" | sort | tail -1)
CRITICS_PATH="$NODR_SEED_DIR/critics.h5"

if [[ ! -f "$ACTOR_PATH" ]]; then
    echo "ERROR: actor checkpoint not found at $ACTOR_PATH"
    exit 1
fi
if [[ ! -f "$CRITICS_PATH" ]]; then
    echo "ERROR: critics.h5 not found at $CRITICS_PATH"
    exit 1
fi

echo "[NODR] Actor: $ACTOR_PATH"
echo "[NODR] Critics: $CRITICS_PATH"

# ---- Step 2: From-scratch on target env ----
echo "[FROM-SCRATCH] seed=$SEED starting..."
cd "$COMPLEX_DIR"
"$COMPLEX_DIR/rl_environments_l2f_dr_sac" "$SEED"
echo "[FROM-SCRATCH] seed=$SEED done."

# ---- Step 3: Fine-tune on target env ----
echo "[FINE-TUNE] seed=$SEED starting..."
cd "$COMPLEX_DIR"
"$COMPLEX_DIR/rl_environments_l2f_finetune" "$SEED" "$ACTOR_PATH" "$CRITICS_PATH"
echo "[FINE-TUNE] seed=$SEED done."

echo "=============================="
echo "Seed $SEED ALL DONE: $(date)"
echo "=============================="
