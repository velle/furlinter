# Observations on Furman style  

Snippets copied from dbf repo.

### Several items per line, starting after opening bracket line

From tables.py:3847

```
bkup = Table(
        new_name, self.structure(), memo_size,
        codepage=self.codepage.name,
        dbf_type=self._versionabbr,
        on_disk=on_disk,
        overwrite=overwrite,
        )
```

### Several items per line, starting on openeing bracket line

From tables.py:3847

```
def from_csv(csvfile, to_disk=False, filename=None, field_names=None, extra_fields=None,
        dbf_type='db3', memo_size=64, min_field_size=1,
        encoding=None, errors=None, overwrite=False):
            pass
```

### Uneven indentation

From tables.py:4564

```
raise BadDataError(
        "field definition block corrupt: %d bytes in size"
            % len(fieldsdef))
```

From data_types.py:1846

```
Marshaller.dispatch[DateTime] = lambda s, dt, w: w(
        '<value><dateTime.iso8601>'
        '%04d%02d%02dT%02d:%02d:%02d'
        '</dateTime.iso8601></value>\n'
            % dt.utctimetuple()[:6])
```

### Two opening brackets compacted on same line, but content across several lines

From bridge.py:47

```
exec(dedent("""\
    def execute(code, gbl=None, lcl=None):
        if lcl is not None:
            exec code in gbl, lcl
        elif gbl is not None:
            exec code in gbl
        else:
            exec code in globals()
        """))
```

### First indentation level is 4 spaces, second is 8 spaces

From tables.py:4228

```
return {
    CHAR: {
            'Type':'Character', 'Retrieve':retrieve_character, 'Update':update_character, 'Blank':lambda x: b' ' * x, 'Init':add_character,
            'Class':unicode, 'Empty':unicode, 'flags':tuple(),
            },
    DATE: {
            'Type':'Date', 'Retrieve':retrieve_date, 'Update':update_date, 'Blank':lambda x: b'        ', 'Init':add_date,
            'Class':datetime.date, 'Empty':none, 'flags':tuple(),
            },
    NUMERIC: {
            'Type':'Numeric', 'Retrieve':retrieve_numeric, 'Update':update_numeric, 'Blank':lambda x: b' ' * x, 'Init':add_numeric,
            'Class':'default', 'Empty':none, 'flags':tuple(),
            },
    LOGICAL: {
            'Type':'Logical', 'Retrieve':retrieve_logical, 'Update':update_logical, 'Blank':lambda x: b'?', 'Init':add_logical,
            'Class':bool, 'Empty':none, 'flags':tuple(),
            },
    MEMO: {
            'Type':'Memo', 'Retrieve':retrieve_memo, 'Update':update_memo, 'Blank':lambda x: b'          ', 'Init':add_memo,
            'Class':unicode, 'Empty':unicode, 'flags':tuple(),
            },
    FLOAT: {
            'Type':'Numeric', 'Retrieve':retrieve_numeric, 'Update':update_numeric, 'Blank':lambda x: b' ' * x, 'Init':add_numeric,
            'Class':'default', 'Empty':none, 'flags':tuple(),
            },
    TIMESTAMP: {
            'Type':'TimeStamp', 'Retrieve':retrieve_clp_timestamp, 'Update':update_clp_timestamp, 'Blank':lambda x: b'\x00' * 8, 'Init':add_clp_timestamp,
            'Class':datetime.datetime, 'Empty':none, 'flags':tuple(),
            },
    }
```

### Multi-line if

tables.py:2471:11  ( ... -> line 2474:45

```
def __eq__(self, other):
    if (self.src_table == other.src_table
    and self.src_field == other.src_field
    and self.tgt_table == other.tgt_table
    and self.tgt_field == other.tgt_field):
        return True
    return False
```

### strformat with even indentation

From constants.py:220.

```
return (
        '<%s.%s: %#02x>'
        %( self.__class__.__name__, self._name_, self._value_)
        )
```

From constants.py:259

```
return '<%s.%s: %r>' % (
        self.__class__.__name__,
        self._name_,
        to_bytes([self._value_]),
        )
```

### Visual indent

From _index.py:12

```
self.index_file.write(b'\xea\xaf\x37\xbf' +    # signature
                        b'\x00'*8           +    # two non-existant lists
                        b'\x00'*500)             # and no indices
```

### Only 4 space indentation

From: test.py:4857

```
self.dbf_table = table = Table(
    os.path.join(tempdir, 'temptable'),
    'name C(25); paid L; qty N(11,5); orderdate D; desc M', dbf_type='db3',
    overwrite=True,
    )
```

### Comma has its own line:

From test.py:3889

```
self.empty_vfp_table = Table(
        os.path.join(tempdir, 'emptytempvfp'),
        'name C(25); paid L; qty N(11,5); orderdate D; desc M; mass B;'
        ' weight F(18,3); age I; meeting T; misc G; photo P; price Y;'
        ' dist B BINARY; atom I BINARY; wealth Y BINARY;'
        ,
        dbf_type='vfp',
        overwrite=True,
        )
```

### Colon part is indented as content, should be 4

From: data_types.py:1112

```
for format in (
        "%H:%M:%S.%f",
        "%H:%M:%S",
        ):
```

### many 'or's are aligned with while

From data_types.py:742

```
    while ( not (0 < month < 13)
    or      not (0 < day <= days_in_month[month])
    or      not (0 <= hour < 24)
    or      not (0 <= minute < 60)
    or      not (0 <= second < 60)
    ):
```

### Two closing brackets are collapsed

From test.py:3740

```
self.assertEqual(
    dbf.scatter(record),
    dict(
        name=unicode('novice                   '),
        paid=False,
        qty=69,
        orderdate=datetime.date(2011, 1, 1),
        desc='master of all he surveys',
        ))
```

### Closing bracket line not aligned with content

From data_types.py:1502

```
return {
        (True, True)  : Falsth,
        (True, False) : Truth,
        (False, True) : Truth,
        (False, False): Falsth,
        }[(x, y)]
```
