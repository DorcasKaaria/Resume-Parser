from pathlib import Path

# =========================
# CONFIGURATION
# =========================

FOLDER = Path(r"/Desktop/Resume Parser Project/resume_samples")  # Change this
DRY_RUN = True  # True = preview only, False = actually delete


# =========================
# FIND AND REMOVE DUPLICATES
# =========================

def remove_duplicate_documents(folder):
    files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in {".pdf", ".docx"}
    ]

    # Group files by document name, ignoring extension
    grouped = {}

    for file in files:
        document_name = file.stem.lower().strip()
        grouped.setdefault(document_name, []).append(file)

    deleted = []
    kept = []

    for document_name, documents in grouped.items():

        # If both PDF and DOCX exist, keep PDF and remove DOCX
        pdf_files = [f for f in documents if f.suffix.lower() == ".pdf"]
        docx_files = [f for f in documents if f.suffix.lower() == ".docx"]

        if pdf_files and docx_files:
            # Keep the first PDF
            keep_file = pdf_files[0]
            kept.append(keep_file)

            # Remove all DOCX versions
            for docx in docx_files:
                if DRY_RUN:
                    print(f"[DRY RUN] Would delete: {docx.name}")
                else:
                    docx.unlink()
                    print(f"Deleted: {docx.name}")

                deleted.append(docx)

        # If there are multiple PDFs with the same name,
        # keep the first one and remove the others
        elif len(pdf_files) > 1:
            keep_file = pdf_files[0]
            kept.append(keep_file)

            for duplicate in pdf_files[1:]:
                if DRY_RUN:
                    print(f"[DRY RUN] Would delete duplicate PDF: {duplicate.name}")
                else:
                    duplicate.unlink()
                    print(f"Deleted duplicate PDF: {duplicate.name}")

                deleted.append(duplicate)

        # If there are multiple DOCX files with the same name,
        # keep the first one and remove the others
        elif len(docx_files) > 1:
            keep_file = docx_files[0]
            kept.append(keep_file)

            for duplicate in docx_files[1:]:
                if DRY_RUN:
                    print(f"[DRY RUN] Would delete duplicate DOCX: {duplicate.name}")
                else:
                    duplicate.unlink()
                    print(f"Deleted duplicate DOCX: {duplicate.name}")

                deleted.append(duplicate)

        else:
            # No duplicate
            kept.extend(documents)

    print("\n" + "=" * 50)
    print(f"Files kept: {len(kept)}")
    print(f"Files removed: {len(deleted)}")

    if DRY_RUN:
        print("\nDRY RUN enabled. No files were actually deleted.")
        print("Set DRY_RUN = False to delete the duplicates.")


# =========================
# RUN
# =========================

remove_duplicate_documents(FOLDER)
