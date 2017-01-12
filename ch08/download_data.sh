#!/usr/bin/env bash

# Download to /tmp
curl -Lko /tmp/on_time_performance.parquet.tgz http://s3.amazonaws.com/agile_data_science/on_time_performance.parquet.tgz

# Get the absolute path of this script, see http://bit.ly/find_path
ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
ABSOLUTE_DIR=$(dirname "${ABSOLUTE_PATH}")

# Extract to Agile_Data_Code_2/data/on_time_performance.parquet, wherever we are executed from
tar -xvzf /tmp/on_time_performance.parquet.tgz -C $ABSOLUTE_DIR/../data/on_time_performance.parquet --strip-components=1

# Cleanup
rm -f /tmp/on_time_performance.parquet.tgz
