# Step1: Install tectonic & Import deps
from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import subprocess
import shutil
import json

@tool
def render_latex_pdf(latex_content: str) -> str:
    """Render a LaTeX document to PDF.

    Args:
        latex_content: The LaTeX document content as a string

    Returns:
        JSON string containing output PDF/TEX paths and optional copied Downloads paths.
    """
    if shutil.which("tectonic") is None:
        raise RuntimeError(
            "tectonic is not installed. Install it first on your system."
        )

    try:
        # Step2: Create directory
        output_dir = Path("output").absolute()
        output_dir.mkdir(exist_ok=True)
        # Step3: Setup filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tex_filename = f"paper_{timestamp}.tex"
        pdf_filename = f"paper_{timestamp}.pdf"
        # Step4: Export as tex & pdf
        tex_file = output_dir / tex_filename
        tex_file.write_text(latex_content)

        result = subprocess.run(
                    ["tectonic", tex_filename, "--outdir", str(output_dir)],
                    cwd=output_dir,
                    capture_output=True,
                    text=True,
                )
        if result.returncode != 0:
            raise RuntimeError(f"tectonic failed: {result.stderr.strip() or result.stdout.strip()}")

        final_pdf = output_dir / pdf_filename
        if not final_pdf.exists():
            raise FileNotFoundError("PDF file was not generated")

        # Best effort: copy artifacts to the current OS user's Downloads folder.
        downloads_dir = Path.home() / "Downloads"
        copied_pdf = None
        copied_tex = None
        if downloads_dir.exists():
            copied_pdf_path = downloads_dir / pdf_filename
            copied_tex_path = downloads_dir / tex_filename
            shutil.copy2(final_pdf, copied_pdf_path)
            shutil.copy2(tex_file, copied_tex_path)
            copied_pdf = str(copied_pdf_path)
            copied_tex = str(copied_tex_path)

        payload = {
            "status": "ok",
            "pdf_path": str(final_pdf),
            "tex_path": str(tex_file),
            "pdf_filename": pdf_filename,
            "tex_filename": tex_filename,
            "downloads_pdf_path": copied_pdf,
            "downloads_tex_path": copied_tex,
        }
        print(f"Successfully generated PDF at {final_pdf}")
        return json.dumps(payload)

    except Exception as e:
        print(f"Error rendering LaTeX: {str(e)}")
        raise
