import csv
import os
from pypdf import PdfReader, PdfWriter
import re

# --- 1. Configuration ---
# Set your file names and column name here
CSV_FILE = "students.csv"  # The name of your CSV file
PDF_FILE = "certificates_Cloud.pdf"  # The name of your main PDF file
OUTPUT_DIR = "output_certificates"  # Folder to save the new PDFs
NAME_COLUMN = "NAME"  # The exact name of the column in your CSV
# --------------------------


def sanitize_filename(name):
    """
    Removes characters that are invalid in Windows/Mac/Linux filenames.
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores (optional, but cleaner)
    sanitized = sanitized.replace(" ", "_")
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    return sanitized


def split_pdf_by_names():
    # --- 2. Create Output Directory ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory '{OUTPUT_DIR}' is ready.")

    # --- 3. Read Student Names from CSV ---
    student_names = []
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Check if the specified name column exists
            if NAME_COLUMN not in reader.fieldnames:
                print(
                    f"Error: CSV file '{CSV_FILE}' does not have a column named '{NAME_COLUMN}'."
                )
                print(f"Found columns: {', '.join(reader.fieldnames)}")
                return

            for row in reader:
                student_names.append(row[NAME_COLUMN])

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{CSV_FILE}'")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if not student_names:
        print("No student names found in the CSV file.")
        return

    print(f"Found {len(student_names)} student names in '{CSV_FILE}'.")

    # --- 4. Read and Split the PDF ---
    try:
        reader = PdfReader(PDF_FILE)
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{PDF_FILE}'")
        return
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    num_pages = len(reader.pages)
    print(f"Found {num_pages} pages in '{PDF_FILE}'.")

    # --- 5. Check for Mismatches ---
    num_to_process = min(len(student_names), num_pages)
    if len(student_names) != num_pages:
        print("\n--- WARNING ---")
        print(f"You have {len(student_names)} names but {num_pages} pages.")
        print(
            f"The script will only process {num_to_process} files based on the smaller number."
        )
        print("---------------\n")

    # --- 6. Create Individual PDFs ---
    print(f"Starting to create {num_to_process} individual PDF files...")
    for i in range(num_to_process):
        # Get the page and the corresponding name
        page = reader.pages[i]
        name = student_names[i]

        # Create a safe filename from the name
        safe_name = sanitize_filename(name)
        if not safe_name:  # Handle case where name is only invalid chars
            safe_name = f"certificate_{i+1}"

        output_filename = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

        # Create a new PDF writer, add the page, and save the file
        writer = PdfWriter()
        writer.add_page(page)

        try:
            with open(output_filename, "wb") as output_pdf:
                writer.write(output_pdf)
            print(f"Successfully created: {output_filename}")
        except Exception as e:
            print(f"Error writing file '{output_filename}': {e}")

    print("\n--- Process Complete ---")
    print(f"{num_to_process} PDF files have been created in the '{OUTPUT_DIR}' folder.")


# --- Run the script ---
if __name__ == "__main__":
    split_pdf_by_names()
