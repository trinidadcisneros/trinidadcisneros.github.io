* Encoding: UTF-8.

DATASET ACTIVATE DataSet1.
UNIANOVA political_interest BY political_spectrum education_level
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PLOT=PROFILE(education_level*political_spectrum political_spectrum*education_level)
  /EMMEANS=TABLES(political_spectrum*education_level) COMPARE(political_spectrum) ADJ(BONFERRONI)
  /EMMEANS=TABLES(political_spectrum*education_level) COMPARE(education_level) ADJ(BONFERRONI)
  /PRINT ETASQ DESCRIPTIVE HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=political_spectrum education_level political_spectrum*education_level.
