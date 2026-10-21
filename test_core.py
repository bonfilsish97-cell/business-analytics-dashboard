import io
import unittest
import pandas as pd
from utils.data_loader import load_dataframe, quality_summary, DataLoadError
from utils.analysis import aggregate


class CoreTests(unittest.TestCase):
    def test_sample_csv_loads_and_dates_parse(self):
        with open("data/sample_business_data.csv", "rb") as f:
            df = load_dataframe(f.read(), "sample.csv")
        self.assertEqual(df.shape[1], 10)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["order_date"]))
        self.assertFalse(pd.api.types.is_datetime64_any_dtype(df["region"]))

    def test_quality_summary_counts(self):
        df = pd.DataFrame({"a": [1, 1, None], "b": ["x", "x", "y"]})
        q = quality_summary(df)
        self.assertEqual(q["missing_cells"], 1)
        self.assertEqual(q["duplicate_rows"], 1)  # rows 0 and 1 are identical

    def test_empty_dataframe_no_divide_by_zero(self):
        self.assertEqual(quality_summary(pd.DataFrame())["missing_pct"], 0.0)

    def test_bad_inputs_raise_friendly_errors(self):
        with self.assertRaises(DataLoadError): load_dataframe(b"", "a.csv")
        with self.assertRaises(DataLoadError): load_dataframe(b"x", "a.txt")
        with self.assertRaises(DataLoadError): load_dataframe(b"a,b\n", "a.csv")

    def test_excel_roundtrip(self):
        buf = io.BytesIO()
        pd.DataFrame({"a": [1, 2]}).to_excel(buf, index=False)
        self.assertEqual(load_dataframe(buf.getvalue(), "a.xlsx").shape, (2, 1))

    def test_aggregate_sum_and_invalid_selection(self):
        df = pd.DataFrame({"g": ["a", "a", "b"], "v": [1, 2, 3], "t": ["x", "y", "z"]})
        out = aggregate(df, "g", "v", "Sum")
        self.assertEqual(out.set_index("g")["v"].to_dict(), {"a": 3, "b": 3})
        with self.assertRaises(ValueError): aggregate(df, "g", "t", "Sum")  # text can't be summed


if __name__ == "__main__":
    unittest.main()
