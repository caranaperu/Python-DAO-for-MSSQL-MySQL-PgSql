def auto_unicode_decode( s ):
    """Takes a string and tries to convert it to a Unicode string.

    This will return a Python unicode string type corresponding to the
    input string (either str or unicode).  The character encoding is
    guessed by looking for either a Unicode BOM prefix, or by the
    rules specified by RFC 4627.  When in doubt it is assumed the
    input is encoded in UTF-8 (the default for JSON).

    """
    if isinstance(s, unicode):
        return s
    if len(s) < 4:
        return s.decode('utf8')  # not enough bytes, assume default of utf-8
    # Look for BOM marker
    import codecs
    bom2 = s[:2]
    bom4 = s[:4]
    a, b, c, d = map(ord, s[:4])  # values of first four bytes
    if bom4 == codecs.BOM_UTF32_LE:
        encoding = 'utf-32le'
        s = s[4:]
    elif bom4 == codecs.BOM_UTF32_BE:
        encoding = 'utf-32be'
        s = s[4:]
    elif bom2 == codecs.BOM_UTF16_LE:
        encoding = 'utf-16le'
        s = s[2:]
    elif bom2 == codecs.BOM_UTF16_BE:
        encoding = 'utf-16be'
        s = s[2:]
    # No BOM, so autodetect encoding used by looking at first four bytes
    # according to RFC 4627 section 3.
    elif a==0 and b==0 and c==0 and d!=0: # UTF-32BE
        encoding = 'utf-32be'
    elif a==0 and b!=0 and c==0 and d!=0: # UTF-16BE
        encoding = 'utf-16be'
    elif a!=0 and b==0 and c==0 and d==0: # UTF-32LE
        encoding = 'utf-32le'
    elif a!=0 and b==0 and c!=0 and d==0: # UTF-16LE
        encoding = 'utf-16le'
    else: #if a!=0 and b!=0 and c!=0 and d!=0: # UTF-8
        # JSON spec says default is UTF-8, so always guess it
        # if we can't guess otherwise
        encoding = 'utf8'
    # Make sure the encoding is supported by Python
    try:
        cdk = codecs.lookup(encoding)
    except LookupError:
        if encoding.startswith('utf-32') \
               or encoding.startswith('ucs4') \
               or encoding.startswith('ucs-4'):
            # Python doesn't natively have a UTF-32 codec, but JSON
            # requires that it be supported.  So we must decode these
            # manually.
            if encoding.endswith('le'):
                unis = utf32le_decode(s)
            else:
                unis = utf32be_decode(s)
        else:
            raise JSONDecodeError('this python has no codec for this character encoding',encoding)
    else:
        # Convert to unicode using a standard codec
        unis = s.decode(encoding)
    return unis


import sys
import chardet

IS_PY2 = sys.version_info < (3, 0)
if not IS_PY2:
    # Helper for Python 2 and 3 compatibility
    unicode = str

def make_compat_str(in_str):
    """
    Tries to guess encoding of [str/bytes] and decode it into
    an unicode object.
    """
    assert isinstance(in_str, (bytes, str, unicode))
    if not in_str:
        return unicode()

    # Chardet in Py2 works on str + bytes objects
    if IS_PY2 and isinstance(in_str, unicode):
        return in_str

    # Chardet in Py3 works on bytes objects
    if not IS_PY2 and not isinstance(in_str, bytes):
        return in_str

    # Detect the encoding now
    enc = chardet.detect(in_str)

    # Decode the object into a unicode object
    out_str = in_str.decode(enc['encoding'])

    # Cleanup: Sometimes UTF-16 strings include the BOM
    if enc['encoding'] == "UTF-16BE":
        # Remove byte order marks (BOM)
        if out_str.startswith('\ufeff'):
            out_str = out_str[1:]

    # Return the decoded string
    return out_str

if __name__ == "__main__":
    stre = u'\u6b70\u695fd'
    s2 = make_compat_str(stre)

    s = stre.encode('utf-16le').decode('utf-8')

    s = stre.encode('utf-16le')
    print(s)
    s2 =s.encode('utf-8')
    s2 = s2.rstrip('\x00')
    print(s2)


    s = stre.encode('utf-16le','strict')
    print(s)
