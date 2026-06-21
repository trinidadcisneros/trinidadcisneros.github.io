-- =====================================================================
-- Project: The Complete Snowflake & dbt Hands On Course
-- Section 1 — Exercise (lecture 13): load nested JSON from S3 into a
-- typed Snowflake table on your own.
-- Author : Trinidad Cisneros
-- Source : s3://snowflake-dbt-hands-on/  (root of public bucket,
--          contains owners-pets JSON files)
-- =====================================================================


-- ---------------------------------------------------------------------
-- STEP 1: Database and schema
-- ---------------------------------------------------------------------
CREATE OR REPLACE DATABASE PETS;
CREATE OR REPLACE SCHEMA PETS.PETS_SCHEMA;


-- ---------------------------------------------------------------------
-- STEP 2: External stage pointing at the bucket root
-- (no subfolder needed; LIST confirms what files are present)
-- ---------------------------------------------------------------------
CREATE OR REPLACE STAGE PETS.PETS_SCHEMA.pets_stage
  url         = 's3://snowflake-dbt-hands-on/'
  FILE_FORMAT = (TYPE = 'json');

LIST @PETS.PETS_SCHEMA.pets_stage;


-- ---------------------------------------------------------------------
-- STEP 3: Explore the JSON payload, confirm the field paths
-- Notes:
--   name and pet are nested objects → chain colons (name:last, pet:type)
--   hobbies is an array            → use [0] to grab the first hobby
-- ---------------------------------------------------------------------
SELECT
  t.$1:name:last  AS LASTNAME,
  t.$1:age        AS AGE,
  t.$1:hobbies[0] AS HOBBIE,
  t.$1:pet:name   AS PET_NAME,
  t.$1:pet:type   AS PET_TYPE
FROM @PETS.PETS_SCHEMA.pets_stage t;


-- ---------------------------------------------------------------------
-- STEP 4: Destination table (schema provided by the exercise)
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE PETS.PETS_SCHEMA.PETS (
  LASTNAME  STRING,
  AGE       INT,
  HOBBIE    STRING,
  PET_NAME  STRING,
  PET_TYPE  STRING
);


-- ---------------------------------------------------------------------
-- STEP 5: Copy from the stage into the typed PETS table
-- Same SELECT as step 3, wrapped in a COPY INTO so it lands in the table
-- ---------------------------------------------------------------------
COPY INTO PETS.PETS_SCHEMA.PETS
FROM (
  SELECT
    t.$1:name:last  AS LASTNAME,
    t.$1:age        AS AGE,
    t.$1:hobbies[0] AS HOBBIE,
    t.$1:pet:name   AS PET_NAME,
    t.$1:pet:type   AS PET_TYPE
  FROM @PETS.PETS_SCHEMA.pets_stage t
);


-- ---------------------------------------------------------------------
-- STEP 6: Validate the result
-- ---------------------------------------------------------------------
SELECT * FROM PETS.PETS_SCHEMA.PETS;


-- ---------------------------------------------------------------------
-- STEP 7: Clean up
-- ---------------------------------------------------------------------
DROP DATABASE PETS;
