# Rescue Selection Notes

The 15 rescue candidates were selected from the previous 50-candidate behavioral sweep. Selection prioritized `could_not_construct`, `structural_only_no_runtime_difference`, and import failures whose dependencies exist in the rebuilt source snapshot. One prior state-only case, dnspython `Tokenizer`, was included because the user prompt explicitly identified it and a real token stream could test whether state-only evidence becomes output-visible.

Excluded cases include the unsafe docutils writer/string-output entries, nondeterministic dnspython `EntropyPool`, import failures requiring unavailable `html5lib` or `aioquic`, AnyIO runtime/context cases that require event-loop semantics, and Docutils parser state-machine directive classes whose realistic setup would require a larger parser framework fixture.

The selected cases favor in-memory fixtures: strings, iterables, `BytesIO`, BeautifulSoup trees, Click's in-process `CliRunner`, Docutils document utilities, and h11 receive buffers. No network, database, credential, browser, server, destructive filesystem, or subprocess-heavy setup is used by the harnesses.
