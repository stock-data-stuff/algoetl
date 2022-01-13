
create schema if not exists testschema;

DROP TABLE IF EXISTS testschema.test_util;

-- SQL Standard Types.
CREATE TABLE testschema.test_util (
    int_col int,
    numeric_col numeric,
    float_col float,
    varchar_col varchar,
    bigint_col bigint,
    decimal_col decimal,
    double_col double precision,
    smallint_col smallint,
    boolean_col boolean,
    date_col date,
    timestamp_col timestamp
);


-- Test data. Confirms formatting
insert into testschema.test_util
(int_col, numeric_col, float_col, varchar_col, bigint_col,
 decimal_col, double_col, smallint_col, boolean_col,
 date_col, timestamp_col)
values (2147483647, 12345678901234.1, 123456.789, 'varchar11', 9223372036854775807,
        12345678901234.2, 1234567890.12345, 32767, true,
        '2018-12-12', '2018-12-12T13:49:51.141Z');

insert into testschema.test_util
(int_col, numeric_col, float_col, varchar_col, bigint_col,
 decimal_col, double_col, smallint_col, boolean_col,
 date_col, timestamp_col)
values (-2147483647, -12345678901234.1, -123456.789, 'varchar22', -9223372036854775807,
        -12345678901234.2, -1234567890.12345, -32768, true,
        '2018-12-13', '2018-12-13T14:49:51.141Z');

-- Use these during dev to clear and view the test data.
-- truncate table testschema.test_util;
select count(*) as cnt from testschema.test_util;
select * from testschema.test_util limit 10;

-- Show schemas
SELECT schema_name FROM information_schema.schemata;
\dn


