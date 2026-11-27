from app.services.document_metadata import extract_document_metadata


def main():
    metadata = extract_document_metadata(
        "test_docs/eor_test_document.pdf"
    )

    print(metadata.model_dump())


if __name__ == "__main__":
    main()