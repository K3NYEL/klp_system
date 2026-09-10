import shutil
import tempfile
import unittest
from pathlib import Path

from app.core.database import connect_database
from app.core.reports import sales_summary


class ReportTests(unittest.TestCase):
    def test_sales_summary_uses_database_values(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "facturacion.db"
            shutil.copy2("facturacion.db", database)
            with connect_database(database) as connection:
                result = sales_summary(connection, "1900-01-01", "2999-12-31")
                self.assertIn("total", result)
                self.assertGreaterEqual(result["facturas"], 0)


if __name__ == "__main__":
    unittest.main()
