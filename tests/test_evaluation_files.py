from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_evaluation_labels_file_exists():
    eval_path = PROJECT_ROOT / "data" / "eval" / "evaluation_labels.csv"

    assert eval_path.exists()


def test_evaluation_labels_have_required_columns():
    eval_path = PROJECT_ROOT / "data" / "eval" / "evaluation_labels.csv"

    df = pd.read_csv(eval_path)

    required_columns = {
        "image_name",
        "expected_issue_keyword",
        "expected_severity",
        "expected_rule_id"
    }

    assert required_columns.issubset(set(df.columns))
    assert len(df) > 0


def test_evaluation_report_files_exist_after_phase_8():
    summary_path = PROJECT_ROOT / "reports" / "evaluation_summary.md"
    results_path = PROJECT_ROOT / "reports" / "evaluation_results.csv"

    assert summary_path.exists()
    assert results_path.exists()