#!/usr/bin/env bash

# Download to /tmp
curl -Lko /tmp/simple_flight_delay_features.parquet.tgz http://s3.amazonaws.com/agile_data_science/simple_flight_delay_features.parquet.tgz

# Get the absolute path of this script, see http://bit.ly/find_path
ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
ABSOLUTE_DIR=$(dirname "${ABSOLUTE_PATH}")

# Extract to Agile_Data_Code_2/data/on_time_performance.parquet, wherever we are executed from
cd $ABSOLUTE_DIR/../data/
mkdir simple_flight_delay_features.parquet
tar -xvzf /tmp/simple_flight_delay_features.parquet.tgz -C simple_flight_delay_features.parquet --strip-components=1

# Cleanup
rm -f /tmp/simple_flight_delay_features.parquet.tgz
