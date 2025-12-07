# Setup Instructions

## Environment Setup

### 1. Create and Activate Conda Environment

```bash
conda create -n ai_engineer python=3.10
conda activate ai_engineer
```

### 2. Install System Dependencies

Required system dependencies for PDF processing:
- **Poppler**: Converts PDF pages to images
- **Tesseract**: OCR engine for text extraction

```bash
conda install -c conda-forge poppler tesseract
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Troubleshooting

### Verify System Dependencies

Check if the tools are installed correctly:

```bash
# Check Poppler
pdfinfo -v

# Check Tesseract
tesseract --version
```

### If Poppler is Not Found

If you still get `PDFInfoNotInstalledError`:

**Option A: Manual Poppler Installation (Windows)**
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract to `C:\poppler`
3. Add `C:\poppler\Library\bin` to your system PATH

**Option B: Specify Poppler Path in Code**
```python
chunks = partition_pdf(
    filename=file_path,
    strategy="hi_res",
    poppler_path=r"C:\path\to\poppler\Library\bin"
)
```

### If Tesseract is Not Found

If you get `TesseractNotFoundError`:

**Option A: Manual Tesseract Installation (Windows)**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or set in code:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Verify Installation

Run this in Python to verify everything is working:

```python
from unstructured.partition.pdf import partition_pdf
print("✓ Unstructured library ready")

# Test poppler
import pdf2image
print("✓ pdf2image ready")

# Test tesseract
import pytesseract
try:
    pytesseract.get_tesseract_version()
    print("✓ Tesseract OCR ready")
except:
    print("✗ Tesseract not found")
```
