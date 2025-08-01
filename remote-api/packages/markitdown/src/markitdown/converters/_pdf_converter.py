<<<<<<< SEARCH
import sys
import io

from typing import BinaryIO, Any


from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE
=======
"""
_pdf_converter.py

This module provides a PDF-to-Markdown converter for the markitdown package.
It uses pdfminer to extract text from PDF files and returns the result as Markdown.
Most style information is ignored, so the output is essentially plain text.

Classes:
    PdfConverter: Converts PDF files to Markdown.

Constants:
    ACCEPTED_MIME_TYPE_PREFIXES: List of MIME type prefixes recognized as PDF.
    ACCEPTED_FILE_EXTENSIONS: List of file extensions recognized as PDF.

Exceptions:
    MissingDependencyException: Raised if pdfminer is not installed.

Usage Example:
    converter = PdfConverter()
    if converter.accepts(file_stream, stream_info):
        result = converter.convert(file_stream, stream_info)
        print(result.markdown)
"""

import sys
import io

from typing import BinaryIO, Any


from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE
>>>>>>> REPLACE

<<<<<<< SEARCH
class PdfConverter(DocumentConverter):
    """
    Converts PDFs to Markdown. Most style information is ignored, so the results are essentially plain-text.
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        # Check the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".pdf",
                    feature="pdf",
                )
            ) from _dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _dependency_exc_info[2]
            )

        assert isinstance(file_stream, io.IOBase)  # for mypy
        return DocumentConverterResult(
            markdown=pdfminer.high_level.extract_text(file_stream),
        )

=======
class PdfConverter(DocumentConverter):
    """
    Converts PDF files to Markdown format.

    This converter uses pdfminer to extract text from PDF files. Most style information is ignored,
    so the results are essentially plain text.

    Methods:
        accepts(file_stream, stream_info, **kwargs): Determines if the converter can handle the given file.
        convert(file_stream, stream_info, **kwargs): Converts the PDF file to Markdown.

    Raises:
        MissingDependencyException: If pdfminer is not installed.
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """
        Determine if the converter can handle the given file based on its extension or MIME type.

        Args:
            file_stream (BinaryIO): The file stream to check.
            stream_info (StreamInfo): Metadata about the file stream.
            **kwargs: Additional options (unused).

        Returns:
            bool: True if the file is a PDF, False otherwise.
        """
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """
        Convert a PDF file stream to Markdown.

        Args:
            file_stream (BinaryIO): The PDF file stream to convert.
            stream_info (StreamInfo): Metadata about the file stream.
            **kwargs: Additional options to pass to the converter.

        Returns:
            DocumentConverterResult: The result containing the extracted Markdown text.

        Raises:
            MissingDependencyException: If pdfminer is not installed.
        """
        # Check the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".pdf",
                    feature="pdf",
                )
            ) from _dependency_exc_info[
                1
            ].with_traceback(  # type: ignore[union-attr]
                _dependency_exc_info[2]
            )

        assert isinstance(file_stream, io.IOBase)  # for mypy
        return DocumentConverterResult(
            markdown=pdfminer.high_level.extract_text(file_stream),
        )

>>>>>>> REPLACE
