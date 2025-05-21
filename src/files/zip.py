import zipfile
import os


def create_zip_archive(directory: str, zip_path: str):
    """Create a zip file of the task directory."""

    try:
        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(str(directory)):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path != str(zip_path):
                        arcname = os.path.relpath(file_path, str(directory))
                        zipf.write(file_path, arcname)

        print(f"Created zip archive: {zip_path}")
    except Exception as e:
        print(f"Failed to create zip archive: {str(e)}")
