---
title: Testing
---
# Introduction

This document walks through the main design decisions and implementation details of the <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="93:2:2" line-data="class MarkItDown:">`MarkItDown`</SwmToken> document conversion system. The code is structured to support extensibility (plugins), robust file-type guessing, and flexible converter registration and prioritization. The walkthrough answers:

1. How are converters registered and prioritized?
2. How does the system handle <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="655:14:16" line-data="        before the PlainTextConverter, but after the built-in converters.">`built-in`</SwmToken> vs plugin converters?
3. How does the conversion process work for different input types (file, stream, URL, response)?
4. How does the system guess file types and handle ambiguous or unknown formats?
5. How are errors and unsupported formats handled?

# Converter registration and prioritization

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="53">

---

Converters are registered with a priority value, which determines the order in which they are tried. Lower values mean higher priority. This allows specific converters (like for .docx or .pdf) to be tried before generic ones (like plain text).

```
# Lower priority values are tried first.
PRIORITY_SPECIFIC_FILE_FORMAT = (
    0.0  # e.g., .docx, .pdf, .xlsx, Or specific pages, e.g., wikipedia
)
PRIORITY_GENERIC_FILE_FORMAT = (
    10.0  # Near catch-all converters for mimetypes like text/*, etc.
)
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="653">

---

The registration itself is handled by a method that inserts new converters at the front of the list, maintaining control over order and allowing plugins to interleave their converters as needed.

```
        Plugins can register converters with any priority, to appear before or
        after the built-ins. For example, a plugin with priority 9 will run
        before the PlainTextConverter, but after the built-in converters.
        """
        self._converters.insert(
            0, ConverterRegistration(converter=converter, priority=priority)
        )
```

---

</SwmSnippet>

# <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="135:1:3" line-data="        Built-in converters are enabled by default.">`Built-in`</SwmToken> vs plugin converters

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="169">

---

<SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="135:1:3" line-data="        Built-in converters are enabled by default.">`Built-in`</SwmToken> converters are enabled by default, but can be toggled. When enabled, a set of common converters is registered, including support for various document, spreadsheet, presentation, image, audio, and archive formats. If a Document Intelligence endpoint is provided, that converter is registered with the highest priority.

```
            # Register converters for successful browsing operations
            # Later registrations are tried first / take higher priority than earlier registrations
            # To this end, the most specific converters should appear below the most generic converters
            self.register_converter(
                PlainTextConverter(), priority=PRIORITY_GENERIC_FILE_FORMAT
            )
            self.register_converter(
                ZipConverter(markitdown=self), priority=PRIORITY_GENERIC_FILE_FORMAT
            )
            self.register_converter(
                HtmlConverter(), priority=PRIORITY_GENERIC_FILE_FORMAT
            )
            self.register_converter(RssConverter())
            self.register_converter(WikipediaConverter())
            self.register_converter(YouTubeConverter())
            self.register_converter(BingSerpConverter())
            self.register_converter(DocxConverter())
            self.register_converter(XlsxConverter())
            self.register_converter(XlsConverter())
            self.register_converter(PptxConverter())
            self.register_converter(AudioConverter())
            self.register_converter(ImageConverter())
            self.register_converter(IpynbConverter())
            self.register_converter(PdfConverter())
            self.register_converter(OutlookMsgConverter())
            self.register_converter(EpubConverter())
            self.register_converter(CsvConverter())
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="73">

---

Plugins are loaded lazily and can register their own converters. The plugin loading process is robust to failures: if a plugin fails to load or register, a warning is issued but the process continues.

```
    # Load plugins
    _plugins = []
    for entry_point in entry_points(group="markitdown.plugin"):
        try:
            _plugins.append(entry_point.load())
        except Exception:
            tb = traceback.format_exc()
            warn(f"Plugin '{entry_point.name}' failed to load ... skipping:\n{tb}")
```

---

</SwmSnippet>

# Conversion process for different input types

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="243">

---

The main entry point for conversion is the <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="243:3:3" line-data="    def convert(">`convert`</SwmToken> method. It dispatches based on the type of the source: string (path or URI), Path object, <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="245:9:11" line-data="        source: Union[str, requests.Response, Path, BinaryIO],">`requests.Response`</SwmToken>, or binary stream. Each type is handled by a dedicated method.

```
    def convert(
        self,
        source: Union[str, requests.Response, Path, BinaryIO],
        *,
        stream_info: Optional[StreamInfo] = None,
        **kwargs: Any,
    ) -> DocumentConverterResult:  # TODO: deal with kwargs
        """
        Args:
            - source: can be a path (str or Path), url, or a requests.response object
            - stream_info: optional stream info to use for the conversion. If None, infer from source
            - kwargs: additional arguments to pass to the converter
        """
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="305">

---

For local files, the system builds a base guess for the file type and opens the file as a binary stream for further analysis.

```
        # Build a base StreamInfo object from which to start guesses
        base_guess = StreamInfo(
            local_path=path,
            extension=os.path.splitext(path)[1],
            filename=os.path.basename(path),
        )
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="360">

---

For streams, it checks if the stream is seekable; if not, it loads the entire stream into memory to allow for multiple passes.

```
        # Check if we have a seekable stream. If not, load the entire stream into memory.
        if not stream.seekable():
            buffer = io.BytesIO()
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                buffer.write(chunk)
            buffer.seek(0)
            stream = buffer
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="396">

---

For <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="409:5:5" line-data="        # File URIs">`URIs`</SwmToken>, the system distinguishes between file, data, and HTTP(S) <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="409:5:5" line-data="        # File URIs">`URIs`</SwmToken>, handling each appropriately. Data <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="409:5:5" line-data="        # File URIs">`URIs`</SwmToken> are parsed and converted to streams; HTTP(S) <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="409:5:5" line-data="        # File URIs">`URIs`</SwmToken> are fetched using a requests session.

```
    def convert_uri(
        self,
        uri: str,
        *,
        stream_info: Optional[StreamInfo] = None,
        file_extension: Optional[str] = None,  # Deprecated -- use stream_info
        mock_url: Optional[
            str
        ] = None,  # Mock the request as if it came from a different URL
        **kwargs: Any,
    ) -> DocumentConverterResult:
        uri = uri.strip()
```

---

</SwmSnippet>

# File type guessing and ambiguity handling

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="686">

---

File type guessing is handled by combining information from file extensions, mimetypes, and content analysis using the magika library. The system tries to reconcile guesses from different sources and, if they are incompatible, tries both.

```
        # Call magika to guess from the stream
        cur_pos = file_stream.tell()
        try:
            result = self._magika.identify_stream(file_stream)
            if result.status == "ok" and result.prediction.output.label != "unknown":
                # If it's text, also guess the charset
                charset = None
                if result.prediction.output.is_text:
                    # Read the first 4k to guess the charset
                    file_stream.seek(cur_pos)
                    stream_page = file_stream.read(4096)
                    charset_result = charset_normalizer.from_bytes(stream_page).best()
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="728">

---

If magika's guess is compatible with the base guess, it is used directly; otherwise, both the enhanced base guess and magika's guess are added to the list of candidates for conversion.

```
                if compatible:
                    # Add the compatible base guess
                    guesses.append(
                        StreamInfo(
                            mimetype=base_guess.mimetype
                            or result.prediction.output.mime_type,
                            extension=base_guess.extension or guessed_extension,
                            charset=base_guess.charset or charset,
                            filename=base_guess.filename,
                            local_path=base_guess.local_path,
                            url=base_guess.url,
                        )
                    )
                else:
                    # The magika guess was incompatible with the base guess, so add both guesses
                    guesses.append(enhanced_guess)
                    guesses.append(
                        StreamInfo(
                            mimetype=result.prediction.output.mime_type,
                            extension=guessed_extension,
                            charset=charset,
                            filename=base_guess.filename,
                            local_path=base_guess.local_path,
                            url=base_guess.url,
                        )
                    )
```

---

</SwmSnippet>

# Error handling and unsupported formats

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="612">

---

If all converters fail, the system raises a <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="614:3:3" line-data="            raise FileConversionException(attempts=failed_attempts)">`FileConversionException`</SwmToken> with details of the failed attempts. If no converter even attempts conversion, an <SwmToken path="/packages/markitdown/src/markitdown/_exceptions.py" pos="34:2:2" line-data="class UnsupportedFormatException(MarkItDownException):">`UnsupportedFormatException`</SwmToken> is raised.

```
        # If we got this far without success, report any exceptions
        if len(failed_attempts) > 0:
            raise FileConversionException(attempts=failed_attempts)
```

---

</SwmSnippet>

<SwmSnippet path="/packages/markitdown/src/markitdown/_markitdown.py" line="591">

---

If a converter accepts the file but fails during conversion, the error is recorded and the next converter is tried. The file stream position is carefully managed to ensure each converter sees the file in its original state.

```
                # Attempt the conversion
                if _accepts:
                    try:
                        res = converter.convert(file_stream, stream_info, **_kwargs)
                    except Exception:
                        failed_attempts.append(
                            FailedConversionAttempt(
                                converter=converter, exc_info=sys.exc_info()
                            )
                        )
                    finally:
                        file_stream.seek(cur_pos)
```

---

</SwmSnippet>

# Summary

- Converter registration is priority-based and supports both <SwmToken path="/packages/markitdown/src/markitdown/_markitdown.py" pos="655:14:16" line-data="        before the PlainTextConverter, but after the built-in converters.">`built-in`</SwmToken> and plugin converters.
- Conversion dispatches based on input type, with robust guessing of file type using both metadata and content analysis.
- Errors are handled gracefully, with detailed reporting for failures and clear exceptions for unsupported formats.

<SwmMeta version="3.0.0" repo-id="Z2l0aHViJTNBJTNBbWFya2l0ZG93biUzQSUzQXVwcmF0aWstY3Q=" repo-name="markitdown"><sup>Powered by [Swimm](https://app.swimm.io/)</sup></SwmMeta>
