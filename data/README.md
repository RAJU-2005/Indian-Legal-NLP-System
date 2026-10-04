# Legal Judgment Dataset Repository

This directory stores copies and metadata for the Indian Legal Judgment corpus used in Assessment 1.

## Structure

- `documents/`: Preserved copies of the 25 Indian Supreme Court and High Court judgment PDFs.
- `metadata/`: Contains `NLP_A1_CaseFiles_Datset_Info.xlsx` describing case names, court, year, sector, and key statutes.

## Primary Dataset Location

By default, the system looks for the primary dataset at:
- `C:\Users\Admin\Downloads\Dataset_NLP_A1`
- `C:\Users\Admin\Downloads\NLP_A1_CaseFiles_Datset_Info.xlsx`

If external paths are absent, the system seamlessly falls back to this local `data/` repository.
All original files in the source download directory remain intact and unmodified.
