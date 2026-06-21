-- =====================================================================
-- Project: The Complete Snowflake & dbt Hands On Course
-- Section 1 — Snowflake basics (lectures 7 through 12)
-- Author : Trinidad Cisneros
-- Goal   : Build a typed WEATHER table from JSON files in a public S3
--          bucket, end to end, using Snowflake stages and COPY INTO.
-- =====================================================================
--
-- Note: account level cost guardrails (resource monitor MONTHLY_CAP_30USD,
-- COMPUTE_WH auto suspend = 60s, account STATEMENT_TIMEOUT_IN_SECONDS = 300)
-- are configured separately via ALTER ACCOUNT / ALTER WAREHOUSE and are
-- intentionally not in this project file.
-- =====================================================================


-- ---------------------------------------------------------------------
-- LECTURE 7 / 8 — First objects: database, schema, larger warehouse
-- Theory: most Snowflake objects live inside a schema, which lives
-- inside a database. Warehouses are the compute that does the work.
-- ---------------------------------------------------------------------

CREATE DATABASE DEMO;

CREATE SCHEMA DEMO.DEMO_SCHEMA;

-- Larger warehouse practice. Cost safe additions:
--   INITIALLY_SUSPENDED = TRUE  → born suspended, never starts unprompted
--   AUTO_SUSPEND        = 60    → stops within 60s of last query
CREATE WAREHOUSE MY_LARGEWH
  WITH WAREHOUSE_SIZE   = 'X-LARGE'
       INITIALLY_SUSPENDED = TRUE
       AUTO_SUSPEND     = 60;


-- ---------------------------------------------------------------------
-- LECTURE 9 — External stage pointing at the public S3 weather bucket
-- A stage is the doorstep into Snowflake. External = points at cloud
-- storage (S3 / Azure / GCS). LIST reads the file inventory.
-- ---------------------------------------------------------------------

CREATE OR REPLACE STAGE DEMO.DEMO_SCHEMA.weather_stage
  url         = 's3://snowflake-workshop-lab/weather-nyc'
  FILE_FORMAT = (TYPE = 'json');

LIST @DEMO.DEMO_SCHEMA.weather_stage;


-- ---------------------------------------------------------------------
-- LECTURE 10 — Intermediate VARIANT table to land the raw JSON
-- VARIANT can hold any semi structured value (objects, arrays, etc.).
-- One column called `data` holds the whole JSON payload per row.
-- ---------------------------------------------------------------------

CREATE OR REPLACE TABLE DEMO.DEMO_SCHEMA.WEATHERTABLE (data variant);

COPY INTO DEMO.DEMO_SCHEMA.WEATHERTABLE
FROM @DEMO.DEMO_SCHEMA.weather_stage;

SELECT * FROM DEMO.DEMO_SCHEMA.WEATHERTABLE;


-- ---------------------------------------------------------------------
-- LECTURE 11 — Navigate the VARIANT JSON with colon path syntax
-- Two tricks:
--   :   walks into a nested object  (data:city:coord:lat)
--   [n] picks an item from a JSON array (data:weather[0]:main)
-- ---------------------------------------------------------------------

SELECT
  data:city:findname,
  data:city:coord:lat,
  data:city:coord:lon,
  data:clouds:all,
  data:main:humidity,
  data:main:pressure,
  data:main:temp,
  data:time,
  data:weather[0]:main
FROM DEMO.DEMO_SCHEMA.WEATHERTABLE;


-- ---------------------------------------------------------------------
-- LECTURE 12 — Final typed WEATHER table + smarter COPY INTO
-- Build the destination once with proper column types, then COPY INTO
-- using a SELECT subquery that pulls fields straight from the stage.
-- `t.$1` references the only column when the stage holds JSON files.
-- ---------------------------------------------------------------------

CREATE OR REPLACE TABLE DEMO.DEMO_SCHEMA.WEATHER (
  CITYNAME  STRING,
  LAT       FLOAT,
  LON       FLOAT,
  CLOUDS    INTEGER,
  HUMIDITY  INTEGER,
  PRESSURE  FLOAT,
  TEMP      FLOAT,
  TIME      TIMESTAMP,
  WEATHER   STRING
);

COPY INTO DEMO.DEMO_SCHEMA.WEATHER
FROM (
  SELECT
    t.$1:city:findname,
    t.$1:city:coord:lat,
    t.$1:city:coord:lon,
    t.$1:clouds:all,
    t.$1:main:humidity,
    t.$1:main:pressure,
    t.$1:main:temp,
    t.$1:time,
    t.$1:weather[0]:main
  FROM @DEMO.DEMO_SCHEMA.weather_stage t
);

SELECT * FROM DEMO.DEMO_SCHEMA.WEATHER;


-- ---------------------------------------------------------------------
-- LECTURE 12 cleanup — drop the intermediate VARIANT table
-- ---------------------------------------------------------------------

DROP TABLE DEMO.DEMO_SCHEMA.WEATHERTABLE;


-- ---------------------------------------------------------------------
-- LECTURE 13 — Exercise (your turn, not yet completed)
-- Repeat the pattern with a new dataset:
--   - Stage URL : s3://snowflake-dbt-hands-on/
--   - Database  : PETS, schema PETS_SCHEMA, table PETS
--   - Columns   : LASTNAME, AGE, HOBBIE, PET_NAME, PET_TYPE
--   - Hint      : HOBBIE is a JSON array, use [0] to grab the first one
-- Paste your solution under this banner once complete.
-- ---------------------------------------------------------------------
