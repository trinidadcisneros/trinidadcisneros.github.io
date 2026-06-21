-- =====================================================================
-- Project: The Complete Snowflake & dbt Hands On Course
-- Section 1 — Lectures 21 + 22: Check stage structure and COPY INTO
--            (Bike pipeline; ~35M rows of Citibike 2023 trip data)
-- Author : Trinidad Cisneros
-- Goal   : Inspect the staged CSV files, then load them into a typed
--          BIKE table using COPY INTO with error handling options.
-- Where  : run from any Snowflake worksheet (browser UI).
-- =====================================================================
--
-- COST FLAG — this is the first lecture that runs real compute on a
-- large dataset. Worst case scenarios:
--   * X-Small  : SELECT/COPY may take ~5 minutes (~0.08 credits ≈ $0.25)
--   * X-Large  : same work in ~10 seconds       (~0.04 credits ≈ $0.13)
-- Either is fine; we'll briefly use X-Large for the COPY then switch
-- right back to X-Small and let auto suspend kick in.
--
-- KEY CONCEPT — schema check before COPY:
-- You should always preview a stage's columns BEFORE writing a COPY
-- INTO statement. The `t.$N` syntax exposes the Nth column of any
-- file in the stage so you can confirm the structure first.
--
-- KEY CONCEPT — ON_ERROR options for COPY INTO:
--   * ABORT_STATEMENT (default) — one bad row → whole COPY fails
--   * CONTINUE                   — bad rows skipped, COPY keeps going
--   * SKIP_FILE                  — skip the entire file if any row fails
--   * SKIP_FILE_<N>              — skip the file if it has N+ bad rows
-- We use SKIP_FILE_1 below + STRING typed columns so the COPY succeeds.
--
-- KEY DECISION — all columns typed as STRING:
-- Daniel loads everything as STRING to avoid date/float parsing errors
-- on 35M rows. The pattern is "land first, type later" — once the data
-- is in Snowflake we'll convert columns when we transform with dbt.
-- =====================================================================


-- ---------------------------------------------------------------------
-- ACTION 1 — Set context (role, database, schema, warehouse)
-- Why:
--   - USE ROLE ACCOUNTADMIN: needed because BIKE_STAGE was created here.
--   - USE DATABASE / SCHEMA: lets us reference objects without full path.
--   - Use COMPUTE_WH for the lightweight inspection in Action 2.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;
USE DATABASE DEMO;
USE SCHEMA DEMO_SCHEMA;
USE WAREHOUSE COMPUTE_WH;


-- ---------------------------------------------------------------------
-- ACTION 2 — Lecture 21: Peek at the staged CSV structure
-- Why:
--   - You can't write a good COPY INTO without knowing the columns.
--   - t.$1 ... t.$14 references the 1st through 14th column of each file.
--   - We grab 14 columns even though the Citibike schema lists 13 — the
--     extra t.$14 is a sanity check that nothing trails after col 13.
--   - Expected: rows of strings; the 1st row contains the headers, and
--     column 14 should be NULL across all rows (confirming 13 cols total).
-- Cost note:
--   - This is the first heavy query (40 CSVs, 1.5 GB compressed, 35M rows).
--   - On X-Small (current) it takes ~30-60 seconds. Acceptable.
-- ---------------------------------------------------------------------
SELECT
  t.$1,
  t.$2,
  t.$3,
  t.$4,
  t.$5,
  t.$6,
  t.$7,
  t.$8,
  t.$9,
  t.$10,
  t.$11,
  t.$12,
  t.$13,
  t.$14
FROM @DEMO.DEMO_SCHEMA.BIKE_STAGE t
LIMIT 100;
-- LIMIT 100 added vs Daniel's full-scan: keeps the schema check cheap.
-- Remove the LIMIT only if you need to verify the full file inventory.


-- ---------------------------------------------------------------------
-- ACTION 3 — Lecture 22 step 1: Create the BIKE destination table
-- Why:
--   - The 13 columns of the Citibike schema (per the source website).
--   - All STRING so the COPY can't fail on type parsing errors.
--   - Typos fixed from Daniel's resource file:
--       START_STATIO_ID  → START_STATION_ID
--       MEMBER_CSUAL     → MEMBER_CASUAL
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE DEMO.DEMO_SCHEMA.BIKE (
  RIDE_ID            STRING,
  RIDEABLE_TYPE      STRING,
  STARTED_AT         STRING,
  ENDED_AT           STRING,
  START_STATION_NAME STRING,
  START_STATION_ID   STRING,
  END_STATION_NAME   STRING,
  END_STATION_ID     STRING,
  START_LAT          STRING,
  START_LNG          STRING,
  END_LAT            STRING,
  END_LNG            STRING,
  MEMBER_CASUAL      STRING
);


-- ---------------------------------------------------------------------
-- ACTION 4 — Switch to the larger warehouse for the bulk load
-- Why:
--   - COPY INTO of 35M rows on X-Small takes ~5 minutes; on X-Large
--     it takes ~10 seconds. Net cost is similar (X-Large is 16x faster
--     for 16x the credit rate) but the wall clock time is huge.
--   - MY_LARGEWH starts suspended and auto suspends after 60 seconds,
--     so we won't accidentally leave it running.
--   - We'll switch back to COMPUTE_WH right after the COPY.
-- ---------------------------------------------------------------------
USE WAREHOUSE MY_LARGEWH;


-- ---------------------------------------------------------------------
-- ACTION 5 — Lecture 22 step 2: COPY INTO with error handling
-- Why:
--   - SELECT subquery picks columns 1-13 from each CSV (skipping the
--     non-existent 14th column we confirmed in Action 2).
--   - ON_ERROR = SKIP_FILE_1 means: if a file has 1 or more parsing
--     errors, skip the WHOLE file rather than aborting the whole COPY.
--     This shields us against the header row appearing as data.
--   - Expected: 40 files loaded, ~35M rows in ~10 seconds on X-Large.
-- ---------------------------------------------------------------------
COPY INTO DEMO.DEMO_SCHEMA.BIKE
FROM (
  SELECT
    t.$1,
    t.$2,
    t.$3,
    t.$4,
    t.$5,
    t.$6,
    t.$7,
    t.$8,
    t.$9,
    t.$10,
    t.$11,
    t.$12,
    t.$13
  FROM @DEMO.DEMO_SCHEMA.BIKE_STAGE t
)
ON_ERROR = SKIP_FILE_1;


-- ---------------------------------------------------------------------
-- ACTION 6 — Verify the load
-- Why:
--   - Confirm BIKE has roughly 35 million rows.
--   - LIMIT 10 keeps the preview cheap.
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS ROW_COUNT FROM DEMO.DEMO_SCHEMA.BIKE;

SELECT * FROM DEMO.DEMO_SCHEMA.BIKE LIMIT 10;


-- ---------------------------------------------------------------------
-- ACTION 7 — Cost safety: switch back to X-Small and suspend X-Large
-- Why:
--   - MY_LARGEWH would auto suspend in 60 seconds anyway, but explicit
--     SUSPEND avoids any risk of an idle big warehouse.
--   - Reset the active warehouse to COMPUTE_WH for future queries.
-- ---------------------------------------------------------------------
USE WAREHOUSE COMPUTE_WH;
ALTER WAREHOUSE MY_LARGEWH SUSPEND;


-- =====================================================================
-- END OF LECTURES 21 + 22
-- Next up: lecture 23 (Loading Data from Stages & Error Handling),
-- where Daniel goes deeper on debugging bad rows.
-- =====================================================================
