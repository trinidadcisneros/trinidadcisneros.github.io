-- =====================================================================
-- Project: The Complete Snowflake & dbt Hands On Course
-- Section 1 — Exercise (lecture 19): Create a Role Analyst
-- Author : Trinidad Cisneros
-- Goal   : Build a custom ANALYST role from scratch and grant it the
--          minimum privileges it needs to read BIKE_STAGE.
-- Cost   : zero (all metadata; no warehouse compute).
-- Where  : run from any Snowflake worksheet (browser UI).
-- =====================================================================
--
-- KEY CONCEPT — the hierarchy:
--   Database  →  Schema  →  Objects (tables, stages, etc.)
-- A role can only "see" an object if it has USAGE all the way down the
-- chain, PLUS the object specific privilege at the end.
-- Missing any link = the object is invisible to that role.
--
-- KEY CONCEPT — internal vs external stages:
--   External stage (S3, Azure, GCS) → grant USAGE
--   Internal stage (Snowflake managed, from PUT) → grant READ and WRITE
-- We use READ and WRITE below because BIKE_STAGE is an internal stage.
-- =====================================================================


-- ---------------------------------------------------------------------
-- ACTION 1 — Set the testing context and create the role
-- Why:
--   - USE ROLE ACCOUNTADMIN: only high privilege roles can create roles
--     and grant cross database access; your default at login is PUBLIC.
--   - USE SECONDARY ROLES NONE: turns off auto inherited privileges so
--     when we test the ANALYST role later, we see ONLY what ANALYST has,
--     not leaked privileges from other roles you also hold.
--   - CREATE ROLE ANALYST: makes an empty bucket; zero privileges yet.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;
USE SECONDARY ROLES NONE;
CREATE ROLE ANALYST;


-- ---------------------------------------------------------------------
-- ACTION 2 — Grant the new role to your user
-- Why:
--   - GRANT ROLE ... TO USER doesn't transfer privileges between roles.
--   - It just gives your user a new "name tag" you can switch into
--     with USE ROLE later.
-- ---------------------------------------------------------------------
GRANT ROLE ANALYST TO USER TRINIDADCISNEROS;


-- ---------------------------------------------------------------------
-- ACTION 3 — Switch into ANALYST and observe what's missing
-- Why:
--   - Confirms the role has zero privileges by default.
--   - Expected result: SHOW DATABASES shows ~3 system databases but
--     NOT your DEMO database. That's the whole point of the exercise.
-- ---------------------------------------------------------------------
USE ROLE ANALYST;
SHOW DATABASES;


-- ---------------------------------------------------------------------
-- ACTION 4 — Grant stage level privileges (with an intentional error)
-- Why:
--   - Snowflake treats internal vs external stages differently.
--   - The first GRANT (USAGE ON STAGE) is meant to FAIL so you see the
--     error: "cannot grant or revoke USAGE on an internal stage location;
--     use READ and/or WRITE instead." That's a deliberate teaching moment.
--   - READ lets the role list files and run COPY FROM the stage.
--   - WRITE lets the role PUT files into the stage.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;

-- This line will fail on purpose — that's the lesson
GRANT USAGE ON STAGE DEMO.DEMO_SCHEMA.BIKE_STAGE TO ROLE ANALYST;

-- These two are the correct grants for an internal stage
GRANT READ ON STAGE DEMO.DEMO_SCHEMA.BIKE_STAGE TO ROLE ANALYST;
GRANT WRITE ON STAGE DEMO.DEMO_SCHEMA.BIKE_STAGE TO ROLE ANALYST;


-- ---------------------------------------------------------------------
-- ACTION 5 — Grant database access and re check
-- Why:
--   - Stage grants alone don't work — the role still can't "see" the
--     database that contains the schema that contains the stage.
--   - USAGE on the database opens the outer door.
--   - Expected: ANALYST can now see DEMO in SHOW DATABASES, but
--     SHOW SCHEMAS IN DATABASE DEMO would still return nothing.
-- ---------------------------------------------------------------------
GRANT USAGE ON DATABASE DEMO TO ROLE ANALYST;

USE ROLE ANALYST;
SHOW DATABASES;


-- ---------------------------------------------------------------------
-- ACTION 6 — Grant schema access and verify the full chain works
-- Why:
--   - USAGE on the schema opens the inner door.
--   - With database + schema + stage grants all in place, ANALYST can
--     finally see and list BIKE_STAGE.
--   - Expected: SHOW SCHEMAS returns DEMO_SCHEMA; LIST returns your 40
--     uploaded files.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA DEMO.DEMO_SCHEMA TO ROLE ANALYST;

USE ROLE ANALYST;
SHOW SCHEMAS IN DATABASE DEMO;
LIST @DEMO.DEMO_SCHEMA.BIKE_STAGE;


-- ---------------------------------------------------------------------
-- CLEANUP (from lecture 20) — Restore default secondary role behavior
-- Why:
--   - We turned secondary roles OFF in Action 1 for a clean test.
--   - Turning them back ON restores Snowflake's normal behavior so the
--     rest of your work doesn't randomly lose privileges.
-- ---------------------------------------------------------------------
USE ROLE ACCOUNTADMIN;
USE SECONDARY ROLES ALL;
