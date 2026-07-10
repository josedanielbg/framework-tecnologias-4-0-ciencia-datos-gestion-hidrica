import unittest

import pandas as pd

from proyecto_grado_v6.hydrology import monthly_hydrology, remove_hydrology_outliers
from proyecto_grado_v6.transforms import clean_numeric_text, seasonal_mean_impute
from proyecto_grado_v6.transforms import valid_year_month_mask


class TransformTests(unittest.TestCase):
    def test_valid_year_month_mask_discards_invalid_months(self):
        values = pd.Series([201501, 201512, 201513, "bad"])

        self.assertEqual(valid_year_month_mask(values).tolist(), [True, True, False, False])

    def test_clean_numeric_text_handles_symbols_and_decimal_comma(self):
        values = pd.Series(["<1,5", ">2.0", " 3 "])

        self.assertEqual(clean_numeric_text(values).tolist(), [1.5, 2.0, 3.0])

    def test_remove_hydrology_outliers_uses_max_threshold(self):
        df = pd.DataFrame({"valorobservado": [0.5, 1.2, 248.0]})

        result = remove_hydrology_outliers(df, max_value=5.0)

        self.assertEqual(result["valorobservado"].tolist(), [0.5, 1.2])

    def test_monthly_hydrology_averages_by_month(self):
        df = pd.DataFrame(
            {
                "fechaobservacion": ["2024-01-01", "2024-01-15", "2024-02-01"],
                "valorobservado": [1.0, 3.0, 5.0],
            }
        )

        result = monthly_hydrology(df)

        self.assertEqual(result["valorobservado"].round(2).tolist(), [2.0, 5.0])

    def test_seasonal_mean_impute_uses_same_calendar_month(self):
        df = pd.DataFrame(
            {
                "fecha": ["2024-01-01", "2025-01-01", "2024-02-01"],
                "valor": [10.0, None, 20.0],
            }
        )

        result = seasonal_mean_impute(df, "fecha", "valor")

        self.assertEqual(result.loc[1, "valor"], 10.0)


if __name__ == "__main__":
    unittest.main()
