#!/usr/bin/env python3
"""
BE Testing - CLI Contract Validation Tests

Generated pytest script to validate the CLI spec against the running application.
Each command is tested as a parameterized test case using pytest.

This script supports two modes:
1. SRC Validation: Tests commands and captures outputs (no expected_stdout/stderr)
2. DST Contract Validation: Tests commands and validates outputs match expected

Generated at: 2026-03-03T09:30:41.375014+00:00
Project: simple-test-2
Milestone: 3
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Test Configuration (embedded from spec validation)
# =============================================================================

_ENV_PLACEHOLDER = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}')


def resolve_env_placeholders(obj: Any) -> Any:
    """Recursively resolve ${VAR_NAME} environment variable placeholders in test data.

    Only resolves braced ${VAR} syntax to avoid unintentional expansion of
    unrelated $VAR patterns (e.g. $HOME, $stored.KEY).
    """
    if isinstance(obj, str):
        return _ENV_PLACEHOLDER.sub(lambda m: os.environ.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, dict):
        return {k: resolve_env_placeholders(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_env_placeholders(item) for item in obj]
    return obj


# Parse JSON at runtime, then resolve any ${VAR_NAME} env var placeholders
# that the agent may have substituted for detected secrets.
TEST_CASES = resolve_env_placeholders(json.loads(r'''[
    {
        "name": "test_help_output",
        "category": "HELP_OUTPUT",
        "description": "Verify --help prints usage information and exits successfully",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--help"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Usage:",
        "expected_stderr": null,
        "timeout_seconds": 15
    },
    {
        "name": "test_analyzer_basic_csv_input",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with a valid CSV file using default output path",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.5\n2024-01-02T00:00:00,20.3\n2024-01-03T00:00:00,15.7\n2024-01-04T00:00:00,25.1\n2024-01-05T00:00:00,18.9\n2024-01-06T00:00:00,22.4\n2024-01-07T00:00:00,30.0\n2024-01-08T00:00:00,12.6\n2024-01-09T00:00:00,28.8\n2024-01-10T00:00:00,16.2"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_custom_output_path",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with a custom JSON output file path",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--output",
            "custom_report.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "custom_report.json",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.5\n2024-01-02T00:00:00,20.3\n2024-01-03T00:00:00,15.7\n2024-01-04T00:00:00,25.1\n2024-01-05T00:00:00,18.9"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "custom_report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_short_output_flag",
        "category": "HAPPY_PATH",
        "description": "Run analyzer using short -o flag for output path",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "-o",
            "short_report.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "short_report.json",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "short_report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_with_log_transform",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with log transformation applied to dataset values",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--transform",
            "log"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_with_sqrt_transform",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with sqrt transformation applied to dataset values",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--transform",
            "sqrt"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,4.0\n2024-01-02T00:00:00,9.0\n2024-01-03T00:00:00,16.0\n2024-01-04T00:00:00,25.0\n2024-01-05T00:00:00,36.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_with_square_transform",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with square transformation applied to dataset values",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--transform",
            "square"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,2.0\n2024-01-02T00:00:00,3.0\n2024-01-03T00:00:00,4.0\n2024-01-04T00:00:00,5.0\n2024-01-05T00:00:00,6.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_with_normalize_transform",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with normalize (z-score) transformation applied to dataset values",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--transform",
            "normalize"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_compare_two_datasets",
        "category": "HAPPY_PATH",
        "description": "Run analyzer comparing two CSV datasets with Pearson correlation and side-by-side stats",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "dataset1.csv",
            "--compare",
            "dataset2.csv",
            "--output",
            "comparison_report.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "comparison_report.json",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_files": [
                {
                    "path": "dataset1.csv",
                    "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0\n2024-01-06T00:00:00,60.0\n2024-01-07T00:00:00,70.0\n2024-01-08T00:00:00,80.0\n2024-01-09T00:00:00,90.0\n2024-01-10T00:00:00,100.0"
                },
                {
                    "path": "dataset2.csv",
                    "content": "timestamp,value\n2024-01-01T00:00:00,15.0\n2024-01-02T00:00:00,25.0\n2024-01-03T00:00:00,35.0\n2024-01-04T00:00:00,45.0\n2024-01-05T00:00:00,55.0\n2024-01-06T00:00:00,65.0\n2024-01-07T00:00:00,75.0\n2024-01-08T00:00:00,85.0\n2024-01-09T00:00:00,95.0\n2024-01-10T00:00:00,105.0"
                }
            ]
        },
        "cleanup": {
            "delete_files": [
                "dataset1.csv",
                "dataset2.csv",
                "comparison_report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_custom_value_column",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with a custom value column name specified via --value-column",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--value-column",
            "price"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "date,price,category\n2024-01-01,105.50,A\n2024-01-02,203.25,B\n2024-01-03,157.00,A\n2024-01-04,251.75,B\n2024-01-05,189.00,A"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_custom_timestamp_column",
        "category": "HAPPY_PATH",
        "description": "Run analyzer with explicit timestamp column name",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--value-column",
            "temperature",
            "--timestamp-column",
            "recorded_at"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "recorded_at,temperature,location\n2024-06-01T08:00:00,22.5,StationA\n2024-06-02T08:00:00,24.1,StationA\n2024-06-03T08:00:00,19.8,StationA\n2024-06-04T08:00:00,26.3,StationA\n2024-06-05T08:00:00,21.7,StationA"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_full_pipeline",
        "category": "HAPPY_PATH",
        "description": "Run full analysis pipeline: input CSV, transform, custom output, and compare",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "main_data.csv",
            "--compare",
            "compare_data.csv",
            "--transform",
            "normalize",
            "--output",
            "full_report.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "full_report.json",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_files": [
                {
                    "path": "main_data.csv",
                    "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,15.0\n2024-01-03T00:00:00,20.0\n2024-01-04T00:00:00,25.0\n2024-01-05T00:00:00,30.0\n2024-01-06T00:00:00,35.0\n2024-01-07T00:00:00,40.0\n2024-01-08T00:00:00,45.0\n2024-01-09T00:00:00,50.0\n2024-01-10T00:00:00,55.0"
                },
                {
                    "path": "compare_data.csv",
                    "content": "timestamp,value\n2024-01-01T00:00:00,12.0\n2024-01-02T00:00:00,18.0\n2024-01-03T00:00:00,22.0\n2024-01-04T00:00:00,28.0\n2024-01-05T00:00:00,32.0\n2024-01-06T00:00:00,38.0\n2024-01-07T00:00:00,42.0\n2024-01-08T00:00:00,48.0\n2024-01-09T00:00:00,52.0\n2024-01-10T00:00:00,58.0"
                }
            ]
        },
        "cleanup": {
            "delete_files": [
                "main_data.csv",
                "compare_data.csv",
                "full_report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_console_summary_output",
        "category": "HAPPY_PATH",
        "description": "Verify analyzer prints dataset summary statistics to console including count, mean, median, std dev, and outliers",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "Mean:",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_missing_input_flag",
        "category": "INVALID_ARGS",
        "description": "Running --analyzer without --input should fail with missing argument error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer"
        ],
        "expected_exit_code": 2,
        "expected_stdout": null,
        "expected_stderr": "input",
        "timeout_seconds": 15
    },
    {
        "name": "test_analyzer_input_flag_no_value",
        "category": "INVALID_ARGS",
        "description": "Running --analyzer --input without a file path value should fail",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input"
        ],
        "expected_exit_code": 2,
        "expected_stdout": null,
        "expected_stderr": "input",
        "timeout_seconds": 15
    },
    {
        "name": "test_analyzer_nonexistent_input_file",
        "category": "INVALID_ARGS",
        "description": "Running analyzer with a non-existent CSV file should fail with file not found error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "nonexistent_file.csv"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "not found",
        "timeout_seconds": 15
    },
    {
        "name": "test_analyzer_invalid_transform_type",
        "category": "INVALID_ARGS",
        "description": "Running analyzer with an unrecognized --transform value should fail",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--transform",
            "invalid_transform"
        ],
        "expected_exit_code": 2,
        "expected_stdout": null,
        "expected_stderr": "transform",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_compare_nonexistent_file",
        "category": "INVALID_ARGS",
        "description": "Running --compare with a non-existent second CSV should fail with file not found error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--compare",
            "missing_compare.csv"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "not found",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_output_flag_no_value",
        "category": "INVALID_ARGS",
        "description": "Running --output without a path value should fail",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--output"
        ],
        "expected_exit_code": 2,
        "expected_stdout": null,
        "expected_stderr": "output",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_unknown_option",
        "category": "INVALID_OPTIONS",
        "description": "Running analyzer with an unknown flag should fail with unrecognized option error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--unknown-option"
        ],
        "expected_exit_code": 2,
        "expected_stdout": null,
        "expected_stderr": "unknown",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv"
            ]
        }
    },
    {
        "name": "test_no_args_interactive_mode",
        "category": "INVALID_OPTIONS",
        "description": "Running with no arguments should enter interactive mode or print a menu (non-batch; tested only for non-crash behavior)",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar"
        ],
        "stdin": "3\n",
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 15
    },
    {
        "name": "test_analyzer_empty_csv_headers_only",
        "category": "BOUNDARY",
        "description": "CSV file with only headers and no data rows should be handled gracefully",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "empty_data.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "empty_data.csv",
                "content": "timestamp,value"
            }
        },
        "cleanup": {
            "delete_files": [
                "empty_data.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_single_datapoint",
        "category": "BOUNDARY",
        "description": "CSV with a single data row should compute basic statistics without crashing (std dev = 0)",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "single_row.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "single_row.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,42.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "single_row.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_large_numeric_values",
        "category": "BOUNDARY",
        "description": "CSV with very large numeric values should be handled without overflow",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "large_values.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "large_values.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,999999999.99\n2024-01-02T00:00:00,888888888.88\n2024-01-03T00:00:00,777777777.77\n2024-01-04T00:00:00,666666666.66\n2024-01-05T00:00:00,555555555.55"
            }
        },
        "cleanup": {
            "delete_files": [
                "large_values.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_negative_values",
        "category": "BOUNDARY",
        "description": "CSV with negative numeric values should be handled correctly",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "negative_values.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "negative_values.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,-50.0\n2024-01-02T00:00:00,-25.0\n2024-01-03T00:00:00,0.0\n2024-01-04T00:00:00,25.0\n2024-01-05T00:00:00,50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "negative_values.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_identical_values",
        "category": "BOUNDARY",
        "description": "CSV where all values are identical (std dev = 0, normalize should be skipped or handled)",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "identical_values.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "identical_values.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,42.0\n2024-01-02T00:00:00,42.0\n2024-01-03T00:00:00,42.0\n2024-01-04T00:00:00,42.0\n2024-01-05T00:00:00,42.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "identical_values.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_two_datapoints",
        "category": "BOUNDARY",
        "description": "CSV with exactly two data rows (minimum for std dev computation)",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "two_rows.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "two_rows.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "two_rows.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_with_timestamps",
        "category": "FILE_INPUT",
        "description": "CSV with ISO-8601 timestamps in a dedicated column should be parsed and used for time series analysis",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "timestamped.csv",
            "--timestamp-column",
            "ts"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "timestamped.csv",
                "content": "ts,value,label\n2024-01-01T08:00:00,10.5,morning\n2024-01-02T08:00:00,12.3,morning\n2024-01-03T08:00:00,11.7,morning\n2024-01-04T08:00:00,14.1,morning\n2024-01-05T08:00:00,13.9,morning\n2024-01-06T08:00:00,15.4,morning\n2024-01-07T08:00:00,16.0,morning\n2024-01-08T08:00:00,14.6,morning\n2024-01-09T08:00:00,17.8,morning\n2024-01-10T08:00:00,18.2,morning"
            }
        },
        "cleanup": {
            "delete_files": [
                "timestamped.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_without_timestamp_column",
        "category": "FILE_INPUT",
        "description": "CSV without any timestamp column should still work with auto-generated timestamps",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "no_timestamps.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "no_timestamps.csv",
                "content": "value\n10.0\n20.0\n30.0\n40.0\n50.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "no_timestamps.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_missing_value_column",
        "category": "FILE_INPUT",
        "description": "CSV that does not contain the expected value column should fail with a column not found error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "wrong_columns.csv"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "Column",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "wrong_columns.csv",
                "content": "name,score,grade\nAlice,95,A\nBob,87,B\nCharlie,92,A"
            }
        },
        "cleanup": {
            "delete_files": [
                "wrong_columns.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_with_invalid_numeric_data",
        "category": "FILE_INPUT",
        "description": "CSV rows containing non-numeric values in the value column should produce an error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "bad_numeric.csv"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": "Invalid data",
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "bad_numeric.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.5\n2024-01-02T00:00:00,not_a_number\n2024-01-03T00:00:00,15.7"
            }
        },
        "cleanup": {
            "delete_files": [
                "bad_numeric.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_with_malformed_timestamps",
        "category": "FILE_INPUT",
        "description": "CSV with malformed timestamp values should fall back to current time rather than crashing",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "bad_timestamps.csv",
            "--timestamp-column",
            "timestamp"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "bad_timestamps.csv",
                "content": "timestamp,value\nnot-a-date,10.5\n2024-01-02T00:00:00,20.3\nalso-not-valid,15.7\n2024-01-04T00:00:00,25.1\n12/31/2024,18.9"
            }
        },
        "cleanup": {
            "delete_files": [
                "bad_timestamps.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_csv_with_extra_columns",
        "category": "FILE_INPUT",
        "description": "CSV with extra columns beyond value and timestamp should be ignored without error",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "extra_cols.csv"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "extra_cols.csv",
                "content": "timestamp,value,label,category,notes\n2024-01-01T00:00:00,10.5,alpha,A,first\n2024-01-02T00:00:00,20.3,beta,B,second\n2024-01-03T00:00:00,15.7,gamma,A,third\n2024-01-04T00:00:00,25.1,delta,B,fourth\n2024-01-05T00:00:00,18.9,epsilon,A,fifth"
            }
        },
        "cleanup": {
            "delete_files": [
                "extra_cols.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_log_transform_with_negative_values",
        "category": "BOUNDARY",
        "description": "Log transform with negative/zero values should skip those values rather than crash",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "mixed_sign.csv",
            "--transform",
            "log"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "mixed_sign.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,-5.0\n2024-01-02T00:00:00,0.0\n2024-01-03T00:00:00,10.0\n2024-01-04T00:00:00,20.0\n2024-01-05T00:00:00,30.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "mixed_sign.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_sqrt_transform_with_negative_values",
        "category": "BOUNDARY",
        "description": "Sqrt transform with negative values should skip those values rather than crash",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "mixed_sign.csv",
            "--transform",
            "sqrt"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "analysis report exported",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "mixed_sign.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,-5.0\n2024-01-02T00:00:00,0.0\n2024-01-03T00:00:00,10.0\n2024-01-04T00:00:00,20.0\n2024-01-05T00:00:00,30.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "mixed_sign.csv",
                "analysis-report.json"
            ]
        }
    },
    {
        "name": "test_analyzer_empty_file",
        "category": "BOUNDARY",
        "description": "Completely empty file (no headers) should fail gracefully",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "empty_file.csv"
        ],
        "expected_exit_code": 1,
        "expected_stdout": null,
        "expected_stderr": null,
        "timeout_seconds": 15,
        "setup": {
            "create_file": {
                "path": "empty_file.csv",
                "content": ""
            }
        },
        "cleanup": {
            "delete_files": [
                "empty_file.csv"
            ]
        }
    },
    {
        "name": "test_analyzer_json_report_structure",
        "category": "HAPPY_PATH",
        "description": "Verify that the exported JSON report contains the expected top-level keys: timestamp, datasets, analysis_history",
        "command": "java",
        "subcommand": "",
        "args": [
            "-jar",
            "target/simple-test-2-1.0.0-SNAPSHOT.jar",
            "--analyzer",
            "--input",
            "test_input.csv",
            "--output",
            "structure_test.json"
        ],
        "expected_exit_code": 0,
        "expected_stdout": "structure_test.json",
        "expected_stderr": null,
        "timeout_seconds": 30,
        "setup": {
            "create_file": {
                "path": "test_input.csv",
                "content": "timestamp,value\n2024-01-01T00:00:00,10.0\n2024-01-02T00:00:00,20.0\n2024-01-03T00:00:00,30.0\n2024-01-04T00:00:00,40.0\n2024-01-05T00:00:00,50.0\n2024-01-06T00:00:00,60.0\n2024-01-07T00:00:00,70.0\n2024-01-08T00:00:00,80.0\n2024-01-09T00:00:00,90.0\n2024-01-10T00:00:00,100.0"
            }
        },
        "cleanup": {
            "delete_files": [
                "test_input.csv",
                "structure_test.json"
            ]
        }
    }
]'''))

# CLI binary/entry point
CLI_COMMAND = "echo success"

# Working directory for CLI execution
WORKING_DIR = "."

# Default command timeout in seconds
DEFAULT_TIMEOUT = 30

# Response validation mode: when True, validates output against expected
VALIDATE_OUTPUT = any(
    tc.get("actual_stdout") is not None or tc.get("actual_stderr") is not None
    for tc in TEST_CASES
)

# =============================================================================
# Output Validation Utilities
# =============================================================================



def normalize_output(output: str) -> str:
    """Normalize output for comparison (strip whitespace, normalize newlines)."""
    if output is None:
        return ""
    return output.strip().replace("\r\n", "\n")


def matches_pattern(actual: str, pattern: str | None) -> bool:
    """
    Check if actual output matches the expected pattern.

    Pattern matching rules:
    - If pattern is None, always matches (no validation)
    - If pattern starts with 'regex:', use regex matching
    - Otherwise, check if pattern is contained in actual output (case-insensitive)
    """
    if pattern is None:
        return True

    actual_normalized = normalize_output(actual)

    if pattern.startswith("regex:"):
        regex_pattern = pattern[6:]  # Remove 'regex:' prefix
        return bool(re.search(regex_pattern, actual_normalized, re.IGNORECASE | re.MULTILINE))

    # Default: substring match (case-insensitive)
    pattern_normalized = normalize_output(pattern)
    return pattern_normalized.lower() in actual_normalized.lower()


def validate_cli_output(
    actual_stdout: str,
    actual_stderr: str,
    expected_stdout: str | None,
    expected_stderr: str | None,
) -> tuple[bool, list[str]]:
    """
    Validate CLI output against expected patterns.

    Args:
        actual_stdout: Actual stdout from command
        actual_stderr: Actual stderr from command
        expected_stdout: Expected stdout pattern (or None)
        expected_stderr: Expected stderr pattern (or None)

    Returns:
        tuple: (is_valid, list of violations)
    """
    violations: list[str] = []

    if expected_stdout is not None and not matches_pattern(actual_stdout, expected_stdout):
        violations.append(
            f"stdout mismatch: expected pattern '{expected_stdout}' not found in output"
        )

    if expected_stderr is not None and not matches_pattern(actual_stderr, expected_stderr):
        violations.append(
            f"stderr mismatch: expected pattern '{expected_stderr}' not found in output"
        )

    return len(violations) == 0, violations


def format_output_diff(violations: list[str]) -> str:
    """Format output differences for error message."""
    if not violations:
        return "No differences"

    output = []
    for i, diff in enumerate(violations):
        output.append(f"  - {diff}")

    return "\n".join(output)


# =============================================================================
# Output Store (cross-test-case value sharing)
# =============================================================================

# In-memory store for values extracted from command outputs and shared across test cases.
# Test cases with a "store" field extract values from their stdout/stderr and save them here.
# Later test cases reference stored values via "$stored.KEY" placeholders.
_output_store: dict[str, Any] = {}


def extract_by_json_path(data: Any, json_path: str) -> Any:
    """Extract a value from nested data using a dot-separated JSON path.

    Supports dict key access and integer list indexing.
    E.g. "data.users.0.id" -> data["data"]["users"][0]["id"]
    """
    current = data
    for key in json_path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current


def store_output_values(test_case: dict[str, Any], stdout: str, stderr: str) -> None:
    """Extract values from command output and save them in the output store.

    The test case's "store" field maps placeholder names to extraction rules:
    - "stdout.json.<json_path>": Parse stdout as JSON and extract by path
    - "stderr.json.<json_path>": Parse stderr as JSON and extract by path
    - "stdout.regex.<pattern>": Match regex against stdout, store first capture group
    - "stderr.regex.<pattern>": Match regex against stderr, store first capture group
    - "stdout": Store the full stdout string (stripped)
    - "stderr": Store the full stderr string (stripped)
    """
    store_config = test_case.get("store")
    if not store_config or not isinstance(store_config, dict):
        return

    for placeholder_name, extraction_rule in store_config.items():
        if not isinstance(extraction_rule, str):
            continue

        value: Any = None

        if extraction_rule == "stdout":
            value = stdout.strip()
        elif extraction_rule == "stderr":
            value = stderr.strip()
        elif extraction_rule.startswith("stdout.json."):
            json_path = extraction_rule[len("stdout.json."):]
            try:
                parsed = json.loads(stdout)
                value = extract_by_json_path(parsed, json_path)
            except (json.JSONDecodeError, TypeError):
                print(f"  Warning: stdout is not valid JSON for store rule '{extraction_rule}'")
        elif extraction_rule.startswith("stderr.json."):
            json_path = extraction_rule[len("stderr.json."):]
            try:
                parsed = json.loads(stderr)
                value = extract_by_json_path(parsed, json_path)
            except (json.JSONDecodeError, TypeError):
                print(f"  Warning: stderr is not valid JSON for store rule '{extraction_rule}'")
        elif extraction_rule.startswith("stdout.regex."):
            pattern = extraction_rule[len("stdout.regex."):]
            match = re.search(pattern, stdout)
            if match:
                value = match.group(1) if match.lastindex else match.group(0)
        elif extraction_rule.startswith("stderr.regex."):
            pattern = extraction_rule[len("stderr.regex."):]
            match = re.search(pattern, stderr)
            if match:
                value = match.group(1) if match.lastindex else match.group(0)

        if value is not None:
            _output_store[placeholder_name] = value
            print(f"  Stored: ${placeholder_name} = <{len(str(value))} chars>")
        else:
            print(f"  Warning: store rule '{extraction_rule}' resolved to None for '{placeholder_name}'")


def resolve_stored_placeholders(obj: Any) -> Any:
    """Replace $stored.KEY placeholders with values from the output store.

    Handles three cases:
    1. Exact match: value is "$stored.key" -> replaced with stored value (preserves type)
    2. Embedded match: value is "Bearer $stored.token" -> string interpolation
    3. Recursive: dicts and lists are traversed recursively
    """
    if not _output_store:
        return obj

    if isinstance(obj, str):
        # Exact match - preserves original type (e.g. int, dict) instead of stringifying
        if obj.startswith("$stored."):
            key = obj[len("$stored."):]
            if key in _output_store:
                return _output_store[key]
        # Embedded string interpolation (handles "Bearer $stored.token" and partial matches)
        if "$stored." in obj:
            result = obj
            for key, value in _output_store.items():
                result = result.replace(f"$stored.{key}", str(value))
            return result
        return obj

    if isinstance(obj, dict):
        return {k: resolve_stored_placeholders(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [resolve_stored_placeholders(item) for item in obj]

    return obj


# =============================================================================
# Test Results Collection
# =============================================================================

test_results: list[dict[str, Any]] = []


def record_result(
    name: str,
    command: str,
    subcommand: str | None,
    args: list[str],
    expected_exit_code: int,
    actual_exit_code: int,
    passed: bool,
    duration_ms: float,
    category: str | None = None,
    description: str | None = None,
    error: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    output_match: bool | None = None,
    output_diff: list[str] | None = None,
) -> None:
    """Record a test result for final output."""
    result: dict[str, Any] = {
        "name": name,
        "command": command,
        "subcommand": subcommand,
        "args": args,
        "expected_exit_code": expected_exit_code,
        "actual_exit_code": actual_exit_code,
        "passed": passed,
        "duration_ms": duration_ms,
        "category": category,
        "description": description,
    }
    if error:
        result["error"] = error

    # Track output validation results (for DST contract testing)
    if output_match is not None:
        result["output_match"] = output_match
    if output_diff:
        result["output_diff"] = output_diff

    # Capture outputs for validation
    if stdout:
        if passed:
            result["actual_stdout"] = stdout  # Capture more for passed tests
        else:
            result["stdout"] = stdout

    if stderr:
        if passed:
            result["actual_stderr"] = stderr
        else:
            result["stderr"] = stderr

    test_results.append(result)


# =============================================================================
# Setup and Cleanup Helpers
# =============================================================================


def run_setup(setup_config: dict[str, Any], work_dir: Path) -> bool:
    """Run setup actions before a test."""
    if not setup_config:
        return True

    try:
        # Create file
        if "create_file" in setup_config:
            file_config = setup_config["create_file"]
            file_path = work_dir / file_config["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_config.get("content", ""))
            print(f"Setup: Created file {file_path}")

        # Create directory
        if "create_dir" in setup_config:
            dir_path = work_dir / setup_config["create_dir"]
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Setup: Created directory {dir_path}")

        # Run command
        if "run_command" in setup_config:
            cmd = setup_config["run_command"]
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode != 0:
                print(f"Setup command failed: {result.stderr}")
                return False

        return True

    except Exception as e:
        print(f"Setup error: {e}")
        return False


def run_cleanup(cleanup_config: dict[str, Any], work_dir: Path) -> None:
    """Run cleanup actions after a test (best effort)."""
    if not cleanup_config:
        return

    try:
        # Delete files
        if "delete_files" in cleanup_config:
            for file_path in cleanup_config["delete_files"]:
                full_path = work_dir / file_path
                if full_path.exists():
                    full_path.unlink()
                    print(f"Cleanup: Deleted file {full_path}")

        # Delete directories
        if "delete_dirs" in cleanup_config:
            for dir_path in cleanup_config["delete_dirs"]:
                full_path = work_dir / dir_path
                if full_path.exists():
                    shutil.rmtree(full_path)
                    print(f"Cleanup: Deleted directory {full_path}")

        # Run command
        if "run_command" in cleanup_config:
            cmd = cleanup_config["run_command"]
            subprocess.run(
                cmd,
                shell=True,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )

    except Exception as e:
        print(f"Cleanup warning: {e}")


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def cli_work_dir() -> Path:
    """Get the CLI working directory."""
    return Path(WORKING_DIR)


@pytest.fixture(scope="session", autouse=True)
def verify_cli_exists() -> None:
    """Verify the CLI command exists before running tests."""
    print(f"\nVerifying CLI command exists: {CLI_COMMAND}...")

    # Check if it's a direct path
    if os.path.isfile(CLI_COMMAND):
        print(f"CLI found at: {CLI_COMMAND}")
        return

    # Check if it's in PATH
    result = shutil.which(CLI_COMMAND)
    if result:
        print(f"CLI found in PATH: {result}")
        return

    # Try common locations
    work_dir = Path(WORKING_DIR)
    common_paths = [
        work_dir / CLI_COMMAND,
        work_dir / "dist" / CLI_COMMAND,
        work_dir / "target" / "release" / CLI_COMMAND,
        work_dir / "bin" / CLI_COMMAND,
    ]

    for path in common_paths:
        if path.exists():
            print(f"CLI found at: {path}")
            return

    pytest.fail(f"CLI command '{CLI_COMMAND}' not found. Please ensure the app is built.")


# =============================================================================
# Test Cases
# =============================================================================


def get_test_ids() -> list[str]:
    """Generate test IDs for parametrization."""
    return [tc.get("name", f"test_{i}") for i, tc in enumerate(TEST_CASES)]


@pytest.mark.parametrize("test_case", TEST_CASES, ids=get_test_ids())
def test_cli_command(test_case: dict[str, Any], cli_work_dir: Path) -> None:
    """Test a single CLI command based on test case configuration."""
    # Extract test case info
    name = test_case.get("name", "unnamed")
    command = CLI_COMMAND
    raw_args = test_case.get("args", [])
    args = (
        [str(arg) for arg in raw_args]
        if isinstance(raw_args, list)
        else ([str(raw_args)] if raw_args is not None else [])
    )
    subcommand = test_case.get("subcommand", "")
    subcommand_parts = (
        [part for part in subcommand.strip().split(" ") if part]
        if isinstance(subcommand, str) and subcommand.strip()
        else []
    )
    execution_args = subcommand_parts + args
    stdin_input = test_case.get("stdin")
    env_vars = test_case.get("env", {})
    expected_exit_code = test_case.get("expected_exit_code", 0)
    expected_stdout = test_case.get("expected_stdout")
    expected_stderr = test_case.get("expected_stderr")
    category = test_case.get("category")
    description = test_case.get("description")
    setup_config = test_case.get("setup")
    cleanup_config = test_case.get("cleanup")
    timeout = test_case.get("timeout_seconds", DEFAULT_TIMEOUT)

    # Expected outputs for DST contract validation (from SRC validation)
    actual_stdout_expected = test_case.get("actual_stdout")
    actual_stderr_expected = test_case.get("actual_stderr")

    try:
        # Run setup if configured
        if setup_config:
            if not run_setup(setup_config, cli_work_dir):
                record_result(
                    name=name,
                    command=command,
                    subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                    args=execution_args,
                    expected_exit_code=expected_exit_code,
                    actual_exit_code=-1,
                    passed=False,
                    duration_ms=0,
                    category=category,
                    description=description,
                    error="Setup failed",
                )
                pytest.fail(f"Setup failed for test '{name}'")

        # Resolve $stored.* placeholders from previous test outputs
        args = resolve_stored_placeholders(args)
        env_vars = resolve_stored_placeholders(env_vars)
        if stdin_input is not None:
            stdin_input = resolve_stored_placeholders(stdin_input)

        # Build full command
        full_cmd = [command] + execution_args

        # Prepare environment
        env = os.environ.copy()
        env.update(env_vars)

        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                full_cmd,
                input=stdin_input,
                cwd=str(cli_work_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            actual_exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr

            # Check exit code first
            exit_code_passed = actual_exit_code == expected_exit_code
            error_msg = None if exit_code_passed else (
                f"Expected exit code {expected_exit_code}, got {actual_exit_code}"
            )

            # Store output values for cross-test-case sharing (before any assertions)
            if exit_code_passed:
                store_output_values(test_case, stdout, stderr)

            # Check output patterns
            output_match: bool | None = None
            output_diff: list[str] | None = None

            # For DST validation, compare against captured SRC output
            if actual_stdout_expected is not None or actual_stderr_expected is not None:
                output_match, output_diff = validate_cli_output(
                    stdout,
                    stderr,
                    actual_stdout_expected,
                    actual_stderr_expected,
                )
                if not output_match:
                    error_msg = f"Output contract violation:\n{format_output_diff(output_diff)}"
            # For SRC validation or basic validation, check expected patterns
            elif expected_stdout is not None or expected_stderr is not None:
                output_match, output_diff = validate_cli_output(
                    stdout,
                    stderr,
                    expected_stdout,
                    expected_stderr,
                )
                if not output_match:
                    error_msg = f"Output pattern mismatch:\n{format_output_diff(output_diff)}"

            # Overall pass
            passed = exit_code_passed and (output_match is None or output_match)

            record_result(
                name=name,
                command=command,
                subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                args=execution_args,
                expected_exit_code=expected_exit_code,
                actual_exit_code=actual_exit_code,
                passed=passed,
                duration_ms=duration_ms,
                category=category,
                description=description,
                error=error_msg,
                stdout=stdout,
                stderr=stderr,
                output_match=output_match,
                output_diff=output_diff,
            )

            # pytest assertions
            if not exit_code_passed:
                pytest.fail(
                    f"Test '{name}': Expected exit code {expected_exit_code}, got {actual_exit_code}.\n"
                    f"stdout: {stdout if stdout else 'empty'}\n"
                    f"stderr: {stderr if stderr else 'empty'}"
                )

            if output_match is False:
                pytest.fail(
                    f"Test '{name}': Output validation failed.\n"
                    f"Violations:\n{format_output_diff(output_diff or [])}"
                )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000
            record_result(
                name=name,
                command=command,
                subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
                args=execution_args,
                expected_exit_code=expected_exit_code,
                actual_exit_code=-1,
                passed=False,
                duration_ms=duration_ms,
                category=category,
                description=description,
                error=f"Command timed out after {timeout}s",
                stdout=e.stdout if hasattr(e, 'stdout') else None,
                stderr=e.stderr if hasattr(e, 'stderr') else None,
            )
            pytest.fail(f"Test '{name}': Command timed out after {timeout}s")

    except Exception as e:
        record_result(
            name=name,
            command=command,
            subcommand=subcommand if isinstance(subcommand, str) and subcommand.strip() else None,
            args=execution_args,
            expected_exit_code=expected_exit_code,
            actual_exit_code=-1,
            passed=False,
            duration_ms=0,
            category=category,
            description=description,
            error=f"Test error: {type(e).__name__}: {e}",
        )
        raise

    finally:
        # Always run cleanup
        if cleanup_config:
            run_cleanup(cleanup_config, cli_work_dir)


# =============================================================================
# Test Results Output
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def output_test_results(request: pytest.FixtureRequest) -> Any:
    """Output test results in JSON format after all tests complete."""
    yield  # Wait for all tests to complete

    # Calculate final results
    passed_count = sum(1 for r in test_results if r["passed"])
    failed_count = len([r for r in test_results if not r["passed"]])
    total_count = len(test_results)
    all_passed = failed_count == 0 and total_count > 0

    failures = [r for r in test_results if not r["passed"]]

    # Count output validation results (for DST contract testing)
    output_validated_count = sum(1 for r in test_results if r.get("output_match") is not None)
    output_match_count = sum(1 for r in test_results if r.get("output_match") is True)

    output = {
        "all_passed": all_passed,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "results": test_results,
        "failures": failures,
    }

    # Add contract validation summary if any tests had expected outputs
    if output_validated_count > 0:
        output["contract_validation"] = {
            "tests_with_expected_output": output_validated_count,
            "output_matches": output_match_count,
            "output_mismatches": output_validated_count - output_match_count,
        }

    print("\n" + "=" * 60)
    print(f"Results: {passed_count}/{total_count} passed")
    if output_validated_count > 0:
        print(f"Contract validation: {output_match_count}/{output_validated_count} outputs matched")
    print("=" * 60)
    print(json.dumps(output))
    sys.stdout.flush()
