-- =====================================================================
-- End of session shutdown check
-- Project: The Complete Snowflake & dbt Hands On Course
-- Author : Trinidad Cisneros
-- Purpose: confirm all warehouses are suspended before closing the day
--          so no compute charges accrue while you're away.
-- Cost   : zero (metadata only commands)
-- Where  : run from any worksheet (browser UI)
-- =====================================================================


-- ---------------------------------------------------------------------
-- STEP 1: View current warehouse states
-- Look at the "state" column in the results pane:
--   SUSPENDED → safe, no cost
--   STARTED   → run STEP 2 to force suspend
-- ---------------------------------------------------------------------
SHOW WAREHOUSES;


-- ---------------------------------------------------------------------
-- STEP 2: Force suspend any running warehouses
-- IMPORTANT: if a warehouse is already SUSPENDED, this line errors with
--   "Invalid state. Warehouse ... cannot be suspended."
-- That error is HARMLESS — it just confirms the warehouse is already off.
-- ---------------------------------------------------------------------
ALTER WAREHOUSE COMPUTE_WH SUSPEND;
ALTER WAREHOUSE MY_LARGEWH SUSPEND;


-- ---------------------------------------------------------------------
-- STEP 3: Verify everything is now suspended
-- ---------------------------------------------------------------------
SHOW WAREHOUSES;
