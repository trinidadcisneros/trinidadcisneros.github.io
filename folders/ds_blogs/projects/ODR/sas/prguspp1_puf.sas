%LET DATADIR  = <Please paste the full path of the directory, in which your data file resides here.> ;
%LET DATAFILE = prguspp1_puf;

LIBNAME DATALIB "&DATADIR" ;
LIBNAME LIBRARY "<Please paste the full path of the directory, in which your format catalog resides.>" ;

PROC FORMAT LIB=LIBRARY ;
  VALUE AGE1634_
    0 = "35 - 74 years old"
    1 = "16 - 34 years old"
  ;
  VALUE AGE6674_
    0 = "16 - 65 years old"
    1 = "66 - 74 years old"
  ;
  VALUE AGEG10LFSEXT
    1 = "24 or less"
    2 = "25-34"
    3 = "35-44"
    4 = "45-54"
    5 = "55-65"
    6 = "66 plus"
    .N = "Not stated or inferred"
  ;
  VALUE AGEG5LFSEXT
    1 = "Aged 16-19"
    2 = "Aged 20-24"
    3 = "Aged 25-29"
    4 = "Aged 30-34"
    5 = "Aged 35-39"
    6 = "Aged 40-44"
    7 = "Aged 45-49"
    8 = "Aged 50-54"
    9 = "Aged 55-59"
    .N = "Not stated or inferred"
    10 = "Aged 60-65"
    11 = "Aged 66-70"
    12 = "71 plus"
  ;
  VALUE BIRTHRGNUS_C
    1 = "North America and Western Europe"
    2 = "Latin America and the Caribbean"
    3 = "other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE BORNLANG
    1 = "Native-born and native-language"
    2 = "Native-born and foreign-language"
    3 = "Foreign-born and native-language"
    4 = "Foreign-born and foreign-language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_D01D_C
    1 = "less than 1 year"
    2 = "1 to less than 2 years"
    3 = "2 to less than 5 years"
    4 = "5 to less than 10 years"
    5 = "10 years or more"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q01A
    1 = "No formal qualification or below ISCED 1"
    2 = "ISCED 1"
    3 = "ISCED 2"
    4 = "ISCED 3C shorter than 2 years"
    5 = "ISCED 3C 2 years or more"
    6 = "ISCED 3A-B"
    7 = "ISCED 3 (without distinction A-B-C, 2y+)"
    8 = "ISCED 4C"
    9 = "ISCED 4A-B"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "ISCED 4 (without distinction A-B-C)"
    11 = "ISCED 5B"
    12 = "ISCED 5A, bachelor degree"
    13 = "ISCED 5A, master degree"
    14 = "ISCED 6"
    15 = "Foreign qualification"
    16 = "ISCED 5A bachelor degree, 5A master degree, and 6 (without distinction)"
  ;
  VALUE B_Q01A3_ISCED11F
    1 = "No formal qualification or below ISCED 1"
    2 = "ISCED 1"
    3 = "ISCED 2"
    4 = "ISCED 3"
    5 = "ISCED 4"
    6 = "ISCED 5"
    7 = "ISCED 6"
    8 = "ISCED 7"
    9 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Foreign qualification"
  ;
  VALUE B_Q01AUS_C
    1 = "Less than high school diploma"
    2 = "High school diploma/some college but no degree"
    3 = "College degree or higher (associate, bachelor, doctorate)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q01A_C
    1 = "ISCED 2 and below"
    2 = "ISCED 3 and 4a-b"
    3 = "ISCED 5a-b and 6"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q01A_ISCED11F
    1 = "No formal qualification or below ISCED 1"
    2 = "ISCED 1"
    3 = "ISCED 2"
    4 = "ISCED 3"
    5 = "ISCED 4"
    6 = "ISCED 5"
    7 = "ISCED 6"
    8 = "ISCED 7"
    9 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Foreign qualification"
  ;
  VALUE B_Q01B
    1 = "General programmes"
    2 = "Teacher training and education science"
    3 = "Humanities, languages and arts"
    4 = "Social sciences, business and law"
    5 = "Science, mathematics and computing"
    6 = "Engineering, manufacturing and construction"
    7 = "Agriculture and veterinary"
    8 = "Health and welfare"
    9 = "Services"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q01C1_C
    1 = "Aged 15 or younger"
    2 = "Aged 16-19"
    3 = "Aged 20-24"
    4 = "Aged 25-29"
    5 = "Aged 30-34"
    6 = "Aged 35 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q02A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q02BUS_C
    1 = "ISCED 3 (without distinction A-B-C, 2y+) or lower"
    2 = "ISCED 4C"
    3 = "ISCED 4A, ISCED 4B"
    4 = "ISCED 5B, associate degree"
    5 = "ISCED 5A, bachelor degree"
    6 = "ISCED 5A, master degree, ISCED 6"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q02B_ISCED11F
    1 = "ISCED 1"
    2 = "ISCED 2"
    3 = "ISCED 3"
    4 = "ISCED 4"
    5 = "ISCED 5"
    6 = "ISCED 6"
    7 = "ISCED 7"
    8 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q02CUS_C
    1 = "General programmes"
    2 = "Teacher training and education science"
    3 = "Humanities, languages and arts"
    4 = "Social sciences, business and law"
    5 = "Science, mathematics and computing"
    6 = "Engineering, manufacturing and construction, Agriculture"
    7 = "Health and welfare"
    8 = "Services"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q03A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q03A_USR
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q03BUS_C
    1 = "ISCED 3 (without distinction A-B-C, 2y+) or lower"
    2 = "ISCED 4C"
    3 = "ISCED 4A, ISCED 4B"
    4 = "ISCED 5B, associate degree"
    5 = "ISCED 5A, bachelor degree"
    6 = "ISCED 5A, master degree, ISCED 6"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q03B_ISCED11F
    1 = "ISCED 1"
    2 = "ISCED 2"
    3 = "ISCED 3"
    4 = "ISCED 4"
    5 = "ISCED 5"
    6 = "ISCED 6"
    7 = "ISCED 7"
    8 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q03B_USR
    1 = "ISCED 1"
    2 = "ISCED 2"
    3 = "ISCED 3C shorter than 2 years"
    4 = "ISCED 3C 2 years or more"
    5 = "ISCED 3A-B"
    6 = "ISCED 3 (without distinction A-B-C, 2y+)"
    7 = "ISCED 4C"
    8 = "ISCED 4A-B"
    9 = "ISCED 4 (without distinction A-B-C)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "ISCED 5B"
    11 = "ISCED 5A, bachelor degree"
    12 = "ISCED 5A, master degree"
    13 = "ISCED 6"
    14 = "ISCED 5A bachelor degree, 5A master degree, and 6 (without distinction)"
  ;
  VALUE B_Q27AUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q27BUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE B_Q27CUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE C300C02A
    .N = "Not reached/Not attempted"
  ;
  VALUE C300C02F
    .N = "Not reached/Not attempted"
  ;
  VALUE C300C02S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C300C02T
    .N = "Not reached/Not attempted"
  ;
  VALUE C301C05A
    .N = "Not reached/Not attempted"
  ;
  VALUE C301C05F
    .N = "Not reached/Not attempted"
  ;
  VALUE C301C05S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C301C05T
    .N = "Not reached/Not attempted"
  ;
  VALUE C305215A
    .N = "Not reached/Not attempted"
  ;
  VALUE C305215F
    .N = "Not reached/Not attempted"
  ;
  VALUE C305215S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C305215T
    .N = "Not reached/Not attempted"
  ;
  VALUE C305218A
    .N = "Not reached/Not attempted"
  ;
  VALUE C305218F
    .N = "Not reached/Not attempted"
  ;
  VALUE C305218S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C305218T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308116A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308116F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308116S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308116T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308117A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308117F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308117S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308117T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308118A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308118F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308118S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308118T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308119A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308119F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308119S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308119T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308120A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308120F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308120S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308120T
    .N = "Not reached/Not attempted"
  ;
  VALUE C308121A
    .N = "Not reached/Not attempted"
  ;
  VALUE C308121F
    .N = "Not reached/Not attempted"
  ;
  VALUE C308121S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C308121T
    .N = "Not reached/Not attempted"
  ;
  VALUE C309319A
    .N = "Not reached/Not attempted"
  ;
  VALUE C309319F
    .N = "Not reached/Not attempted"
  ;
  VALUE C309319S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C309319T
    .N = "Not reached/Not attempted"
  ;
  VALUE C309320A
    .N = "Not reached/Not attempted"
  ;
  VALUE C309320F
    .N = "Not reached/Not attempted"
  ;
  VALUE C309320S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C309320T
    .N = "Not reached/Not attempted"
  ;
  VALUE C309321A
    .N = "Not reached/Not attempted"
  ;
  VALUE C309321F
    .N = "Not reached/Not attempted"
  ;
  VALUE C309321S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C309321T
    .N = "Not reached/Not attempted"
  ;
  VALUE C309322A
    .N = "Not reached/Not attempted"
  ;
  VALUE C309322F
    .N = "Not reached/Not attempted"
  ;
  VALUE C309322S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C309322T
    .N = "Not reached/Not attempted"
  ;
  VALUE C310406A
    .N = "Not reached/Not attempted"
  ;
  VALUE C310406F
    .N = "Not reached/Not attempted"
  ;
  VALUE C310406S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C310406T
    .N = "Not reached/Not attempted"
  ;
  VALUE C310407A
    .N = "Not reached/Not attempted"
  ;
  VALUE C310407F
    .N = "Not reached/Not attempted"
  ;
  VALUE C310407S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C310407T
    .N = "Not reached/Not attempted"
  ;
  VALUE C313410A
    .N = "Not reached/Not attempted"
  ;
  VALUE C313410F
    .N = "Not reached/Not attempted"
  ;
  VALUE C313410S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C313410T
    .N = "Not reached/Not attempted"
  ;
  VALUE C313411A
    .N = "Not reached/Not attempted"
  ;
  VALUE C313411F
    .N = "Not reached/Not attempted"
  ;
  VALUE C313411S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C313411T
    .N = "Not reached/Not attempted"
  ;
  VALUE C313412A
    .N = "Not reached/Not attempted"
  ;
  VALUE C313412F
    .N = "Not reached/Not attempted"
  ;
  VALUE C313412S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C313412T
    .N = "Not reached/Not attempted"
  ;
  VALUE C313413A
    .N = "Not reached/Not attempted"
  ;
  VALUE C313413F
    .N = "Not reached/Not attempted"
  ;
  VALUE C313413S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C313413T
    .N = "Not reached/Not attempted"
  ;
  VALUE C313414A
    .N = "Not reached/Not attempted"
  ;
  VALUE C313414F
    .N = "Not reached/Not attempted"
  ;
  VALUE C313414S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C313414T
    .N = "Not reached/Not attempted"
  ;
  VALUE C600C04A
    .N = "Not reached/Not attempted"
  ;
  VALUE C600C04F
    .N = "Not reached/Not attempted"
  ;
  VALUE C600C04S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C600C04T
    .N = "Not reached/Not attempted"
  ;
  VALUE C601C06A
    .N = "Not reached/Not attempted"
  ;
  VALUE C601C06F
    .N = "Not reached/Not attempted"
  ;
  VALUE C601C06S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C601C06T
    .N = "Not reached/Not attempted"
  ;
  VALUE C602501A
    .N = "Not reached/Not attempted"
  ;
  VALUE C602501F
    .N = "Not reached/Not attempted"
  ;
  VALUE C602501S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C602501T
    .N = "Not reached/Not attempted"
  ;
  VALUE C602502A
    .N = "Not reached/Not attempted"
  ;
  VALUE C602502F
    .N = "Not reached/Not attempted"
  ;
  VALUE C602502S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C602502T
    .N = "Not reached/Not attempted"
  ;
  VALUE C602503A
    .N = "Not reached/Not attempted"
  ;
  VALUE C602503F
    .N = "Not reached/Not attempted"
  ;
  VALUE C602503S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C602503T
    .N = "Not reached/Not attempted"
  ;
  VALUE C604505A
    .N = "Not reached/Not attempted"
  ;
  VALUE C604505F
    .N = "Not reached/Not attempted"
  ;
  VALUE C604505S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C604505T
    .N = "Not reached/Not attempted"
  ;
  VALUE C605506A
    .N = "Not reached/Not attempted"
  ;
  VALUE C605506F
    .N = "Not reached/Not attempted"
  ;
  VALUE C605506S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C605506T
    .N = "Not reached/Not attempted"
  ;
  VALUE C605507A
    .N = "Not reached/Not attempted"
  ;
  VALUE C605507F
    .N = "Not reached/Not attempted"
  ;
  VALUE C605507S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C605507T
    .N = "Not reached/Not attempted"
  ;
  VALUE C605508A
    .N = "Not reached/Not attempted"
  ;
  VALUE C605508F
    .N = "Not reached/Not attempted"
  ;
  VALUE C605508S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C605508T
    .N = "Not reached/Not attempted"
  ;
  VALUE C606509A
    .N = "Not reached/Not attempted"
  ;
  VALUE C606509F
    .N = "Not reached/Not attempted"
  ;
  VALUE C606509S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C606509T
    .N = "Not reached/Not attempted"
  ;
  VALUE C607510A
    .N = "Not reached/Not attempted"
  ;
  VALUE C607510F
    .N = "Not reached/Not attempted"
  ;
  VALUE C607510S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C607510T
    .N = "Not reached/Not attempted"
  ;
  VALUE C608513A
    .N = "Not reached/Not attempted"
  ;
  VALUE C608513F
    .N = "Not reached/Not attempted"
  ;
  VALUE C608513S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C608513T
    .N = "Not reached/Not attempted"
  ;
  VALUE C611516A
    .N = "Not reached/Not attempted"
  ;
  VALUE C611516F
    .N = "Not reached/Not attempted"
  ;
  VALUE C611516S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C611516T
    .N = "Not reached/Not attempted"
  ;
  VALUE C611517A
    .N = "Not reached/Not attempted"
  ;
  VALUE C611517F
    .N = "Not reached/Not attempted"
  ;
  VALUE C611517S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C611517T
    .N = "Not reached/Not attempted"
  ;
  VALUE C612518A
    .N = "Not reached/Not attempted"
  ;
  VALUE C612518F
    .N = "Not reached/Not attempted"
  ;
  VALUE C612518S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C612518T
    .N = "Not reached/Not attempted"
  ;
  VALUE C613520A
    .N = "Not reached/Not attempted"
  ;
  VALUE C613520F
    .N = "Not reached/Not attempted"
  ;
  VALUE C613520S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C613520T
    .N = "Not reached/Not attempted"
  ;
  VALUE C614601A
    .N = "Not reached/Not attempted"
  ;
  VALUE C614601F
    .N = "Not reached/Not attempted"
  ;
  VALUE C614601S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C614601T
    .N = "Not reached/Not attempted"
  ;
  VALUE C615602A
    .N = "Not reached/Not attempted"
  ;
  VALUE C615602F
    .N = "Not reached/Not attempted"
  ;
  VALUE C615602S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C615602T
    .N = "Not reached/Not attempted"
  ;
  VALUE C615603A
    .N = "Not reached/Not attempted"
  ;
  VALUE C615603F
    .N = "Not reached/Not attempted"
  ;
  VALUE C615603S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C615603T
    .N = "Not reached/Not attempted"
  ;
  VALUE C617605A
    .N = "Not reached/Not attempted"
  ;
  VALUE C617605F
    .N = "Not reached/Not attempted"
  ;
  VALUE C617605S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C617605T
    .N = "Not reached/Not attempted"
  ;
  VALUE C617606A
    .N = "Not reached/Not attempted"
  ;
  VALUE C617606F
    .N = "Not reached/Not attempted"
  ;
  VALUE C617606S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C617606T
    .N = "Not reached/Not attempted"
  ;
  VALUE C618607A
    .N = "Not reached/Not attempted"
  ;
  VALUE C618607F
    .N = "Not reached/Not attempted"
  ;
  VALUE C618607S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C618607T
    .N = "Not reached/Not attempted"
  ;
  VALUE C618608A
    .N = "Not reached/Not attempted"
  ;
  VALUE C618608F
    .N = "Not reached/Not attempted"
  ;
  VALUE C618608S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C618608T
    .N = "Not reached/Not attempted"
  ;
  VALUE C619609A
    .N = "Not reached/Not attempted"
  ;
  VALUE C619609F
    .N = "Not reached/Not attempted"
  ;
  VALUE C619609S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C619609T
    .N = "Not reached/Not attempted"
  ;
  VALUE C620610A
    .N = "Not reached/Not attempted"
  ;
  VALUE C620610F
    .N = "Not reached/Not attempted"
  ;
  VALUE C620610S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C620610T
    .N = "Not reached/Not attempted"
  ;
  VALUE C620612A
    .N = "Not reached/Not attempted"
  ;
  VALUE C620612F
    .N = "Not reached/Not attempted"
  ;
  VALUE C620612S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C620612T
    .N = "Not reached/Not attempted"
  ;
  VALUE C622615A
    .N = "Not reached/Not attempted"
  ;
  VALUE C622615F
    .N = "Not reached/Not attempted"
  ;
  VALUE C622615S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C622615T
    .N = "Not reached/Not attempted"
  ;
  VALUE C623616A
    .N = "Not reached/Not attempted"
  ;
  VALUE C623616F
    .N = "Not reached/Not attempted"
  ;
  VALUE C623616S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C623616T
    .N = "Not reached/Not attempted"
  ;
  VALUE C623617A
    .N = "Not reached/Not attempted"
  ;
  VALUE C623617F
    .N = "Not reached/Not attempted"
  ;
  VALUE C623617S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C623617T
    .N = "Not reached/Not attempted"
  ;
  VALUE C624619A
    .N = "Not reached/Not attempted"
  ;
  VALUE C624619F
    .N = "Not reached/Not attempted"
  ;
  VALUE C624619S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C624619T
    .N = "Not reached/Not attempted"
  ;
  VALUE C624620A
    .N = "Not reached/Not attempted"
  ;
  VALUE C624620F
    .N = "Not reached/Not attempted"
  ;
  VALUE C624620S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE C624620T
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD1STG1_
    0 = "Missing"
    1 = "Easy"
    2 = "Medium"
    3 = "Hard"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD1STG2_
    0 = "Missing"
    1 = "Easy"
    2 = "Medium 1"
    3 = "Medium 2"
    4 = "Hard"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD1_
    0 = "Missing"
    1 = "LIT"
    2 = "NUM"
    3 = "PS1"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD2ALT
    0 = "Missing"
    .N = "Not reached/Not attempted"
    12 = "LIT-NUM"
    13 = "LIT-PS2"
    21 = "NUM-LIT"
    23 = "NUM-PS2"
    31 = "PS1-LIT"
    32 = "PS1-NUM"
    33 = "PS1-PS2"
  ;
  VALUE CBAMOD2STG1_
    0 = "Missing"
    1 = "Easy"
    2 = "Medium"
    3 = "Hard"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD2STG2_
    0 = "Missing"
    1 = "Easy"
    2 = "Medium 1"
    3 = "Medium 2"
    4 = "Hard"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBAMOD2_
    0 = "Missing"
    1 = "LIT"
    2 = "NUM"
    3 = "PS2"
    .N = "Not reached/Not attempted"
  ;
  VALUE CBA_CORE_STAGE1_SCORE
    .N = "Not stated or inferred"
  ;
  VALUE CBA_CORE_STAGE2_SCORE
    .N = "Not stated or inferred"
  ;
  VALUE CBA_START
    1 = "Continue to computer based exercise"
    2 = "Continue to paper based exercise"
    .N = "Not reached/Not attempted"
  ;
  VALUE CILANG
    1 = "English"
    2 = "German"
    3 = "Dutch"
    4 = "Spanish"
    5 = "French"
    6 = "Greek"
    7 = "Czech"
    8 = "Danish"
    9 = "Estonian"
    .N = "Not stated or inferred"
    10 = "Russian"
    11 = "Finnish"
    12 = "Swedish"
    13 = "German"
    14 = "Hungarian"
    15 = "Italian"
    16 = "Japanese"
    17 = "Korean"
    18 = "Dutch"
    19 = "Norwegian (Bokmål)"
    20 = "Polish"
    21 = "Portuguese"
    22 = "Russian"
    23 = "Slovak"
    24 = "Slovenian"
    25 = "Basque"
    26 = "Catalan"
    27 = "Spanish"
    28 = "Galician"
    29 = "Valencian"
    30 = "Swedish"
    31 = "Welsh"
  ;
  VALUE $CNTRY
    AUS = "Australia"
    AUT = "Austria"
    BELL = "Flanders (Belgium)"
    CAN = "Canada"
    CANE = "Canada (English)"
    CANF = "Canada (French)"
    CYP = "Cyprus"
    CZE = "Czech Republic"
    DEU = "Germany"
    DNK = "Denmark"
    ESP = "Spain"
    EST = "Estonia"
    FIN = "Finland"
    FRA = "France"
    GBR = "England/N. Ireland (UK)"
    GBRE = "England (UK)"
    GBRN = "Northern Ireland (UK)"
    IRL = "Ireland"
    ITA = "Italy"
    JPN = "Japan"
    KOR = "Korea"
    NLD = "Netherlands"
    NOR = "Norway"
    POL = "Poland"
    RUS = "Russian Federation"
    SVK = "Slovak Republic"
    SWE = "Sweden"
    USA = "United States"
  ;
  VALUE CNTRYID
    36 = "Australia"
    40 = "Austria"
    56 = "Belgium"
    124 = "Canada"
    196 = "Cyprus"
    203 = "Czech Republic"
    208 = "Denmark"
    233 = "Estonia"
    246 = "Finland"
    250 = "France"
    276 = "Germany"
    372 = "Ireland"
    380 = "Italy"
    392 = "Japan"
    410 = "Korea"
    528 = "Netherlands"
    578 = "Norway"
    616 = "Poland"
    643 = "Russian Federation"
    703 = "Slovak Republic"
    724 = "Spain"
    752 = "Sweden"
    826 = "United Kingdom"
    840 = "United States"
    84091 = "United States (16-74 y.o. sample)"
    84092 = "United States (prison sample)"
  ;
  VALUE CNTRYID_E
    36 = "Australia"
    40 = "Austria"
    124 = "Canada"
    196 = "Cyprus"
    203 = "Czech Republic"
    208 = "Denmark"
    233 = "Estonia"
    246 = "Finland"
    250 = "France"
    276 = "Germany"
    372 = "Ireland"
    380 = "Italy"
    392 = "Japan"
    410 = "Korea"
    528 = "Netherlands"
    578 = "Norway"
    616 = "Poland"
    643 = "Russian Federation"
    703 = "Slovak Republic"
    724 = "Spain"
    752 = "Sweden"
    840 = "United States"
    926 = "England (UK)"
    928 = "Northern Ireland (UK)"
    956 = "Flanders (Belgium)"
    1241 = "Canada (English)"
    1242 = "Canada (French)"
    8261 = "England/N. Ireland (UK)"
  ;
  VALUE $CNTRY_E
    AUS = "Australia"
    AUT = "Austria"
    BFL = "Flanders (Belgium)"
    CAN = "Canada"
    CEN = "Canada (English)"
    CFR = "Canada (French)"
    CYP = "Cyprus"
    CZE = "Czech Republic"
    DEU = "Germany"
    DNK = "Denmark"
    ENG = "England (UK)"
    ESP = "Spain"
    EST = "Estonia"
    FIN = "Finland"
    FRA = "France"
    IRL = "Ireland"
    ITA = "Italy"
    JPN = "Japan"
    KOR = "Korea"
    NIR = "Northern Ireland (UK)"
    NLD = "Netherlands"
    NOR = "Norway"
    POL = "Poland"
    RUS = "Russian Federation"
    SVK = "Slovak Republic"
    SWE = "Sweden"
    UK1 = "England/N. Ireland (UK)"
    USA = "United States"
  ;
  VALUE CNT_BRTHUS_C
    1 = "Native"
    2 = "foreign born"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE COMPUTEREXPERIENCEUSP
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE CORESTAGE1_PASS
    1 = "Passed"
    .N = "Not stated or inferred"
    29 = "Not passed"
  ;
  VALUE CORESTAGE2_PASS
    1 = "Passed"
    .N = "Not stated or inferred"
    29 = "Not passed"
  ;
  VALUE CTRYRGN
    1 = "Arab States"
    2 = "South and West Asia"
    3 = "Latin America and the Caribbean"
    4 = "Sub-Saharan Africa"
    5 = "East Asia and the Pacific (poorer countries)"
    6 = "Central Asia"
    7 = "East Asia and the Pacific (richer countries)"
    8 = "Central and Eastern Europe"
    9 = "North America and Western Europe"
    .N = "Not stated or inferred"
  ;
  VALUE C_Q07USP
    1 = "Full-time employed (self-employed, employee)"
    2 = "Part-time employed (self-employed, employee)"
    3 = "Unemployed"
    4 = "Pupil, student"
    5 = "Apprentice, internship"
    6 = "In retirement or early retirement"
    7 = "Permanently disabled"
    8 = "In compulsory military or community service"
    9 = "Fulfilling domestic tasks or looking after children/family"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Other"
  ;
  VALUE C_Q08AUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE C_Q09_C
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE C_Q10AUSP_C
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE D302C02A
    .N = "Not reached/Not attempted"
  ;
  VALUE D302C02F
    .N = "Not reached/Not attempted"
  ;
  VALUE D302C02S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D302C02T
    .N = "Not reached/Not attempted"
  ;
  VALUE D304710A
    .N = "Not reached/Not attempted"
  ;
  VALUE D304710F
    .N = "Not reached/Not attempted"
  ;
  VALUE D304710S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D304710T
    .N = "Not reached/Not attempted"
  ;
  VALUE D304711A
    .N = "Not reached/Not attempted"
  ;
  VALUE D304711F
    .N = "Not reached/Not attempted"
  ;
  VALUE D304711S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D304711T
    .N = "Not reached/Not attempted"
  ;
  VALUE D306110A
    .N = "Not reached/Not attempted"
  ;
  VALUE D306110F
    .N = "Not reached/Not attempted"
  ;
  VALUE D306110S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D306110T
    .N = "Not reached/Not attempted"
  ;
  VALUE D306111A
    .N = "Not reached/Not attempted"
  ;
  VALUE D306111F
    .N = "Not reached/Not attempted"
  ;
  VALUE D306111S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D306111T
    .N = "Not reached/Not attempted"
  ;
  VALUE D307401A
    .N = "Not reached/Not attempted"
  ;
  VALUE D307401F
    .N = "Not reached/Not attempted"
  ;
  VALUE D307401S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D307401T
    .N = "Not reached/Not attempted"
  ;
  VALUE D307402A
    .N = "Not reached/Not attempted"
  ;
  VALUE D307402F
    .N = "Not reached/Not attempted"
  ;
  VALUE D307402S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D307402T
    .N = "Not reached/Not attempted"
  ;
  VALUE D311701A
    .N = "Not reached/Not attempted"
  ;
  VALUE D311701F
    .N = "Not reached/Not attempted"
  ;
  VALUE D311701S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D311701T
    .N = "Not reached/Not attempted"
  ;
  VALUE D315512A
    .N = "Not reached/Not attempted"
  ;
  VALUE D315512F
    .N = "Not reached/Not attempted"
  ;
  VALUE D315512S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE D315512T
    .N = "Not reached/Not attempted"
  ;
  VALUE DISP_BQ
    0 = "Not assigned"
    1 = "Complete"
    3 = "Partial complete/breakoff"
    4 = "Refusal - Sample person"
    5 = "Refusal - Other"
    7 = "Language problem"
    8 = "Reading and writing difficulty"
    9 = "Learning/mental disability"
    .N = "Not stated or inferred"
    12 = "Hearing impairment"
    13 = "Blindness/visual impairment"
    14 = "Speech impairment"
    15 = "Physical disability"
    16 = "Other disability"
    17 = "Other (unspecified), such as sickness or unusual circumstances"
    18 = "Death"
    21 = "Maximum number of calls"
    24 = "Temporarily absent/unavailable during field period"
    25 = "Ineligible"
    27 = "Duplication - already interviewed"
    90 = "Technical problem"
  ;
  VALUE DISP_CIBQ
    0 = "Not assigned"
    1 = "Complete"
    3 = "Partial complete/breakoff"
    4 = "Refusal - Sample person"
    5 = "Refusal - Other"
    7 = "Language problem"
    8 = "Reading and writing difficulty"
    9 = "Learning/mental disability"
    .N = "Not stated or inferred"
    12 = "Hearing impairment"
    13 = "Blindness/visual impairment"
    14 = "Speech impairment"
    15 = "Physical disability"
    16 = "Other disability"
    17 = "Other (unspecified), such as sickness or unusual circumstances"
    18 = "Death"
    21 = "Maximum number of calls"
    24 = "Temporarily absent/unavailable during field period"
    25 = "Ineligible"
    27 = "Duplication - already interviewed"
    90 = "Technical problem"
  ;
  VALUE D_Q10USP_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE D_Q10USP_C
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E318001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E318001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E318001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E318001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E318003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E318003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E318003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E318003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E320001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E320001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E320001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E320001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E320003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E320003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E320003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E320003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E320004A
    .N = "Not reached/Not attempted"
  ;
  VALUE E320004F
    .N = "Not reached/Not attempted"
  ;
  VALUE E320004S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E320004T
    .N = "Not reached/Not attempted"
  ;
  VALUE E321001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E321001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E321001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E321001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E321002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E321002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E321002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E321002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E322001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E322001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E322001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E322001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E322002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E322002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E322002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E322002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E322003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E322003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E322003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E322003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E322004A
    .N = "Not reached/Not attempted"
  ;
  VALUE E322004F
    .N = "Not reached/Not attempted"
  ;
  VALUE E322004S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E322004T
    .N = "Not reached/Not attempted"
  ;
  VALUE E322005A
    .N = "Not reached/Not attempted"
  ;
  VALUE E322005F
    .N = "Not reached/Not attempted"
  ;
  VALUE E322005S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E322005T
    .N = "Not reached/Not attempted"
  ;
  VALUE E323002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E323002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E323002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E323002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E323003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E323003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E323003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E323003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E323004A
    .N = "Not reached/Not attempted"
  ;
  VALUE E323004F
    .N = "Not reached/Not attempted"
  ;
  VALUE E323004S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E323004T
    .N = "Not reached/Not attempted"
  ;
  VALUE E323005A
    .N = "Not reached/Not attempted"
  ;
  VALUE E323005F
    .N = "Not reached/Not attempted"
  ;
  VALUE E323005S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E323005T
    .N = "Not reached/Not attempted"
  ;
  VALUE E327001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E327001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E327001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E327001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E327002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E327002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E327002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E327002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E327003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E327003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E327003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E327003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E327004A
    .N = "Not reached/Not attempted"
  ;
  VALUE E327004F
    .N = "Not reached/Not attempted"
  ;
  VALUE E327004S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E327004T
    .N = "Not reached/Not attempted"
  ;
  VALUE E329002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E329002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E329002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E329002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E329003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E329003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E329003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E329003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E632001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E632001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E632001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E632001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E632002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E632002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E632002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E632002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E634001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E634001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E634001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E634001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E634002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E634002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E634002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E634002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E635001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E635001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E635001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E635001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E636001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E636001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E636001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E636001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E641001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E641001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E641001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E641001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E644002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E644002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E644002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E644002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E645001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E645001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E645001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E645001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E646002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E646002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E646002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E646002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E650001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E650001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E650001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E650001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E651002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E651002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E651002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E651002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E655001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E655001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E655001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E655001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E657001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E657001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E657001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E657001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E660003A
    .N = "Not reached/Not attempted"
  ;
  VALUE E660003F
    .N = "Not reached/Not attempted"
  ;
  VALUE E660003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E660003T
    .N = "Not reached/Not attempted"
  ;
  VALUE E660004A
    .N = "Not reached/Not attempted"
  ;
  VALUE E660004F
    .N = "Not reached/Not attempted"
  ;
  VALUE E660004S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E660004T
    .N = "Not reached/Not attempted"
  ;
  VALUE E661001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E661001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E661001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E661001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E661002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E661002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E661002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E661002T
    .N = "Not reached/Not attempted"
  ;
  VALUE E664001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E664001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E664001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E664001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E665001A
    .N = "Not reached/Not attempted"
  ;
  VALUE E665001F
    .N = "Not reached/Not attempted"
  ;
  VALUE E665001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E665001T
    .N = "Not reached/Not attempted"
  ;
  VALUE E665002A
    .N = "Not reached/Not attempted"
  ;
  VALUE E665002F
    .N = "Not reached/Not attempted"
  ;
  VALUE E665002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE E665002T
    .N = "Not reached/Not attempted"
  ;
  VALUE EDCAT6_
    1 = "Lower secondary or less (ISCED 1,2, 3C short or less)"
    2 = "Upper secondary (ISCED 3A-B, C long)"
    3 = "Post-secondary, non-tertiary (ISCED 4A-B-C)"
    4 = "Tertiary - professional degree (ISCED 5B)"
    5 = "Tertiary - bachelor degree (ISCED 5A)"
    6 = "Tertiary - master/research degree (ISCED 5A/6)"
    7 = "Tertiary - bachelor/master/research degree (ISCED 5A/6)"
    .N = "Not stated or inferred"
  ;
  VALUE EDCAT7_
    1 = "Primary or less (ISCED 1 or less)"
    2 = "Lower secondary (ISCED 2, ISCED 3C short)"
    3 = "Upper secondary (ISCED 3A-B, C long)"
    4 = "Post-secondary, non-tertiary (ISCED 4A-B-C)"
    5 = "Tertiary - professional degree (ISCED 5B)"
    6 = "Tertiary - bachelor degree (ISCED 5A)"
    7 = "Tertiary - master/research degree (ISCED 5A/6)"
    8 = "Tertiary - bachelor/master/research degree (ISCED 5A/6)"
    .N = "Not stated or inferred"
  ;
  VALUE EDCAT8_
    1 = "Primary or less (ISCED 1 or less)"
    2 = "Lower secondary (ISCED 2, ISCED 3C short)"
    3 = "Upper secondary (ISCED 3A-B, C long)"
    4 = "Post-secondary, non-tertiary (ISCED 4A-B-C)"
    5 = "Tertiary - professional degree (ISCED 5B)"
    6 = "Tertiary - bachelor degree (ISCED 5A)"
    7 = "Tertiary - master degree (ISCED 5A)"
    8 = "Tertiary - research degree (ISCED 6)"
    9 = "Tertiary - bachelor/master/research degree (ISCED 5A/6)"
    .N = "Not stated or inferred"
  ;
  VALUE EDLEVEL3_
    1 = "Low"
    2 = "Medium"
    3 = "High"
    .N = "Not stated or inferred"
  ;
  VALUE E_Q03USP_
    1 = "The private sector (for example a company)"
    2 = "The public sector (for example the local government or a state school)"
    3 = "A non-profit organisation (for example a charity, professional association or religious organisation)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q03US_P
    1 = "The private sector (for example a company)"
    2 = "The public sector (for example the local government or a state school)"
    3 = "A non-profit organisation (for example a charity, professional association or religious organisation)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q04USP_
    1 = "Employee"
    2 = "Self-employed"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q05A1USP_C
    1 = "Aged 19 or younger"
    2 = "Aged 20-24"
    3 = "Aged 25-29"
    4 = "Aged 30-34"
    5 = "Aged 35-39"
    6 = "Aged 40-44"
    7 = "Aged 45-49"
    8 = "Aged 50-54"
    9 = "Aged 55 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q05A2USP_C
    1 = "1959 - 1985"
    2 = "1986 - 1995"
    3 = "1996 - 2005"
    4 = "2006 - 2012"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q05B1USP_C
    1 = "Aged 19 or younger"
    2 = "Aged 20-24"
    3 = "Aged 25-29"
    4 = "Aged 30-34"
    5 = "Aged 35-39"
    6 = "Aged 40-44"
    7 = "Aged 45-49"
    8 = "Aged 50-54"
    9 = "Aged 55 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q05B2USP_C
    1 = "1958 - 2005"
    2 = "2006 - 2012"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q06USP_
    1 = "1 to 10 people"
    2 = "11 to 50 people"
    3 = "51 to 250 people"
    4 = "251 to 1000 people"
    5 = "More than 1000 people"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q08USP_C
    1 = "An indefinite contract"
    2 = "A fixed term contract"
    3 = "A temporary employment agency contract"
    4 = "No contract"
    5 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q09USP_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q09USP_C
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE E_Q10USP
    1 = "Dismissed"
    2 = "Job eliminated"
    3 = "Temporary job ended"
    4 = "Resigned"
    5 = "Gave up for health reasons"
    6 = "Early retirement"
    7 = "Retired"
    8 = "Gave up for family responsibilities"
    9 = "Gave up to study"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Other"
    11 = "Arrested"
    12 = "Incarcerated"
  ;
  VALUE FAET12JR
    0 = "Did not participate in formal AET for JR reasons"
    1 = "Participated in formal AET for JR reasons"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FAET12NJR
    0 = "Did not participate in FE for NJR reasons"
    1 = "Participated in FE for NJR reasons"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FIRLGRGNUS_C
    1 = "North America and Western Europe"
    2 = "other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE FNFAET12JR
    0 = "Did not participate in formal or non-formal AET for JR reasons"
    1 = "Participated in formal or non-formal AET for JR reasons"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FNFAET12NJR
    0 = "Did not participate in formal or non-formal AET for non JR reasons"
    1 = "Participated in formal or non-formal AET for non JR reasons"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FNFAET12_
    0 = "Did not participate in formal or non-formal AET"
    1 = "Participated in formal and/or non-formal AET"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FNFE12JR
    0 = "Did not participate in FE or NFE for JR reasons"
    1 = "Participated in FE or NFE for JR reasons"
    .A = "Student in regular cycle of studies"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE FORBILANG
    0 = "Monolingual or at least bilingual including test language"
    1 = "At least bilingual not including test language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE FORBORNLANG
    0 = "Either native-born or native-language"
    1 = "Foreign-born and foreign-language"
    .N = "Not stated or inferred"
  ;
  VALUE F_Q01BUSP
    1 = "None of the time"
    2 = "Up to a quarter of the time"
    3 = "Up to half of the time"
    4 = "More than half of the time"
    5 = "All of the time"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q02AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q02BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q02CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q02DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q02EUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q03AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q03BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q03CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q04AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q04BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q05AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q05BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q06BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q06CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q07AUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE F_Q07BUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE GENDER_R
    1 = "Male"
    2 = "Female"
    .N = "Not stated or inferred"
  ;
  VALUE G_Q01AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01EUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q01HUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q02AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q02BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q02CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q02DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q03HUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q04USP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05EUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q05HUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q06USP
    1 = "Straightforward"
    2 = "Moderate"
    3 = "Complex"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q07USP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE G_Q08USP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE HOMLANG
    0 = "Test language not same as home language"
    1 = "Test language same as home language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE HOMLGRGNUS_C
    1 = "North America and Western Europe"
    2 = "other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01EUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q01HUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q02AUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q02BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q02CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q02DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03BUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03CUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03DUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q03HUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q04AUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q04BUSP
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q05EUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q05FUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE H_Q05GUSP
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE ICTWORK_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE IMGEN
    1 = "1st generation immigrants"
    2 = "2nd generation immigrants"
    3 = "Non 1st or 2nd generation immigrants"
    .A = "Non-immigrant and one foreign-born parent"
    .N = "Not stated or inferred"
  ;
  VALUE IMPAR
    1 = "Both parents foreign-born"
    2 = "One parent foreign-born"
    3 = "Both parents native-born"
    .N = "Not stated or inferred"
  ;
  VALUE IMYRCAT
    1 = "In host country 5 or fewer years"
    2 = "In host country more than 5 years"
    3 = "Non-immigrants"
    .N = "Not stated or inferred"
  ;
  VALUE IMYRS_C
    1 = "0-5 years"
    2 = "6-10 years"
    3 = "11-15 years"
    4 = "more than 15 years"
    .A = "Native born"
    .N = "Not stated or inferred"
  ;
  VALUE INFLUENCE_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE INPIAAC
    0 = "Out-of-international-sample"
    1 = "In-international-sample"
  ;
  VALUE INTLFLAG
    0 = "Other"
    1 = "Household sample 16 - 65 years old"
  ;
  VALUE $ISCO08_CUSP_C
    0 = "Armed forces occupations"
    01 = "Commissioned armed forces officers"
    011 = "Commissioned armed forces officers"
    0110 = "Commissioned armed forces officers"
    02 = "Non-commissioned armed forces officers"
    021 = "Non-commissioned armed forces officers"
    0210 = "Non-commissioned armed forces officers"
    03 = "Armed forces occupations, other ranks"
    031 = "Armed forces occupations, other ranks"
    0310 = "Armed forces occupations, other ranks"
    1 = "Managers"
    11 = "Chief executives, senior officials and legislators"
    111 = "Legislators and senior officials"
    1111 = "Legislators"
    1112 = "Senior government officials"
    1113 = "Traditional chiefs and heads of village"
    1114 = "Senior officials of special-interest organizations"
    112 = "Managing directors and chief executives"
    1120 = "Managing directors and chief executives"
    12 = "Administrative and commercial managers"
    121 = "Business services and administration managers"
    1211 = "Finance managers"
    1212 = "Human resource managers"
    1213 = "Policy and planning managers"
    1219 = "Business services and administration managers not elsewhere classified"
    122 = "Sales, marketing and development managers"
    1221 = "Sales and marketing managers"
    1222 = "Advertising and public relations managers"
    1223 = "Research and development managers"
    13 = "Production and specialised services managers"
    131 = "Production managers in agriculture, forestry and fisheries"
    1311 = "Agricultural and forestry production managers"
    1312 = "Aquaculture and fisheries production managers"
    132 = "Manufacturing, mining, construction, and distribution managers"
    1321 = "Manufacturing managers"
    1322 = "Mining managers"
    1323 = "Construction managers"
    1324 = "Supply, distribution and related managers"
    133 = "Information and communications technology service managers"
    1330 = "Information and communications technology service managers"
    134 = "Professional services managers"
    1341 = "Child care services managers"
    1342 = "Health services managers"
    1343 = "Aged care services managers"
    1344 = "Social welfare managers"
    1345 = "Education managers"
    1346 = "Financial and insurance services branch managers"
    1349 = "Professional services managers not elsewhere classified"
    14 = "Hospitality, retail and other services managers"
    141 = "Hotel and restaurant managers"
    1411 = "Hotel managers"
    1412 = "Restaurant managers"
    142 = "Retail and wholesale trade managers"
    1420 = "Retail and wholesale trade managers"
    143 = "Other services managers"
    1431 = "Sports, recreation and cultural centre managers"
    1439 = "Services managers not elsewhere classified"
    2 = "Professionals"
    21 = "Science and engineering professionals"
    211 = "Physical and earth science professionals"
    2111 = "Physicists and astronomers"
    2112 = "Meteorologists"
    2113 = "Chemists"
    2114 = "Geologists and geophysicists"
    212 = "Mathematicians, actuaries and statisticians"
    2120 = "Mathematicians, actuaries and statisticians"
    213 = "Life science professionals"
    2131 = "Biologists, botanists, zoologists and related professionals"
    2132 = "Farming, forestry and fisheries advisers"
    2133 = "Environmental protection professionals"
    214 = "Engineering professionals (excluding electrotechnology)"
    2141 = "Industrial and production engineers"
    2142 = "Civil engineers"
    2143 = "Environmental engineers"
    2144 = "Mechanical engineers"
    2145 = "Chemical engineers"
    2146 = "Mining engineers, metallurgists and related professionals"
    2149 = "Engineering professionals not elsewhere classified"
    215 = "Electrotechnology engineers"
    2151 = "Electrical engineers"
    2152 = "Electronics engineers"
    2153 = "Telecommunications engineers"
    216 = "Architects, planners, surveyors and designers"
    2161 = "Building architects"
    2162 = "Landscape architects"
    2163 = "Product and garment designers"
    2164 = "Town and traffic planners"
    2165 = "Cartographers and surveyors"
    2166 = "Graphic and multimedia designers"
    22 = "Health professionals"
    221 = "Medical doctors"
    2211 = "Generalist medical practitioners"
    2212 = "Specialist medical practitioners"
    222 = "Nursing and midwifery professionals"
    2221 = "Nursing professionals"
    2222 = "Midwifery professionals"
    223 = "Traditional and complementary medicine professionals"
    2230 = "Traditional and complementary medicine professionals"
    224 = "Paramedical practitioners"
    2240 = "Paramedical practitioners"
    225 = "Veterinarians"
    2250 = "Veterinarians"
    226 = "Other health professionals"
    2261 = "Dentists"
    2262 = "Pharmacists"
    2263 = "Environmental and occupational health and hygiene professionals"
    2264 = "Physiotherapists"
    2265 = "Dieticians and nutritionists"
    2266 = "Audiologists and speech therapists"
    2267 = "Optometrists and ophthalmic opticians"
    2269 = "Health professionals not elsewhere classified"
    23 = "Teaching professionals"
    231 = "University and higher education teachers"
    2310 = "University and higher education teachers"
    232 = "Vocational education teachers"
    2320 = "Vocational education teachers"
    233 = "Secondary education teachers"
    2330 = "Secondary education teachers"
    234 = "Primary school and early childhood teachers"
    2341 = "Primary school teachers"
    2342 = "Early childhood educators"
    235 = "Other teaching professionals"
    2351 = "Education methods specialists"
    2352 = "Special needs teachers"
    2353 = "Other language teachers"
    2354 = "Other music teachers"
    2355 = "Other arts teachers"
    2356 = "Information technology trainers"
    2359 = "Teaching professionals not elsewhere classified"
    24 = "Business and administration professionals"
    241 = "Finance professionals"
    2411 = "Accountants"
    2412 = "Financial and investment advisers"
    2413 = "Financial analysts"
    242 = "Administration professionals"
    2421 = "Management and organization analysts"
    2422 = "Policy administration professionals"
    2423 = "Personnel and careers professionals"
    2424 = "Training and staff development professionals"
    243 = "Sales, marketing and public relations professionals"
    2431 = "Advertising and marketing professionals"
    2432 = "Public relations professionals"
    2433 = "Technical and medical sales professionals (excluding ICT)"
    2434 = "Information and communications technology sales professionals"
    25 = "Information and communications technology professionals"
    251 = "Software and applications developers and analysts"
    2511 = "Systems analysts"
    2512 = "Software developers"
    2513 = "Web and multimedia developers"
    2514 = "Applications programmers"
    2519 = "Software and applications developers and analysts not elsewhere classified"
    252 = "Database and network professionals"
    2521 = "Database designers and administrators"
    2522 = "Systems administrators"
    2523 = "Computer network professionals"
    2529 = "Database and network professionals not elsewhere classified"
    26 = "Legal, social and cultural professionals"
    261 = "Legal professionals"
    2611 = "Lawyers"
    2612 = "Judges"
    2619 = "Legal professionals not elsewhere classified"
    262 = "Librarians, archivists and curators"
    2621 = "Archivists and curators"
    2622 = "Librarians and related information professionals"
    263 = "Social and religious professionals"
    2631 = "Economists"
    2632 = "Sociologists, anthropologists and related professionals"
    2633 = "Philosophers, historians and political scientists"
    2634 = "Psychologists"
    2635 = "Social work and counselling professionals"
    2636 = "Religious professionals"
    264 = "Authors, journalists and linguists"
    2641 = "Authors and related writers"
    2642 = "Journalists"
    2643 = "Translators, interpreters and other linguists"
    265 = "Creative and performing artists"
    2651 = "Visual artists"
    2652 = "Musicians, singers and composers"
    2653 = "Dancers and choreographers"
    2654 = "Film, stage and related directors and producers"
    2655 = "Actors"
    2656 = "Announcers on radio, television and other media"
    2659 = "Creative and performing artists not elsewhere classified"
    3 = "Technicians and associate professionals"
    31 = "Science and engineering associate professionals"
    311 = "Physical and engineering science technicians"
    3111 = "Chemical and physical science technicians"
    3112 = "Civil engineering technicians"
    3113 = "Electrical engineering technicians"
    3114 = "Electronics engineering technicians"
    3115 = "Mechanical engineering technicians"
    3116 = "Chemical engineering technicians"
    3117 = "Mining and metallurgical technicians"
    3118 = "Draughtspersons"
    3119 = "Physical and engineering science technicians not elsewhere classified"
    312 = "Mining, manufacturing and construction supervisors"
    3121 = "Mining supervisors"
    3122 = "Manufacturing supervisors"
    3123 = "Construction supervisors"
    313 = "Process control technicians"
    3131 = "Power production plant operators"
    3132 = "Incinerator and water treatment plant operators"
    3133 = "Chemical processing plant controllers"
    3134 = "Petroleum and natural gas refining plant operators"
    3135 = "Metal production process controllers"
    3139 = "Process control technicians not elsewhere classified"
    314 = "Life science technicians and related associate professionals"
    3141 = "Life science technicians (excluding medical)"
    3142 = "Agricultural technicians"
    3143 = "Forestry technicians"
    315 = "Ship and aircraft controllers and technicians"
    3151 = "Ships' engineers"
    3152 = "Ships' deck officers and pilots"
    3153 = "Aircraft pilots and related associate professionals"
    3154 = "Air traffic controllers"
    3155 = "Air traffic safety electronics technicians"
    32 = "Health associate professionals"
    321 = "Medical and pharmaceutical technicians"
    3211 = "Medical imaging and therapeutic equipment technicians"
    3212 = "Medical and pathology laboratory technicians"
    3213 = "Pharmaceutical technicians and assistants"
    3214 = "Medical and dental prosthetic technicians"
    322 = "Nursing and midwifery associate professionals"
    3221 = "Nursing associate professionals"
    3222 = "Midwifery associate professionals"
    323 = "Traditional and complementary medicine associate professionals"
    3230 = "Traditional and complementary medicine associate professionals"
    324 = "Veterinary technicians and assistants"
    3240 = "Veterinary technicians and assistants"
    325 = "Other health associate professionals"
    3251 = "Dental assistants and therapists"
    3252 = "Medical records and health information technicians"
    3253 = "Community health workers"
    3254 = "Dispensing opticians"
    3255 = "Physiotherapy technicians and assistants"
    3256 = "Medical assistants"
    3257 = "Environmental and occupational health inspectors and associates"
    3258 = "Ambulance workers"
    3259 = "Health associate professionals not elsewhere classified"
    33 = "Business and administration associate professionals"
    331 = "Financial and mathematical associate professionals"
    3311 = "Securities and finance dealers and brokers"
    3312 = "Credit and loans officers"
    3313 = "Accounting associate professionals"
    3314 = "Statistical, mathematical and related associate professionals"
    3315 = "Valuers and loss assessors"
    332 = "Sales and purchasing agents and brokers"
    3321 = "Insurance representatives"
    3322 = "Commercial sales representatives"
    3323 = "Buyers"
    3324 = "Trade brokers"
    333 = "Business services agents"
    3331 = "Clearing and forwarding agents"
    3332 = "Conference and event planners"
    3333 = "Employment agents and contractors"
    3334 = "Real estate agents and property managers"
    3339 = "Business services agents not elsewhere classified"
    334 = "Administrative and specialised secretaries"
    3341 = "Office supervisors"
    3342 = "Legal secretaries"
    3343 = "Administrative and executive secretaries"
    3344 = "Medical secretaries"
    335 = "Regulatory government associate professionals"
    3351 = "Customs and border inspectors"
    3352 = "Government tax and excise officials"
    3353 = "Government social benefits officials"
    3354 = "Government licensing officials"
    3355 = "Police inspectors and detectives"
    3359 = "Regulatory government associate professionals not elsewhere classified"
    34 = "Legal, social, cultural and related associate professionals"
    341 = "Legal, social and religious associate professionals"
    3411 = "Police inspectors and detectives"
    3412 = "Social work associate professionals"
    3413 = "Religious associate professionals"
    342 = "Sports and fitness workers"
    3421 = "Athletes and sports players"
    3422 = "Sports coaches, instructors and officials"
    3423 = "Fitness and recreation instructors and program leaders"
    343 = "Artistic, cultural and culinary associate professionals"
    3431 = "Photographers"
    3432 = "Interior designers and decorators"
    3433 = "Gallery, museum and library technicians"
    3434 = "Chefs"
    3435 = "Other artistic and cultural associate professionals"
    35 = "Information and communications technicians"
    351 = "Information and communications technology operations and user support technicians"
    3511 = "Information and communications technology operations technicians"
    3512 = "Information and communications technology user support technicians"
    3513 = "Computer network and systems technicians"
    3514 = "Web technicians"
    352 = "Telecommunications and broadcasting technicians"
    3521 = "Broadcasting and audio-visual technicians"
    3522 = "Telecommunications engineering technicians"
    4 = "Clerical support workers"
    41 = "General and keyboard clerks"
    411 = "General office clerks"
    4110 = "General office clerks"
    412 = "Secretaries (general)"
    4120 = "Secretaries (general)"
    413 = "Keyboard operators"
    4131 = "Typists and word processing operators"
    4132 = "Data entry clerks"
    42 = "Customer services clerks"
    421 = "Tellers, money collectors and related clerks"
    4211 = "Bank tellers and related clerks"
    4212 = "Bookmakers, croupiers and related gaming workers"
    4213 = "Pawnbrokers and money-lenders"
    4214 = "Debt-collectors and related workers"
    422 = "Client information workers"
    4221 = "Travel consultants and clerks"
    4222 = "Contact centre information clerks"
    4223 = "Telephone switchboard operators"
    4224 = "Hotel receptionists"
    4225 = "Enquiry clerks"
    4226 = "Receptionists (general)"
    4227 = "Survey and market research interviewers"
    4229 = "Client information workers not elsewhere classified"
    43 = "Numerical and material recording clerks"
    431 = "Numerical clerks"
    4311 = "Accounting and bookkeeping clerks"
    4312 = "Statistical, finance and insurance clerks"
    4313 = "Payroll clerks"
    432 = "Material-recording and transport clerks"
    4321 = "Stock clerks"
    4322 = "Production clerks"
    4323 = "Transport clerks"
    44 = "Other clerical support workers"
    441 = "Other clerical support workers"
    4411 = "Library clerks"
    4412 = "Mail carriers and sorting clerks"
    4413 = "Coding, proof-reading and related clerks"
    4414 = "Scribes and related workers"
    4415 = "Filing and copying clerks"
    4416 = "Personnel clerks"
    4419 = "Clerical support workers not elsewhere classified"
    5 = "Service and sales workers"
    51 = "Personal service workers"
    511 = "Travel attendants, conductors and guides"
    5111 = "Travel attendants and travel stewards"
    5112 = "Transport conductors"
    5113 = "Travel guides"
    512 = "Cooks"
    5120 = "Cooks"
    513 = "Waiters and bartenders"
    5131 = "Waiters"
    5132 = "Bartenders"
    514 = "Hairdressers, beauticians and related workers"
    5141 = "Hairdressers"
    5142 = "Beauticians and related workers"
    515 = "Building and housekeeping supervisors"
    5151 = "Cleaning and housekeeping supervisors in offices, hotels and other establishments"
    5152 = "Domestic housekeepers"
    5153 = "Building caretakers"
    516 = "Other personal services workers"
    5161 = "Astrologers, fortune-tellers and related workers"
    5162 = "Companions and valets"
    5163 = "Undertakers and embalmers"
    5164 = "Pet groomers and animal care workers"
    5165 = "Driving instructors"
    5169 = "Personal services workers not elsewhere classified"
    52 = "Sales workers"
    521 = "Street and market salespersons"
    5211 = "Stall and market salespersons"
    5212 = "Street food salespersons"
    522 = "Shop salespersons"
    5221 = "Shop keepers"
    5222 = "Shop supervisors"
    5223 = "Shop sales assistants"
    523 = "Cashiers and ticket clerks"
    5230 = "Cashiers and ticket clerks"
    524 = "Other sales workers"
    5241 = "Fashion and other models"
    5242 = "Sales demonstrators"
    5243 = "Door to door salespersons"
    5244 = "Contact centre salespersons"
    5245 = "Service station attendants"
    5246 = "Food service counter attendants"
    5249 = "Sales workers not elsewhere classified"
    53 = "Personal care workers"
    531 = "Child care workers and teachers' aides"
    5311 = "Child care workers"
    5312 = "Teachers' aides"
    532 = "Personal care workers in health services"
    5321 = "Health care assistants"
    5322 = "Home-based personal care workers"
    5329 = "Personal care workers in health services not elsewhere classified"
    54 = "Protective services workers"
    541 = "Protective services workers"
    5411 = "Fire-fighters"
    5412 = "Police officers"
    5413 = "Prison guards"
    5414 = "Security guards"
    5419 = "Protective services workers not elsewhere classified"
    6 = "Skilled agricultural, forestry and fishery workers"
    61 = "Market-oriented skilled agricultural workers"
    611 = "Market gardeners and crop growers"
    6111 = "Field crop and vegetable growers"
    6112 = "Tree and shrub crop growers"
    6113 = "Gardeners, horticultural and nursery growers"
    6114 = "Mixed crop growers"
    612 = "Animal producers"
    6121 = "Livestock and dairy producers"
    6122 = "Poultry producers"
    6123 = "Apiarists and sericulturists"
    6129 = "Animal producers not elsewhere classified"
    613 = "Mixed crop and animal producers"
    6130 = "Mixed crop and animal producers"
    62 = "Market-oriented skilled forestry, fishery and hunting workers"
    621 = "Forestry and related workers"
    6210 = "Forestry and related workers"
    622 = "Fishery workers, hunters and trappers"
    6221 = "Aquaculture workers"
    6222 = "Inland and coastal waters fishery workers"
    6223 = "Deep-sea fishery workers"
    6224 = "Hunters and trappers"
    63 = "Subsistence farmers, fishers, hunters and gatherers"
    631 = "Subsistence crop farmers"
    6310 = "Subsistence crop farmers"
    632 = "Subsistence livestock farmers"
    6320 = "Subsistence livestock farmers"
    633 = "Subsistence mixed crop and livestock farmers"
    6330 = "Subsistence mixed crop and livestock farmers"
    634 = "Subsistence fishers, hunters, trappers and gatherers"
    6340 = "Subsistence fishers, hunters, trappers and gatherers"
    7 = "Craft and related trades workers"
    71 = "Building and related trades workers, excluding electricians"
    711 = "Building frame and related trades workers"
    7111 = "House builders"
    7112 = "Bricklayers and related workers"
    7113 = "Stonemasons, stone cutters, splitters and carvers"
    7114 = "Concrete placers, concrete finishers and related workers"
    7115 = "Carpenters and joiners"
    7119 = "Building frame and related trades workers not elsewhere classified"
    712 = "Building finishers and related trades workers"
    7121 = "Roofers"
    7122 = "Floor layers and tile setters"
    7123 = "Plasterers"
    7124 = "Insulation workers"
    7125 = "Glaziers"
    7126 = "Plumbers and pipe fitters"
    7127 = "Air conditioning and refrigeration mechanics"
    713 = "Painters, building structure cleaners and related trades workers"
    7131 = "Painters and related workers"
    7132 = "Spray painters and varnishers"
    7133 = "Building structure cleaners"
    72 = "Metal, machinery and related trades workers"
    721 = "Sheet and structural metal workers, moulders and welders, and related workers"
    7211 = "Metal moulders and coremakers"
    7212 = "Welders and flamecutters"
    7213 = "Sheet-metal workers"
    7214 = "Structural-metal preparers and erectors"
    7215 = "Riggers and cable splicers"
    722 = "Blacksmiths, toolmakers and related trades workers"
    7221 = "Blacksmiths, hammersmiths and forging press workers"
    7222 = "Toolmakers and related workers"
    7223 = "Metal working machine tool setters and operators"
    7224 = "Metal polishers, wheel grinders and tool sharpeners"
    723 = "Machinery mechanics and repairers"
    7231 = "Motor vehicle mechanics and repairers"
    7232 = "Aircraft engine mechanics and repairers"
    7233 = "Agricultural and industrial machinery mechanics and repairers"
    7234 = "Bicycle and related repairers"
    73 = "Handicraft and printing workers"
    731 = "Handicraft workers"
    7311 = "Precision-instrument makers and repairers"
    7312 = "Musical instrument makers and tuners"
    7313 = "Jewellery and precious-metal workers"
    7314 = "Potters and related workers"
    7315 = "Glass makers, cutters, grinders and finishers"
    7316 = "Sign writers, decorative painters, engravers and etchers"
    7317 = "Handicraft workers in wood, basketry and related materials"
    7318 = "Handicraft workers in textile, leather and related materials"
    7319 = "Handicraft workers not elsewhere classified"
    732 = "Printing trades workers"
    7321 = "Pre-press technicians"
    7322 = "Printers"
    7323 = "Print finishing and binding workers"
    74 = "Electrical and electronic trades workers"
    741 = "Electrical equipment installers and repairers"
    7411 = "Building and related electricians"
    7412 = "Electrical mechanics and fitters"
    7413 = "Electrical line installers and repairers"
    742 = "Electronics and telecommunications installers and repairers"
    7421 = "Electronics mechanics and servicers"
    7422 = "Information and communications technology installers and servicers"
    75 = "Food processing, wood working, garment and other craft and related trades workers"
    751 = "Food processing and related trades workers"
    7511 = "Butchers, fishmongers and related food preparers"
    7512 = "Bakers, pastry-cooks and confectionery makers"
    7513 = "Dairy-products makers"
    7514 = "Fruit, vegetable and related preservers"
    7515 = "Food and beverage tasters and graders"
    7516 = "Tobacco preparers and tobacco products makers"
    752 = "Wood treaters, cabinet-makers and related trades workers"
    7521 = "Wood treaters"
    7522 = "Cabinet-makers and related workers"
    7523 = "Woodworking-machine tool setters and operators"
    753 = "Garment and related trades workers"
    7531 = "Tailors, dressmakers, furriers and hatters"
    7532 = "Garment and related pattern-makers and cutters"
    7533 = "Sewing, embroidery and related workers"
    7534 = "Upholsterers and related workers"
    7535 = "Pelt dressers, tanners and fellmongers"
    7536 = "Shoemakers and related workers"
    754 = "Other craft and related workers"
    7541 = "Underwater divers"
    7542 = "Shotfirers and blasters"
    7543 = "Product graders and testers (excluding foods and beverages)"
    7544 = "Fumigators and other pest and weed controllers"
    7549 = "Craft and related workers not elsewhere classified"
    8 = "Plant and machine operators, and assemblers"
    81 = "Stationary plant and machine operators"
    811 = "Mining and mineral processing plant operators"
    8111 = "Miners and quarriers"
    8112 = "Mineral and stone processing plant operators"
    8113 = "Well drillers and borers and related workers"
    8114 = "Cement, stone and other mineral products machine operators"
    812 = "Metal processing and finishing plant operators"
    8121 = "Metal processing plant operators"
    8122 = "Metal finishing, plating and coating machine operators"
    813 = "Chemical and photographic products plant and machine operators"
    8131 = "Chemical products plant and machine operators"
    8132 = "Photographic products machine operators"
    814 = "Rubber, plastic and paper products machine operators"
    8141 = "Rubber products machine operators"
    8142 = "Plastic products machine operators"
    8143 = "Paper products machine operators"
    815 = "Textile, fur and leather products machine operators"
    8151 = "Fibre preparing, spinning and winding machine operators"
    8152 = "Weaving and knitting machine operators"
    8153 = "Sewing machine operators"
    8154 = "Bleaching, dyeing and fabric cleaning machine operators"
    8155 = "Fur and leather preparing machine operators"
    8156 = "Shoemaking and related machine operators"
    8157 = "Laundry machine operators"
    8159 = "Textile, fur and leather products machine operators not elsewhere classified"
    816 = "Food and related products machine operators"
    8160 = "Food and related products machine operators"
    817 = "Wood processing and papermaking plant operators"
    8171 = "Pulp and papermaking plant operators"
    8172 = "Wood processing plant operators"
    818 = "Other stationary plant and machine operators"
    8181 = "Glass and ceramics plant operators"
    8182 = "Steam engine and boiler operators"
    8183 = "Packing, bottling and labelling machine operators"
    8189 = "Stationary plant and machine operators not elsewhere classified"
    82 = "Assemblers"
    821 = "Assemblers"
    8211 = "Mechanical machinery assemblers"
    8212 = "Electrical and electronic equipment assemblers"
    8219 = "Assemblers not elsewhere classified"
    83 = "Drivers and mobile plant operators"
    831 = "Locomotive engine drivers and related workers"
    8311 = "Locomotive engine drivers"
    8312 = "Railway brake, signal and switch operators"
    832 = "Car, van and motorcycle drivers"
    8321 = "Motorcycle drivers"
    8322 = "Car, taxi and van drivers"
    833 = "Heavy truck and bus drivers"
    8331 = "Bus and tram drivers"
    8332 = "Heavy truck and lorry drivers"
    834 = "Mobile plant operators"
    8341 = "Mobile farm and forestry plant operators"
    8342 = "Earthmoving and related plant operators"
    8343 = "Crane, hoist and related plant operators"
    8344 = "Lifting truck operators"
    835 = "Ships' deck crews and related workers"
    8350 = "Ships' deck crews and related workers"
    9 = "Elementary occupations"
    91 = "Cleaners and helpers"
    911 = "Domestic, hotel and office cleaners and helpers"
    9111 = "Domestic cleaners and helpers"
    9112 = "Cleaners and helpers in offices, hotels and other establishments"
    912 = "Vehicle, window, laundry and other hand cleaning workers"
    9121 = "Hand launderers and pressers"
    9122 = "Vehicle cleaners"
    9123 = "Window cleaners"
    9129 = "Other cleaning workers"
    92 = "Agricultural, forestry and fishery labourers"
    921 = "Agricultural, forestry and fishery labourers"
    9211 = "Crop farm labourers"
    9212 = "Livestock farm labourers"
    9213 = "Mixed crop and livestock farm labourers"
    9214 = "Garden and horticultural labourers"
    9215 = "Forestry labourers"
    9216 = "Fishery and aquaculture labourers"
    93 = "Labourers in mining, construction, manufacturing and transport"
    931 = "Mining and construction labourers"
    9311 = "Mining and quarrying labourers"
    9312 = "Civil engineering labourers"
    9313 = "Building construction labourers"
    932 = "Manufacturing labourers"
    9321 = "Hand packers"
    9329 = "Manufacturing labourers not elsewhere classified"
    933 = "Transport and storage labourers"
    9331 = "Hand and pedal vehicle drivers"
    9332 = "Drivers of animal-drawn vehicles and machinery"
    9333 = "Freight handlers"
    9334 = "Shelf fillers"
    94 = "Food preparation assistants"
    941 = "Food preparation assistants"
    9411 = "Fast food preparers"
    9412 = "Kitchen helpers"
    95 = "Street and related sales and service workers"
    951 = "Street and related service workers"
    9510 = "Street and related service workers"
    952 = "Street vendors (excluding food)"
    9520 = "Street vendors (excluding food)"
    96 = "Refuse workers and other elementary workers"
    961 = "Refuse workers"
    9611 = "Garbage and recycling collectors"
    9612 = "Refuse sorters"
    9613 = "Sweepers and related labourers"
    962 = "Other elementary workers"
    9621 = "Messengers, package deliverers and luggage porters"
    9622 = "Odd job persons"
    9623 = "Meter readers and vending-machine collectors"
    9624 = "Water and firewood collectors"
    9629 = "Elementary workers not elsewhere classified"
    9996 = "Valid skip"
    9997 = "Don't know"
    9998 = "Refused"
    9999 = "Not stated or inferred"
  ;
  VALUE $ISCO08_LUSP_C
    0 = "Armed forces occupations"
    01 = "Commissioned armed forces officers"
    011 = "Commissioned armed forces officers"
    0110 = "Commissioned armed forces officers"
    02 = "Non-commissioned armed forces officers"
    021 = "Non-commissioned armed forces officers"
    0210 = "Non-commissioned armed forces officers"
    03 = "Armed forces occupations, other ranks"
    031 = "Armed forces occupations, other ranks"
    0310 = "Armed forces occupations, other ranks"
    1 = "Managers"
    11 = "Chief executives, senior officials and legislators"
    111 = "Legislators and senior officials"
    1111 = "Legislators"
    1112 = "Senior government officials"
    1113 = "Traditional chiefs and heads of village"
    1114 = "Senior officials of special-interest organizations"
    112 = "Managing directors and chief executives"
    1120 = "Managing directors and chief executives"
    12 = "Administrative and commercial managers"
    121 = "Business services and administration managers"
    1211 = "Finance managers"
    1212 = "Human resource managers"
    1213 = "Policy and planning managers"
    1219 = "Business services and administration managers not elsewhere classified"
    122 = "Sales, marketing and development managers"
    1221 = "Sales and marketing managers"
    1222 = "Advertising and public relations managers"
    1223 = "Research and development managers"
    13 = "Production and specialised services managers"
    131 = "Production managers in agriculture, forestry and fisheries"
    1311 = "Agricultural and forestry production managers"
    1312 = "Aquaculture and fisheries production managers"
    132 = "Manufacturing, mining, construction, and distribution managers"
    1321 = "Manufacturing managers"
    1322 = "Mining managers"
    1323 = "Construction managers"
    1324 = "Supply, distribution and related managers"
    133 = "Information and communications technology service managers"
    1330 = "Information and communications technology service managers"
    134 = "Professional services managers"
    1341 = "Child care services managers"
    1342 = "Health services managers"
    1343 = "Aged care services managers"
    1344 = "Social welfare managers"
    1345 = "Education managers"
    1346 = "Financial and insurance services branch managers"
    1349 = "Professional services managers not elsewhere classified"
    14 = "Hospitality, retail and other services managers"
    141 = "Hotel and restaurant managers"
    1411 = "Hotel managers"
    1412 = "Restaurant managers"
    142 = "Retail and wholesale trade managers"
    1420 = "Retail and wholesale trade managers"
    143 = "Other services managers"
    1431 = "Sports, recreation and cultural centre managers"
    1439 = "Services managers not elsewhere classified"
    2 = "Professionals"
    21 = "Science and engineering professionals"
    211 = "Physical and earth science professionals"
    2111 = "Physicists and astronomers"
    2112 = "Meteorologists"
    2113 = "Chemists"
    2114 = "Geologists and geophysicists"
    212 = "Mathematicians, actuaries and statisticians"
    2120 = "Mathematicians, actuaries and statisticians"
    213 = "Life science professionals"
    2131 = "Biologists, botanists, zoologists and related professionals"
    2132 = "Farming, forestry and fisheries advisers"
    2133 = "Environmental protection professionals"
    214 = "Engineering professionals (excluding electrotechnology)"
    2141 = "Industrial and production engineers"
    2142 = "Civil engineers"
    2143 = "Environmental engineers"
    2144 = "Mechanical engineers"
    2145 = "Chemical engineers"
    2146 = "Mining engineers, metallurgists and related professionals"
    2149 = "Engineering professionals not elsewhere classified"
    215 = "Electrotechnology engineers"
    2151 = "Electrical engineers"
    2152 = "Electronics engineers"
    2153 = "Telecommunications engineers"
    216 = "Architects, planners, surveyors and designers"
    2161 = "Building architects"
    2162 = "Landscape architects"
    2163 = "Product and garment designers"
    2164 = "Town and traffic planners"
    2165 = "Cartographers and surveyors"
    2166 = "Graphic and multimedia designers"
    22 = "Health professionals"
    221 = "Medical doctors"
    2211 = "Generalist medical practitioners"
    2212 = "Specialist medical practitioners"
    222 = "Nursing and midwifery professionals"
    2221 = "Nursing professionals"
    2222 = "Midwifery professionals"
    223 = "Traditional and complementary medicine professionals"
    2230 = "Traditional and complementary medicine professionals"
    224 = "Paramedical practitioners"
    2240 = "Paramedical practitioners"
    225 = "Veterinarians"
    2250 = "Veterinarians"
    226 = "Other health professionals"
    2261 = "Dentists"
    2262 = "Pharmacists"
    2263 = "Environmental and occupational health and hygiene professionals"
    2264 = "Physiotherapists"
    2265 = "Dieticians and nutritionists"
    2266 = "Audiologists and speech therapists"
    2267 = "Optometrists and ophthalmic opticians"
    2269 = "Health professionals not elsewhere classified"
    23 = "Teaching professionals"
    231 = "University and higher education teachers"
    2310 = "University and higher education teachers"
    232 = "Vocational education teachers"
    2320 = "Vocational education teachers"
    233 = "Secondary education teachers"
    2330 = "Secondary education teachers"
    234 = "Primary school and early childhood teachers"
    2341 = "Primary school teachers"
    2342 = "Early childhood educators"
    235 = "Other teaching professionals"
    2351 = "Education methods specialists"
    2352 = "Special needs teachers"
    2353 = "Other language teachers"
    2354 = "Other music teachers"
    2355 = "Other arts teachers"
    2356 = "Information technology trainers"
    2359 = "Teaching professionals not elsewhere classified"
    24 = "Business and administration professionals"
    241 = "Finance professionals"
    2411 = "Accountants"
    2412 = "Financial and investment advisers"
    2413 = "Financial analysts"
    242 = "Administration professionals"
    2421 = "Management and organization analysts"
    2422 = "Policy administration professionals"
    2423 = "Personnel and careers professionals"
    2424 = "Training and staff development professionals"
    243 = "Sales, marketing and public relations professionals"
    2431 = "Advertising and marketing professionals"
    2432 = "Public relations professionals"
    2433 = "Technical and medical sales professionals (excluding ICT)"
    2434 = "Information and communications technology sales professionals"
    25 = "Information and communications technology professionals"
    251 = "Software and applications developers and analysts"
    2511 = "Systems analysts"
    2512 = "Software developers"
    2513 = "Web and multimedia developers"
    2514 = "Applications programmers"
    2519 = "Software and applications developers and analysts not elsewhere classified"
    252 = "Database and network professionals"
    2521 = "Database designers and administrators"
    2522 = "Systems administrators"
    2523 = "Computer network professionals"
    2529 = "Database and network professionals not elsewhere classified"
    26 = "Legal, social and cultural professionals"
    261 = "Legal professionals"
    2611 = "Lawyers"
    2612 = "Judges"
    2619 = "Legal professionals not elsewhere classified"
    262 = "Librarians, archivists and curators"
    2621 = "Archivists and curators"
    2622 = "Librarians and related information professionals"
    263 = "Social and religious professionals"
    2631 = "Economists"
    2632 = "Sociologists, anthropologists and related professionals"
    2633 = "Philosophers, historians and political scientists"
    2634 = "Psychologists"
    2635 = "Social work and counselling professionals"
    2636 = "Religious professionals"
    264 = "Authors, journalists and linguists"
    2641 = "Authors and related writers"
    2642 = "Journalists"
    2643 = "Translators, interpreters and other linguists"
    265 = "Creative and performing artists"
    2651 = "Visual artists"
    2652 = "Musicians, singers and composers"
    2653 = "Dancers and choreographers"
    2654 = "Film, stage and related directors and producers"
    2655 = "Actors"
    2656 = "Announcers on radio, television and other media"
    2659 = "Creative and performing artists not elsewhere classified"
    3 = "Technicians and associate professionals"
    31 = "Science and engineering associate professionals"
    311 = "Physical and engineering science technicians"
    3111 = "Chemical and physical science technicians"
    3112 = "Civil engineering technicians"
    3113 = "Electrical engineering technicians"
    3114 = "Electronics engineering technicians"
    3115 = "Mechanical engineering technicians"
    3116 = "Chemical engineering technicians"
    3117 = "Mining and metallurgical technicians"
    3118 = "Draughtspersons"
    3119 = "Physical and engineering science technicians not elsewhere classified"
    312 = "Mining, manufacturing and construction supervisors"
    3121 = "Mining supervisors"
    3122 = "Manufacturing supervisors"
    3123 = "Construction supervisors"
    313 = "Process control technicians"
    3131 = "Power production plant operators"
    3132 = "Incinerator and water treatment plant operators"
    3133 = "Chemical processing plant controllers"
    3134 = "Petroleum and natural gas refining plant operators"
    3135 = "Metal production process controllers"
    3139 = "Process control technicians not elsewhere classified"
    314 = "Life science technicians and related associate professionals"
    3141 = "Life science technicians (excluding medical)"
    3142 = "Agricultural technicians"
    3143 = "Forestry technicians"
    315 = "Ship and aircraft controllers and technicians"
    3151 = "Ships' engineers"
    3152 = "Ships' deck officers and pilots"
    3153 = "Aircraft pilots and related associate professionals"
    3154 = "Air traffic controllers"
    3155 = "Air traffic safety electronics technicians"
    32 = "Health associate professionals"
    321 = "Medical and pharmaceutical technicians"
    3211 = "Medical imaging and therapeutic equipment technicians"
    3212 = "Medical and pathology laboratory technicians"
    3213 = "Pharmaceutical technicians and assistants"
    3214 = "Medical and dental prosthetic technicians"
    322 = "Nursing and midwifery associate professionals"
    3221 = "Nursing associate professionals"
    3222 = "Midwifery associate professionals"
    323 = "Traditional and complementary medicine associate professionals"
    3230 = "Traditional and complementary medicine associate professionals"
    324 = "Veterinary technicians and assistants"
    3240 = "Veterinary technicians and assistants"
    325 = "Other health associate professionals"
    3251 = "Dental assistants and therapists"
    3252 = "Medical records and health information technicians"
    3253 = "Community health workers"
    3254 = "Dispensing opticians"
    3255 = "Physiotherapy technicians and assistants"
    3256 = "Medical assistants"
    3257 = "Environmental and occupational health inspectors and associates"
    3258 = "Ambulance workers"
    3259 = "Health associate professionals not elsewhere classified"
    33 = "Business and administration associate professionals"
    331 = "Financial and mathematical associate professionals"
    3311 = "Securities and finance dealers and brokers"
    3312 = "Credit and loans officers"
    3313 = "Accounting associate professionals"
    3314 = "Statistical, mathematical and related associate professionals"
    3315 = "Valuers and loss assessors"
    332 = "Sales and purchasing agents and brokers"
    3321 = "Insurance representatives"
    3322 = "Commercial sales representatives"
    3323 = "Buyers"
    3324 = "Trade brokers"
    333 = "Business services agents"
    3331 = "Clearing and forwarding agents"
    3332 = "Conference and event planners"
    3333 = "Employment agents and contractors"
    3334 = "Real estate agents and property managers"
    3339 = "Business services agents not elsewhere classified"
    334 = "Administrative and specialised secretaries"
    3341 = "Office supervisors"
    3342 = "Legal secretaries"
    3343 = "Administrative and executive secretaries"
    3344 = "Medical secretaries"
    335 = "Regulatory government associate professionals"
    3351 = "Customs and border inspectors"
    3352 = "Government tax and excise officials"
    3353 = "Government social benefits officials"
    3354 = "Government licensing officials"
    3355 = "Police inspectors and detectives"
    3359 = "Regulatory government associate professionals not elsewhere classified"
    34 = "Legal, social, cultural and related associate professionals"
    341 = "Legal, social and religious associate professionals"
    3411 = "Police inspectors and detectives"
    3412 = "Social work associate professionals"
    3413 = "Religious associate professionals"
    342 = "Sports and fitness workers"
    3421 = "Athletes and sports players"
    3422 = "Sports coaches, instructors and officials"
    3423 = "Fitness and recreation instructors and program leaders"
    343 = "Artistic, cultural and culinary associate professionals"
    3431 = "Photographers"
    3432 = "Interior designers and decorators"
    3433 = "Gallery, museum and library technicians"
    3434 = "Chefs"
    3435 = "Other artistic and cultural associate professionals"
    35 = "Information and communications technicians"
    351 = "Information and communications technology operations and user support technicians"
    3511 = "Information and communications technology operations technicians"
    3512 = "Information and communications technology user support technicians"
    3513 = "Computer network and systems technicians"
    3514 = "Web technicians"
    352 = "Telecommunications and broadcasting technicians"
    3521 = "Broadcasting and audio-visual technicians"
    3522 = "Telecommunications engineering technicians"
    4 = "Clerical support workers"
    41 = "General and keyboard clerks"
    411 = "General office clerks"
    4110 = "General office clerks"
    412 = "Secretaries (general)"
    4120 = "Secretaries (general)"
    413 = "Keyboard operators"
    4131 = "Typists and word processing operators"
    4132 = "Data entry clerks"
    42 = "Customer services clerks"
    421 = "Tellers, money collectors and related clerks"
    4211 = "Bank tellers and related clerks"
    4212 = "Bookmakers, croupiers and related gaming workers"
    4213 = "Pawnbrokers and money-lenders"
    4214 = "Debt-collectors and related workers"
    422 = "Client information workers"
    4221 = "Travel consultants and clerks"
    4222 = "Contact centre information clerks"
    4223 = "Telephone switchboard operators"
    4224 = "Hotel receptionists"
    4225 = "Enquiry clerks"
    4226 = "Receptionists (general)"
    4227 = "Survey and market research interviewers"
    4229 = "Client information workers not elsewhere classified"
    43 = "Numerical and material recording clerks"
    431 = "Numerical clerks"
    4311 = "Accounting and bookkeeping clerks"
    4312 = "Statistical, finance and insurance clerks"
    4313 = "Payroll clerks"
    432 = "Material-recording and transport clerks"
    4321 = "Stock clerks"
    4322 = "Production clerks"
    4323 = "Transport clerks"
    44 = "Other clerical support workers"
    441 = "Other clerical support workers"
    4411 = "Library clerks"
    4412 = "Mail carriers and sorting clerks"
    4413 = "Coding, proof-reading and related clerks"
    4414 = "Scribes and related workers"
    4415 = "Filing and copying clerks"
    4416 = "Personnel clerks"
    4419 = "Clerical support workers not elsewhere classified"
    5 = "Service and sales workers"
    51 = "Personal service workers"
    511 = "Travel attendants, conductors and guides"
    5111 = "Travel attendants and travel stewards"
    5112 = "Transport conductors"
    5113 = "Travel guides"
    512 = "Cooks"
    5120 = "Cooks"
    513 = "Waiters and bartenders"
    5131 = "Waiters"
    5132 = "Bartenders"
    514 = "Hairdressers, beauticians and related workers"
    5141 = "Hairdressers"
    5142 = "Beauticians and related workers"
    515 = "Building and housekeeping supervisors"
    5151 = "Cleaning and housekeeping supervisors in offices, hotels and other establishments"
    5152 = "Domestic housekeepers"
    5153 = "Building caretakers"
    516 = "Other personal services workers"
    5161 = "Astrologers, fortune-tellers and related workers"
    5162 = "Companions and valets"
    5163 = "Undertakers and embalmers"
    5164 = "Pet groomers and animal care workers"
    5165 = "Driving instructors"
    5169 = "Personal services workers not elsewhere classified"
    52 = "Sales workers"
    521 = "Street and market salespersons"
    5211 = "Stall and market salespersons"
    5212 = "Street food salespersons"
    522 = "Shop salespersons"
    5221 = "Shop keepers"
    5222 = "Shop supervisors"
    5223 = "Shop sales assistants"
    523 = "Cashiers and ticket clerks"
    5230 = "Cashiers and ticket clerks"
    524 = "Other sales workers"
    5241 = "Fashion and other models"
    5242 = "Sales demonstrators"
    5243 = "Door to door salespersons"
    5244 = "Contact centre salespersons"
    5245 = "Service station attendants"
    5246 = "Food service counter attendants"
    5249 = "Sales workers not elsewhere classified"
    53 = "Personal care workers"
    531 = "Child care workers and teachers' aides"
    5311 = "Child care workers"
    5312 = "Teachers' aides"
    532 = "Personal care workers in health services"
    5321 = "Health care assistants"
    5322 = "Home-based personal care workers"
    5329 = "Personal care workers in health services not elsewhere classified"
    54 = "Protective services workers"
    541 = "Protective services workers"
    5411 = "Fire-fighters"
    5412 = "Police officers"
    5413 = "Prison guards"
    5414 = "Security guards"
    5419 = "Protective services workers not elsewhere classified"
    6 = "Skilled agricultural, forestry and fishery workers"
    61 = "Market-oriented skilled agricultural workers"
    611 = "Market gardeners and crop growers"
    6111 = "Field crop and vegetable growers"
    6112 = "Tree and shrub crop growers"
    6113 = "Gardeners, horticultural and nursery growers"
    6114 = "Mixed crop growers"
    612 = "Animal producers"
    6121 = "Livestock and dairy producers"
    6122 = "Poultry producers"
    6123 = "Apiarists and sericulturists"
    6129 = "Animal producers not elsewhere classified"
    613 = "Mixed crop and animal producers"
    6130 = "Mixed crop and animal producers"
    62 = "Market-oriented skilled forestry, fishery and hunting workers"
    621 = "Forestry and related workers"
    6210 = "Forestry and related workers"
    622 = "Fishery workers, hunters and trappers"
    6221 = "Aquaculture workers"
    6222 = "Inland and coastal waters fishery workers"
    6223 = "Deep-sea fishery workers"
    6224 = "Hunters and trappers"
    63 = "Subsistence farmers, fishers, hunters and gatherers"
    631 = "Subsistence crop farmers"
    6310 = "Subsistence crop farmers"
    632 = "Subsistence livestock farmers"
    6320 = "Subsistence livestock farmers"
    633 = "Subsistence mixed crop and livestock farmers"
    6330 = "Subsistence mixed crop and livestock farmers"
    634 = "Subsistence fishers, hunters, trappers and gatherers"
    6340 = "Subsistence fishers, hunters, trappers and gatherers"
    7 = "Craft and related trades workers"
    71 = "Building and related trades workers, excluding electricians"
    711 = "Building frame and related trades workers"
    7111 = "House builders"
    7112 = "Bricklayers and related workers"
    7113 = "Stonemasons, stone cutters, splitters and carvers"
    7114 = "Concrete placers, concrete finishers and related workers"
    7115 = "Carpenters and joiners"
    7119 = "Building frame and related trades workers not elsewhere classified"
    712 = "Building finishers and related trades workers"
    7121 = "Roofers"
    7122 = "Floor layers and tile setters"
    7123 = "Plasterers"
    7124 = "Insulation workers"
    7125 = "Glaziers"
    7126 = "Plumbers and pipe fitters"
    7127 = "Air conditioning and refrigeration mechanics"
    713 = "Painters, building structure cleaners and related trades workers"
    7131 = "Painters and related workers"
    7132 = "Spray painters and varnishers"
    7133 = "Building structure cleaners"
    72 = "Metal, machinery and related trades workers"
    721 = "Sheet and structural metal workers, moulders and welders, and related workers"
    7211 = "Metal moulders and coremakers"
    7212 = "Welders and flamecutters"
    7213 = "Sheet-metal workers"
    7214 = "Structural-metal preparers and erectors"
    7215 = "Riggers and cable splicers"
    722 = "Blacksmiths, toolmakers and related trades workers"
    7221 = "Blacksmiths, hammersmiths and forging press workers"
    7222 = "Toolmakers and related workers"
    7223 = "Metal working machine tool setters and operators"
    7224 = "Metal polishers, wheel grinders and tool sharpeners"
    723 = "Machinery mechanics and repairers"
    7231 = "Motor vehicle mechanics and repairers"
    7232 = "Aircraft engine mechanics and repairers"
    7233 = "Agricultural and industrial machinery mechanics and repairers"
    7234 = "Bicycle and related repairers"
    73 = "Handicraft and printing workers"
    731 = "Handicraft workers"
    7311 = "Precision-instrument makers and repairers"
    7312 = "Musical instrument makers and tuners"
    7313 = "Jewellery and precious-metal workers"
    7314 = "Potters and related workers"
    7315 = "Glass makers, cutters, grinders and finishers"
    7316 = "Sign writers, decorative painters, engravers and etchers"
    7317 = "Handicraft workers in wood, basketry and related materials"
    7318 = "Handicraft workers in textile, leather and related materials"
    7319 = "Handicraft workers not elsewhere classified"
    732 = "Printing trades workers"
    7321 = "Pre-press technicians"
    7322 = "Printers"
    7323 = "Print finishing and binding workers"
    74 = "Electrical and electronic trades workers"
    741 = "Electrical equipment installers and repairers"
    7411 = "Building and related electricians"
    7412 = "Electrical mechanics and fitters"
    7413 = "Electrical line installers and repairers"
    742 = "Electronics and telecommunications installers and repairers"
    7421 = "Electronics mechanics and servicers"
    7422 = "Information and communications technology installers and servicers"
    75 = "Food processing, wood working, garment and other craft and related trades workers"
    751 = "Food processing and related trades workers"
    7511 = "Butchers, fishmongers and related food preparers"
    7512 = "Bakers, pastry-cooks and confectionery makers"
    7513 = "Dairy-products makers"
    7514 = "Fruit, vegetable and related preservers"
    7515 = "Food and beverage tasters and graders"
    7516 = "Tobacco preparers and tobacco products makers"
    752 = "Wood treaters, cabinet-makers and related trades workers"
    7521 = "Wood treaters"
    7522 = "Cabinet-makers and related workers"
    7523 = "Woodworking-machine tool setters and operators"
    753 = "Garment and related trades workers"
    7531 = "Tailors, dressmakers, furriers and hatters"
    7532 = "Garment and related pattern-makers and cutters"
    7533 = "Sewing, embroidery and related workers"
    7534 = "Upholsterers and related workers"
    7535 = "Pelt dressers, tanners and fellmongers"
    7536 = "Shoemakers and related workers"
    754 = "Other craft and related workers"
    7541 = "Underwater divers"
    7542 = "Shotfirers and blasters"
    7543 = "Product graders and testers (excluding foods and beverages)"
    7544 = "Fumigators and other pest and weed controllers"
    7549 = "Craft and related workers not elsewhere classified"
    8 = "Plant and machine operators, and assemblers"
    81 = "Stationary plant and machine operators"
    811 = "Mining and mineral processing plant operators"
    8111 = "Miners and quarriers"
    8112 = "Mineral and stone processing plant operators"
    8113 = "Well drillers and borers and related workers"
    8114 = "Cement, stone and other mineral products machine operators"
    812 = "Metal processing and finishing plant operators"
    8121 = "Metal processing plant operators"
    8122 = "Metal finishing, plating and coating machine operators"
    813 = "Chemical and photographic products plant and machine operators"
    8131 = "Chemical products plant and machine operators"
    8132 = "Photographic products machine operators"
    814 = "Rubber, plastic and paper products machine operators"
    8141 = "Rubber products machine operators"
    8142 = "Plastic products machine operators"
    8143 = "Paper products machine operators"
    815 = "Textile, fur and leather products machine operators"
    8151 = "Fibre preparing, spinning and winding machine operators"
    8152 = "Weaving and knitting machine operators"
    8153 = "Sewing machine operators"
    8154 = "Bleaching, dyeing and fabric cleaning machine operators"
    8155 = "Fur and leather preparing machine operators"
    8156 = "Shoemaking and related machine operators"
    8157 = "Laundry machine operators"
    8159 = "Textile, fur and leather products machine operators not elsewhere classified"
    816 = "Food and related products machine operators"
    8160 = "Food and related products machine operators"
    817 = "Wood processing and papermaking plant operators"
    8171 = "Pulp and papermaking plant operators"
    8172 = "Wood processing plant operators"
    818 = "Other stationary plant and machine operators"
    8181 = "Glass and ceramics plant operators"
    8182 = "Steam engine and boiler operators"
    8183 = "Packing, bottling and labelling machine operators"
    8189 = "Stationary plant and machine operators not elsewhere classified"
    82 = "Assemblers"
    821 = "Assemblers"
    8211 = "Mechanical machinery assemblers"
    8212 = "Electrical and electronic equipment assemblers"
    8219 = "Assemblers not elsewhere classified"
    83 = "Drivers and mobile plant operators"
    831 = "Locomotive engine drivers and related workers"
    8311 = "Locomotive engine drivers"
    8312 = "Railway brake, signal and switch operators"
    832 = "Car, van and motorcycle drivers"
    8321 = "Motorcycle drivers"
    8322 = "Car, taxi and van drivers"
    833 = "Heavy truck and bus drivers"
    8331 = "Bus and tram drivers"
    8332 = "Heavy truck and lorry drivers"
    834 = "Mobile plant operators"
    8341 = "Mobile farm and forestry plant operators"
    8342 = "Earthmoving and related plant operators"
    8343 = "Crane, hoist and related plant operators"
    8344 = "Lifting truck operators"
    835 = "Ships' deck crews and related workers"
    8350 = "Ships' deck crews and related workers"
    9 = "Elementary occupations"
    91 = "Cleaners and helpers"
    911 = "Domestic, hotel and office cleaners and helpers"
    9111 = "Domestic cleaners and helpers"
    9112 = "Cleaners and helpers in offices, hotels and other establishments"
    912 = "Vehicle, window, laundry and other hand cleaning workers"
    9121 = "Hand launderers and pressers"
    9122 = "Vehicle cleaners"
    9123 = "Window cleaners"
    9129 = "Other cleaning workers"
    92 = "Agricultural, forestry and fishery labourers"
    921 = "Agricultural, forestry and fishery labourers"
    9211 = "Crop farm labourers"
    9212 = "Livestock farm labourers"
    9213 = "Mixed crop and livestock farm labourers"
    9214 = "Garden and horticultural labourers"
    9215 = "Forestry labourers"
    9216 = "Fishery and aquaculture labourers"
    93 = "Labourers in mining, construction, manufacturing and transport"
    931 = "Mining and construction labourers"
    9311 = "Mining and quarrying labourers"
    9312 = "Civil engineering labourers"
    9313 = "Building construction labourers"
    932 = "Manufacturing labourers"
    9321 = "Hand packers"
    9329 = "Manufacturing labourers not elsewhere classified"
    933 = "Transport and storage labourers"
    9331 = "Hand and pedal vehicle drivers"
    9332 = "Drivers of animal-drawn vehicles and machinery"
    9333 = "Freight handlers"
    9334 = "Shelf fillers"
    94 = "Food preparation assistants"
    941 = "Food preparation assistants"
    9411 = "Fast food preparers"
    9412 = "Kitchen helpers"
    95 = "Street and related sales and service workers"
    951 = "Street and related service workers"
    9510 = "Street and related service workers"
    952 = "Street vendors (excluding food)"
    9520 = "Street vendors (excluding food)"
    96 = "Refuse workers and other elementary workers"
    961 = "Refuse workers"
    9611 = "Garbage and recycling collectors"
    9612 = "Refuse sorters"
    9613 = "Sweepers and related labourers"
    962 = "Other elementary workers"
    9621 = "Messengers, package deliverers and luggage porters"
    9622 = "Odd job persons"
    9623 = "Meter readers and vending-machine collectors"
    9624 = "Water and firewood collectors"
    9629 = "Elementary workers not elsewhere classified"
    9996 = "Valid skip"
    9997 = "Don't know"
    9998 = "Refused"
    9999 = "Not stated or inferred"
  ;

  VALUE $ISIC4_CUS_C
    01 = "Crop and animal production, hunting and related service activities"
    011 = "Growing of non-perennial crops"
    0111 = "Growing of cereals (except rice), leguminous crops and oil seeds"
    0112 = "Growing of rice"
    0113 = "Growing of vegetables and melons, roots and tubers"
    0114 = "Growing of sugar cane"
    0115 = "Growing of tobacco"
    0116 = "Growing of fibre crops"
    0119 = "Growing of other non-perennial crops"
    012 = "Growing of perennial crops"
    0121 = "Growing of grapes"
    0122 = "Growing of tropical and subtropical fruits"
    0123 = "Growing of citrus fruits"
    0124 = "Growing of pome fruits and stone fruits"
    0125 = "Growing of other tree and bush fruits and nuts"
    0126 = "Growing of oleaginous fruits"
    0127 = "Growing of beverage crops"
    0128 = "Growing of spices, aromatic, drug and pharmaceutical crops"
    0129 = "Growing of other perennial crops"
    013 = "Plant propagation"
    0130 = "Plant propagation"
    014 = "Animal production"
    0141 = "Raising of cattle and buffaloes"
    0142 = "Raising of horses and other equines"
    0143 = "Raising of camels and camelids"
    0144 = "Raising of sheep and goats"
    0145 = "Raising of swine/pigs"
    0146 = "Raising of poultry"
    0149 = "Raising of other animals"
    015 = "Mixed farming"
    0150 = "Mixed farming"
    016 = "Support activities to agriculture and post-harvest crop activities"
    0161 = "Support activities for crop production"
    0162 = "Support activities for animal production"
    0163 = "Post-harvest crop activities"
    0164 = "Seed processing for propagation"
    017 = "Hunting, trapping and related service activities"
    0170 = "Hunting, trapping and related service activities"
    02 = "Forestry and logging"
    021 = "Silviculture and other forestry activities"
    0210 = "Silviculture and other forestry activities"
    022 = "Logging"
    0220 = "Logging"
    023 = "Gathering of non-wood forest products"
    0230 = "Gathering of non-wood forest products"
    024 = "Support services to forestry"
    0240 = "Support services to forestry"
    03 = "Fishing and aquaculture"
    031 = "Fishing"
    0311 = "Marine fishing"
    0312 = "Freshwater fishing"
    032 = "Aquaculture"
    0321 = "Marine aquaculture"
    0322 = "Freshwater aquaculture"
    05 = "Mining of coal and lignite"
    051 = "Mining of hard coal"
    0510 = "Mining of hard coal"
    052 = "Mining of lignite"
    0520 = "Mining of lignite"
    06 = "Extraction of crude petroleum and natural gas"
    061 = "Extraction of crude petroleum"
    0610 = "Extraction of crude petroleum"
    062 = "Extraction of natural gas"
    0620 = "Extraction of natural gas"
    07 = "Mining of metal ores"
    071 = "Mining of iron ores"
    0710 = "Mining of iron ores"
    072 = "Mining of non-ferrous metal ores"
    0721 = "Mining of uranium and thorium ores"
    0729 = "Mining of other non-ferrous metal ores"
    08 = "Other mining and quarrying"
    081 = "Quarrying of stone, sand and clay"
    0810 = "Quarrying of stone, sand and clay"
    089 = "Mining and quarrying n.e.c."
    0891 = "Mining of chemical and fertilizer minerals"
    0892 = "Extraction of peat"
    0893 = "Extraction of salt"
    0899 = "Other mining and quarrying n.e.c."
    09 = "Mining support service activities"
    091 = "Support activities for petroleum and natural gas extraction"
    0910 = "Support activities for petroleum and natural gas extraction"
    099 = "Support activities for other mining and quarrying"
    0990 = "Support activities for other mining and quarrying"
    10 = "Manufacture of food products"
    101 = "Processing and preserving of meat"
    1010 = "Processing and preserving of meat"
    102 = "Processing and preserving of fish, crustaceans and molluscs"
    1020 = "Processing and preserving of fish, crustaceans and molluscs"
    103 = "Processing and preserving of fruit and vegetables"
    1030 = "Processing and preserving of fruit and vegetables"
    104 = "Manufacture of vegetable and animal oils and fats"
    1040 = "Manufacture of vegetable and animal oils and fats"
    105 = "Manufacture of dairy products"
    1050 = "Manufacture of dairy products"
    106 = "Manufacture of grain mill products, starches and starch products"
    1061 = "Manufacture of grain mill products"
    1062 = "Manufacture of starches and starch products"
    107 = "Manufacture of other food products"
    1071 = "Manufacture of bakery products"
    1072 = "Manufacture of sugar"
    1073 = "Manufacture of cocoa, chocolate and sugar confectionery"
    1074 = "Manufacture of macaroni, noodles, couscous and similar farinaceous products"
    1075 = "Manufacture of prepared meals and dishes"
    1079 = "Manufacture of other food products n.e.c."
    108 = "Manufacture of prepared animal feeds"
    1080 = "Manufacture of prepared animal feeds"
    11 = "Manufacture of beverages"
    110 = "Manufacture of beverages"
    1101 = "Distilling, rectifying and blending of spirits"
    1102 = "Manufacture of wines"
    1103 = "Manufacture of malt liquors and malt"
    1104 = "Manufacture of soft drinks; production of mineral waters and other bottled waters"
    12 = "Manufacture of tobacco products"
    120 = "Manufacture of tobacco products"
    1200 = "Manufacture of tobacco products"
    13 = "Manufacture of textiles"
    131 = "Spinning, weaving and finishing of textiles"
    1311 = "Preparation and spinning of textile fibres"
    1312 = "Weaving of textiles"
    1313 = "Finishing of textiles"
    139 = "Manufacture of other textiles"
    1391 = "Manufacture of knitted and crocheted fabrics"
    1392 = "Manufacture of made-up textile articles, except apparel"
    1393 = "Manufacture of carpets and rugs"
    1394 = "Manufacture of cordage, rope, twine and netting"
    1399 = "Manufacture of other textiles n.e.c."
    14 = "Manufacture of wearing apparel"
    141 = "Manufacture of wearing apparel, except fur apparel"
    1410 = "Manufacture of wearing apparel, except fur apparel"
    142 = "Manufacture of articles of fur"
    1420 = "Manufacture of articles of fur"
    143 = "Manufacture of knitted and crocheted apparel"
    1430 = "Manufacture of knitted and crocheted apparel"
    15 = "Manufacture of leather and related products"
    151 = "Tanning and dressing of leather; manufacture of luggage, handbags, saddlery and harness; dressing and dyeing of fur"
    1511 = "Tanning and dressing of leather; dressing and dyeing of fur"
    1512 = "Manufacture of luggage, handbags and the like, saddlery and harness"
    152 = "Manufacture of footwear"
    1520 = "Manufacture of footwear"
    16 = "Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plait"
    161 = "Sawmilling and planing of wood"
    1610 = "Sawmilling and planing of wood"
    162 = "Manufacture of products of wood, cork, straw and plaiting materials"
    1621 = "Manufacture of veneer sheets and wood-based panels"
    1622 = "Manufacture of builders' carpentry and joinery"
    1623 = "Manufacture of wooden containers"
    1629 = "Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials"
    17 = "Manufacture of paper and paper products"
    170 = "Manufacture of paper and paper products"
    1701 = "Manufacture of pulp, paper and paperboard"
    1702 = "Manufacture of corrugated paper and paperboard and of containers of paper and paperboard"
    1709 = "Manufacture of other articles of paper and paperboard"
    18 = "Printing and reproduction of recorded media"
    181 = "Printing and service activities related to printing"
    1811 = "Printing"
    1812 = "Service activities related to printing"
    182 = "Reproduction of recorded media"
    1820 = "Reproduction of recorded media"
    19 = "Manufacture of coke and refined petroleum products"
    191 = "Manufacture of coke oven products"
    1910 = "Manufacture of coke oven products"
    192 = "Manufacture of refined petroleum products"
    1920 = "Manufacture of refined petroleum products"
    20 = "Manufacture of chemicals and chemical products"
    201 = "Manufacture of basic chemicals, fertilizers and nitrogen compounds, plastics and synthetic rubber in primary forms"
    2011 = "Manufacture of basic chemicals"
    2012 = "Manufacture of fertilizers and nitrogen compounds"
    2013 = "Manufacture of plastics and synthetic rubber in primary forms"
    202 = "Manufacture of other chemical products"
    2021 = "Manufacture of pesticides and other agrochemical products"
    2022 = "Manufacture of paints, varnishes and similar coatings, printing ink and mastics"
    2023 = "Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations"
    2029 = "Manufacture of other chemical products n.e.c."
    203 = "Manufacture of man-made fibres"
    2030 = "Manufacture of man-made fibres"
    21 = "Manufacture of basic pharmaceutical products and pharmaceutical preparations"
    210 = "Manufacture of pharmaceuticals, medicinal chemical and botanical products"
    2100 = "Manufacture of pharmaceuticals, medicinal chemical and botanical products"
    22 = "Manufacture of rubber and plastics products"
    221 = "Manufacture of rubber products"
    2211 = "Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres"
    2219 = "Manufacture of other rubber products"
    222 = "Manufacture of plastics products"
    2220 = "Manufacture of plastics products"
    23 = "Manufacture of other non-metallic mineral products"
    231 = "Manufacture of glass and glass products"
    2310 = "Manufacture of glass and glass products"
    239 = "Manufacture of non-metallic mineral products n.e.c."
    2391 = "Manufacture of refractory products"
    2392 = "Manufacture of clay building materials"
    2393 = "Manufacture of other porcelain and ceramic products"
    2394 = "Manufacture of cement, lime and plaster"
    2395 = "Manufacture of articles of concrete, cement and plaster"
    2396 = "Cutting, shaping and finishing of stone"
    2399 = "Manufacture of other non-metallic mineral products n.e.c."
    24 = "Manufacture of basic metals"
    241 = "Manufacture of basic iron and steel"
    2410 = "Manufacture of basic iron and steel"
    242 = "Manufacture of basic precious and other non-ferrous metals"
    2420 = "Manufacture of basic precious and other non-ferrous metals"
    243 = "Casting of metals"
    2431 = "Casting of iron and steel"
    2432 = "Casting of non-ferrous metals"
    25 = "Manufacture of fabricated metal products, except machinery and equipment"
    251 = "Manufacture of structural metal products, tanks, reservoirs and steam generators"
    2511 = "Manufacture of structural metal products"
    2512 = "Manufacture of tanks, reservoirs and containers of metal"
    2513 = "Manufacture of steam generators, except central heating hot water boilers"
    252 = "Manufacture of weapons and ammunition"
    2520 = "Manufacture of weapons and ammunition"
    259 = "Manufacture of other fabricated metal products; metalworking service activities"
    2591 = "Forging, pressing, stamping and roll-forming of metal; powder metallurgy"
    2592 = "Treatment and coating of metals; machining"
    2593 = "Manufacture of cutlery, hand tools and general hardware"
    2599 = "Manufacture of other fabricated metal products n.e.c."
    26 = "Manufacture of computer, electronic and optical products"
    261 = "Manufacture of electronic components and boards"
    2610 = "Manufacture of electronic components and boards"
    262 = "Manufacture of computers and peripheral equipment"
    2620 = "Manufacture of computers and peripheral equipment"
    263 = "Manufacture of communication equipment"
    2630 = "Manufacture of communication equipment"
    264 = "Manufacture of consumer electronics"
    2640 = "Manufacture of consumer electronics"
    265 = "Manufacture of measuring, testing, navigating and control equipment; watches and clocks"
    2651 = "Manufacture of measuring, testing, navigating and control equipment"
    2652 = "Manufacture of watches and clocks"
    266 = "Manufacture of irradiation, electromedical and electrotherapeutic equipment"
    2660 = "Manufacture of irradiation, electromedical and electrotherapeutic equipment"
    267 = "Manufacture of optical instruments and photographic equipment"
    2670 = "Manufacture of optical instruments and photographic equipment"
    268 = "Manufacture of magnetic and optical media"
    2680 = "Manufacture of magnetic and optical media"
    27 = "Manufacture of electrical equipment"
    271 = "Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus"
    2710 = "Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus"
    272 = "Manufacture of batteries and accumulators"
    2720 = "Manufacture of batteries and accumulators"
    273 = "Manufacture of wiring and wiring devices"
    2731 = "Manufacture of fibre optic cables"
    2732 = "Manufacture of other electronic and electric wires and cables"
    2733 = "Manufacture of wiring devices"
    274 = "Manufacture of electric lighting equipment"
    2740 = "Manufacture of electric lighting equipment"
    275 = "Manufacture of domestic appliances"
    2750 = "Manufacture of domestic appliances"
    279 = "Manufacture of other electrical equipment"
    2790 = "Manufacture of other electrical equipment"
    28 = "Manufacture of machinery and equipment n.e.c."
    281 = "Manufacture of general-purpose machinery"
    2811 = "Manufacture of engines and turbines, except aircraft, vehicle and cycle engines"
    2812 = "Manufacture of fluid power equipment"
    2813 = "Manufacture of other pumps, compressors, taps and valves"
    2814 = "Manufacture of bearings, gears, gearing and driving elements"
    2815 = "Manufacture of ovens, furnaces and furnace burners"
    2816 = "Manufacture of lifting and handling equipment"
    2817 = "Manufacture of office machinery and equipment (except computers and peripheral equipment)"
    2818 = "Manufacture of power-driven hand tools"
    2819 = "Manufacture of other general-purpose machinery"
    282 = "Manufacture of special-purpose machinery"
    2821 = "Manufacture of agricultural and forestry machinery"
    2822 = "Manufacture of metal-forming machinery and machine tools"
    2823 = "Manufacture of machinery for metallurgy"
    2824 = "Manufacture of machinery for mining, quarrying and construction"
    2825 = "Manufacture of machinery for food, beverage and tobacco processing"
    2826 = "Manufacture of machinery for textile, apparel and leather production"
    2829 = "Manufacture of other special-purpose machinery"
    29 = "Manufacture of motor vehicles, trailers and semi-trailers"
    291 = "Manufacture of motor vehicles"
    2910 = "Manufacture of motor vehicles"
    292 = "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers"
    2920 = "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers"
    293 = "Manufacture of parts and accessories for motor vehicles"
    2930 = "Manufacture of parts and accessories for motor vehicles"
    30 = "Manufacture of other transport equipment"
    301 = "Building of ships and boats"
    3011 = "Building of ships and floating structures"
    3012 = "Building of pleasure and sporting boats"
    302 = "Manufacture of railway locomotives and rolling stock"
    3020 = "Manufacture of railway locomotives and rolling stock"
    303 = "Manufacture of air and spacecraft and related machinery"
    3030 = "Manufacture of air and spacecraft and related machinery"
    304 = "Manufacture of military fighting vehicles"
    3040 = "Manufacture of military fighting vehicles"
    309 = "Manufacture of transport equipment n.e.c."
    3091 = "Manufacture of motorcycles"
    3092 = "Manufacture of bicycles and invalid carriages"
    3099 = "Manufacture of other transport equipment n.e.c."
    31 = "Manufacture of furniture"
    310 = "Manufacture of furniture"
    3100 = "Manufacture of furniture"
    32 = "Other manufacturing"
    321 = "Manufacture of jewellery, bijouterie and related articles"
    3211 = "Manufacture of jewellery and related articles"
    3212 = "Manufacture of imitation jewellery and related articles"
    322 = "Manufacture of musical instruments"
    3220 = "Manufacture of musical instruments"
    323 = "Manufacture of sports goods"
    3230 = "Manufacture of sports goods"
    324 = "Manufacture of games and toys"
    3240 = "Manufacture of games and toys"
    325 = "Manufacture of medical and dental instruments and supplies"
    3250 = "Manufacture of medical and dental instruments and supplies"
    329 = "Other manufacturing n.e.c."
    3290 = "Other manufacturing n.e.c."
    33 = "Repair and installation of machinery and equipment"
    331 = "Repair of fabricated metal products, machinery and equipment"
    3311 = "Repair of fabricated metal products"
    3312 = "Repair of machinery"
    3313 = "Repair of electronic and optical equipment"
    3314 = "Repair of electrical equipment"
    3315 = "Repair of transport equipment, except motor vehicles"
    3319 = "Repair of other equipment"
    332 = "Installation of industrial machinery and equipment"
    3320 = "Installation of industrial machinery and equipment"
    35 = "Electricity, gas, steam and air conditioning supply"
    351 = "Electric power generation, transmission and distribution"
    3510 = "Electric power generation, transmission and distribution"
    352 = "Manufacture of gas; distribution of gaseous fuels through mains"
    3520 = "Manufacture of gas; distribution of gaseous fuels through mains"
    353 = "Steam and air conditioning supply"
    3530 = "Steam and air conditioning supply"
    36 = "Water collection, treatment and supply"
    360 = "Water collection, treatment and supply"
    3600 = "Water collection, treatment and supply"
    37 = "Sewerage"
    370 = "Sewerage"
    3700 = "Sewerage"
    38 = "Waste collection, treatment and disposal activities; materials recovery"
    381 = "Waste collection"
    3811 = "Collection of non-hazardous waste"
    3812 = "Collection of hazardous waste"
    382 = "Waste treatment and disposal"
    3821 = "Treatment and disposal of non-hazardous waste"
    3822 = "Treatment and disposal of hazardous waste"
    383 = "Materials recovery"
    3830 = "Materials recovery"
    39 = "Remediation activities and other waste management services"
    390 = "Remediation activities and other waste management services"
    3900 = "Remediation activities and other waste management services"
    41 = "Construction of buildings"
    410 = "Construction of buildings"
    4100 = "Construction of buildings"
    42 = "Civil engineering"
    421 = "Construction of roads and railways"
    4210 = "Construction of roads and railways"
    422 = "Construction of utility projects"
    4220 = "Construction of utility projects"
    429 = "Construction of other civil engineering projects"
    4290 = "Construction of other civil engineering projects"
    43 = "Specialized construction activities"
    431 = "Demolition and site preparation"
    4311 = "Demolition"
    4312 = "Site preparation"
    432 = "Electrical, plumbing and other construction installation activities"
    4321 = "Electrical installation"
    4322 = "Plumbing, heat and air-conditioning installation"
    4329 = "Other construction installation"
    433 = "Building completion and finishing"
    4330 = "Building completion and finishing"
    439 = "Other specialized construction activities"
    4390 = "Other specialized construction activities"
    45 = "Wholesale and retail trade and repair of motor vehicles and motorcycles"
    451 = "Sale of motor vehicles"
    4510 = "Sale of motor vehicles"
    452 = "Maintenance and repair of motor vehicles"
    4520 = "Maintenance and repair of motor vehicles"
    453 = "Sale of motor vehicle parts and accessories"
    4530 = "Sale of motor vehicle parts and accessories"
    454 = "Sale, maintenance and repair of motorcycles and related parts and accessories"
    4540 = "Sale, maintenance and repair of motorcycles and related parts and accessories"
    46 = "Wholesale trade, except of motor vehicles and motorcycles"
    461 = "Wholesale on a fee or contract basis"
    4610 = "Wholesale on a fee or contract basis"
    462 = "Wholesale of agricultural raw materials and live animals"
    4620 = "Wholesale of agricultural raw materials and live animals"
    463 = "Wholesale of food, beverages and tobacco"
    4630 = "Wholesale of food, beverages and tobacco"
    464 = "Wholesale of household goods"
    4641 = "Wholesale of textiles, clothing and footwear"
    4649 = "Wholesale of other household goods"
    465 = "Wholesale of machinery, equipment and supplies"
    4651 = "Wholesale of computers, computer peripheral equipment and software"
    4652 = "Wholesale of electronic and telecommunications equipment and parts"
    4653 = "Wholesale of agricultural machinery, equipment and supplies"
    4659 = "Wholesale of other machinery and equipment"
    466 = "Other specialized wholesale"
    4661 = "Wholesale of solid, liquid and gaseous fuels and related products"
    4662 = "Wholesale of metals and metal ores"
    4663 = "Wholesale of construction materials, hardware, plumbing and heating equipment and supplies"
    4669 = "Wholesale of waste and scrap and other products n.e.c."
    469 = "Non-specialized wholesale trade"
    4690 = "Non-specialized wholesale trade"
    47 = "Retail trade, except of motor vehicles and motorcycles"
    471 = "Retail sale in non-specialized stores"
    4711 = "Retail sale in non-specialized stores with food, beverages or tobacco predominating"
    4719 = "Other retail sale in non-specialized stores"
    472 = "Retail sale of food, beverages and tobacco in specialized stores"
    4721 = "Retail sale of food in specialized stores"
    4722 = "Retail sale of beverages in specialized stores"
    4723 = "Retail sale of tobacco products in specialized stores"
    473 = "Retail sale of automotive fuel in specialized stores"
    4730 = "Retail sale of automotive fuel in specialized stores"
    474 = "Retail sale of information and communications equipment in specialized stores"
    4741 = "Retail sale of computers, peripheral units, software and telecommunications equipment in specialized stores"
    4742 = "Retail sale of audio and video equipment in specialized stores"
    475 = "Retail sale of other household equipment in specialized stores"
    4751 = "Retail sale of textiles in specialized stores"
    4752 = "Retail sale of hardware, paints and glass in specialized stores"
    4753 = "Retail sale of carpets, rugs, wall and floor coverings in specialized stores"
    4759 = "Retail sale of electrical household appliances, furniture, lighting equipm. and other household articles in spec. stores"
    476 = "Retail sale of cultural and recreation goods in specialized stores"
    4761 = "Retail sale of books, newspapers and stationary in specialized stores"
    4762 = "Retail sale of music and video recordings in specialized stores"
    4763 = "Retail sale of sporting equipment in specialized stores"
    4764 = "Retail sale of games and toys in specialized stores"
    477 = "Retail sale of other goods in specialized stores"
    4771 = "Retail sale of clothing, footwear and leather articles in specialized stores"
    4772 = "Retail sale of pharmaceutical and medical goods, cosmetic and toilet articles in specialized stores"
    4773 = "Other retail sale of new goods in specialized stores"
    4774 = "Retail sale of second-hand goods"
    478 = "Retail sale via stalls and markets"
    4781 = "Retail sale via stalls and markets of food, beverages and tobacco products"
    4782 = "Retail sale via stalls and markets of textiles, clothing and footwear"
    4789 = "Retail sale via stalls and markets of other goods"
    479 = "Retail trade not in stores, stalls or markets"
    4791 = "Retail sale via mail order houses or via Internet"
    4799 = "Other retail sale not in stores, stalls or markets"
    49 = "Land transport and transport via pipelines"
    491 = "Transport via railways"
    4911 = "Passenger rail transport, interurban"
    4912 = "Freight rail transport"
    492 = "Other land transport"
    4921 = "Urban and suburban passenger land transport"
    4922 = "Other passenger land transport"
    4923 = "Freight transport by road"
    493 = "Transport via pipeline"
    4930 = "Transport via pipeline"
    50 = "Water transport"
    501 = "Sea and coastal water transport"
    5011 = "Sea and coastal passenger water transport"
    5012 = "Sea and coastal freight water transport"
    502 = "Inland water transport"
    5021 = "Inland passenger water transport"
    5022 = "Inland freight water transport"
    51 = "Air transport"
    511 = "Passenger air transport"
    5110 = "Passenger air transport"
    512 = "Freight air transport"
    5120 = "Freight air transport"
    52 = "Warehousing and support activities for transportation"
    521 = "Warehousing and storage"
    5210 = "Warehousing and storage"
    522 = "Support activities for transportation"
    5221 = "Service activities incidental to land transportation"
    5222 = "Service activities incidental to water transportation"
    5223 = "Service activities incidental to air transportation"
    5224 = "Cargo handling"
    5229 = "Other transportation support activities"
    53 = "Postal and courier activities"
    531 = "Postal activities"
    5310 = "Postal activities"
    532 = "Courier activities"
    5320 = "Courier activities"
    55 = "Accommodation"
    551 = "Short term accommodation activities"
    5510 = "Short term accommodation activities"
    552 = "Camping grounds, recreational vehicle parks and trailer parks"
    5520 = "Camping grounds, recreational vehicle parks and trailer parks"
    559 = "Other accommodation"
    5590 = "Other accommodation"
    56 = "Food and beverage service activities"
    561 = "Restaurants and mobile food service activities"
    5610 = "Restaurants and mobile food service activities"
    562 = "Event catering and other food service activities"
    5621 = "Event catering"
    5629 = "Other food service activities"
    563 = "Beverage serving activities"
    5630 = "Beverage serving activities"
    58 = "Publishing activities"
    581 = "Publishing of books, periodicals and other publishing activities"
    5811 = "Book publishing"
    5812 = "Publishing of directories and mailing lists"
    5813 = "Publishing of newspapers, journals and periodicals"
    5819 = "Other publishing activities"
    582 = "Software publishing"
    5820 = "Software publishing"
    59 = "Motion picture, video and television programme production, sound recording and music publishing activities"
    591 = "Motion picture, video and television programme activities"
    5911 = "Motion picture, video and television programme production activities"
    5912 = "Motion picture, video and television programme post-production activities"
    5913 = "Motion picture, video and television programme distribution activities"
    5914 = "Motion picture projection activities"
    592 = "Sound recording and music publishing activities"
    5920 = "Sound recording and music publishing activities"
    60 = "Programming and broadcasting activities"
    601 = "Radio broadcasting"
    6010 = "Radio broadcasting"
    602 = "Television programming and broadcasting activities"
    6020 = "Television programming and broadcasting activities"
    61 = "Telecommunications"
    611 = "Wired telecommunications activities"
    6110 = "Wired telecommunications activities"
    612 = "Wireless telecommunications activities"
    6120 = "Wireless telecommunications activities"
    613 = "Satellite telecommunications activities"
    6130 = "Satellite telecommunications activities"
    619 = "Other telecommunications activities"
    6190 = "Other telecommunications activities"
    62 = "Computer programming, consultancy and related activities"
    620 = "Computer programming, consultancy and related activities"
    6201 = "Computer programming activities"
    6202 = "Computer consultancy and computer facilities management activities"
    6209 = "Other information technology and computer service activities"
    63 = "Information service activities"
    631 = "Data processing, hosting and related activities; web portals"
    6311 = "Data processing, hosting and related activities"
    6312 = "Web portals"
    639 = "Other information service activities"
    6391 = "News agency activities"
    6399 = "Other information service activities n.e.c."
    64 = "Financial service activities, except insurance and pension funding"
    641 = "Monetary intermediation"
    6411 = "Central banking"
    6419 = "Other monetary intermediation"
    642 = "Activities of holding companies"
    6420 = "Activities of holding companies"
    643 = "Trusts, funds and similar financial entities"
    6430 = "Trusts, funds and similar financial entities"
    649 = "Other financial service activities, except insurance and pension funding activities"
    6491 = "Financial leasing"
    6492 = "Other credit granting"
    6499 = "Other financial service activities, except insurance and pension funding activities, n.e.c."
    65 = "Insurance, reinsurance and pension funding, except compulsory social security"
    651 = "Insurance"
    6511 = "Life insurance"
    6512 = "Non-life insurance"
    652 = "Reinsurance"
    6520 = "Reinsurance"
    653 = "Pension funding"
    6530 = "Pension funding"
    66 = "Activities auxiliary to financial service and insurance activities"
    661 = "Activities auxiliary to financial service activities, except insurance and pension funding"
    6611 = "Administration of financial markets"
    6612 = "Security and commodity contracts brokerage"
    6619 = "Other activities auxiliary to financial service activities"
    662 = "Activities auxiliary to insurance and pension funding"
    6621 = "Risk and damage evaluation"
    6622 = "Activities of insurance agents and brokers"
    6629 = "Other activities auxiliary to insurance and pension funding"
    663 = "Fund management activities"
    6630 = "Fund management activities"
    68 = "Real estate activities"
    681 = "Real estate activities with own or leased property"
    6810 = "Real estate activities with own or leased property"
    682 = "Real estate activities on a fee or contract basis"
    6820 = "Real estate activities on a fee or contract basis"
    69 = "Legal and accounting activities"
    691 = "Legal activities"
    6910 = "Legal activities"
    692 = "Accounting, bookkeeping and auditing activities; tax consultancy"
    6920 = "Accounting, bookkeeping and auditing activities; tax consultancy"
    70 = "Activities of head offices; management consultancy activities"
    701 = "Activities of head offices"
    7010 = "Activities of head offices"
    702 = "Management consultancy activities"
    7020 = "Management consultancy activities"
    71 = "Architectural and engineering activities; technical testing and analysis"
    711 = "Architectural and engineering activities and related technical consultancy"
    7110 = "Architectural and engineering activities and related technical consultancy"
    712 = "Technical testing and analysis"
    7120 = "Technical testing and analysis"
    72 = "Scientific research and development"
    721 = "Research and experimental development on natural sciences and engineering"
    7210 = "Research and experimental development on natural sciences and engineering"
    722 = "Research and experimental development on social sciences and humanities"
    7220 = "Research and experimental development on social sciences and humanities"
    73 = "Advertising and market research"
    731 = "Advertising"
    7310 = "Advertising"
    732 = "Market research and public opinion polling"
    7320 = "Market research and public opinion polling"
    74 = "Other professional, scientific and technical activities"
    741 = "Specialized design activities"
    7410 = "Specialized design activities"
    742 = "Photographic activities"
    7420 = "Photographic activities"
    749 = "Other professional, scientific and technical activities n.e.c."
    7490 = "Other professional, scientific and technical activities n.e.c."
    75 = "Veterinary activities"
    750 = "Veterinary activities"
    7500 = "Veterinary activities"
    77 = "Rental and leasing activities"
    771 = "Renting and leasing of motor vehicles"
    7710 = "Renting and leasing of motor vehicles"
    772 = "Renting and leasing of personal and household goods"
    7721 = "Renting and leasing of recreational and sports goods"
    7722 = "Renting of video tapes and disks"
    7729 = "Renting and leasing of other personal and household goods"
    773 = "Renting and leasing of other machinery, equipment and tangible goods"
    7730 = "Renting and leasing of other machinery, equipment and tangible goods"
    774 = "Leasing of intellectual property and similar products, except copyrighted works"
    7740 = "Leasing of intellectual property and similar products, except copyrighted works"
    78 = "Employment activities"
    781 = "Activities of employment placement agencies"
    7810 = "Activities of employment placement agencies"
    782 = "Temporary employment agency activities"
    7820 = "Temporary employment agency activities"
    783 = "Other human resources provision"
    7830 = "Other human resources provision"
    79 = "Travel agency, tour operator, reservation service and related activities"
    791 = "Travel agency and tour operator activities"
    7911 = "Travel agency activities"
    7912 = "Tour operator activities"
    799 = "Other reservation service and related activities"
    7990 = "Other reservation service and related activities"
    80 = "Security and investigation activities"
    801 = "Private security activities"
    8010 = "Private security activities"
    802 = "Security systems service activities"
    8020 = "Security systems service activities"
    803 = "Investigation activities"
    8030 = "Investigation activities"
    81 = "Services to buildings and landscape activities"
    811 = "Combined facilities support activities"
    8110 = "Combined facilities support activities"
    812 = "Cleaning activities"
    8121 = "General cleaning of buildings"
    8129 = "Other building and industrial cleaning activities"
    813 = "Landscape care and maintenance service activities"
    8130 = "Landscape care and maintenance service activities"
    82 = "Office administrative, office support and other business support activities"
    821 = "Office administrative and support activities"
    8211 = "Combined office administrative service activities"
    8219 = "Photocopying, document preparation and other specialized office support activities"
    822 = "Activities of call centres"
    8220 = "Activities of call centres"
    823 = "Organization of conventions and trade shows"
    8230 = "Organization of conventions and trade shows"
    829 = "Business support service activities n.e.c."
    8291 = "Activities of collection agencies and credit bureaus"
    8292 = "Packaging activities"
    8299 = "Other business support service activities n.e.c."
    84 = "Public administration and defence; compulsory social security"
    841 = "Administration of the State and the economic and social policy of the community"
    8411 = "General public administration activities"
    8412 = "Regulation of the act. of providing health care, education, cultural serv. and other social serv., excl. social security"
    8413 = "Regulation of and contribution to more efficient operation of businesses"
    842 = "Provision of services to the community as a whole"
    8421 = "Foreign affairs"
    8422 = "Defence activities"
    8423 = "Public order and safety activities"
    843 = "Compulsory social security activities"
    8430 = "Compulsory social security activities"
    85 = "Education"
    851 = "Pre-primary and primary education"
    8510 = "Pre-primary and primary education"
    852 = "Secondary education"
    8521 = "General secondary education"
    8522 = "Technical and vocational secondary education"
    853 = "Higher education"
    8530 = "Higher education"
    854 = "Other education"
    8541 = "Sports and recreation education"
    8542 = "Cultural education"
    8549 = "Other education n.e.c."
    855 = "Educational support activities"
    8550 = "Educational support activities"
    86 = "Human health activities"
    861 = "Hospital activities"
    8610 = "Hospital activities"
    862 = "Medical and dental practice activities"
    8620 = "Medical and dental practice activities"
    869 = "Other human health activities"
    8690 = "Other human health activities"
    87 = "Residential care activities"
    871 = "Residential nursing care facilities"
    8710 = "Residential nursing care facilities"
    872 = "Residential care activities for mental retardation, mental health and substance abuse"
    8720 = "Residential care activities for mental retardation, mental health and substance abuse"
    873 = "Residential care activities for the elderly and disabled"
    8730 = "Residential care activities for the elderly and disabled"
    879 = "Other residential care activities"
    8790 = "Other residential care activities"
    88 = "Social work activities without accommodation"
    881 = "Social work activities without accommodation for the elderly and disabled"
    8810 = "Social work activities without accommodation for the elderly and disabled"
    889 = "Other social work activities without accommodation"
    8890 = "Other social work activities without accommodation"
    90 = "Creative, arts and entertainment activities"
    900 = "Creative, arts and entertainment activities"
    9000 = "Creative, arts and entertainment activities"
    91 = "Libraries, archives, museums and other cultural activities"
    910 = "Libraries, archives, museums and other cultural activities"
    9101 = "Library and archives activities"
    9102 = "Museums activities and operation of historical sites and buildings"
    9103 = "Botanical and zoological gardens and nature reserves activities"
    92 = "Gambling and betting activities"
    920 = "Gambling and betting activities"
    9200 = "Gambling and betting activities"
    93 = "Sports activities and amusement and recreation activities"
    931 = "Sports activities"
    9311 = "Operation of sports facilities"
    9312 = "Activities of sports clubs"
    9319 = "Other sports activities"
    932 = "Other amusement and recreation activities"
    9321 = "Activities of amusement parks and theme parks"
    9329 = "Other amusement and recreation activities n.e.c."
    94 = "Activities of membership organizations"
    941 = "Activities of business, employers and professional membership organizations"
    9411 = "Activities of business and employers membership organizations"
    9412 = "Activities of professional membership organizations"
    942 = "Activities of trade unions"
    9420 = "Activities of trade unions"
    949 = "Activities of other membership organizations"
    9491 = "Activities of religious organizations"
    9492 = "Activities of political organizations"
    9499 = "Activities of other membership organizations n.e.c."
    95 = "Repair of computers and personal and household goods"
    951 = "Repair of computers and communication equipment"
    9511 = "Repair of computers and peripheral equipment"
    9512 = "Repair of communication equipment"
    952 = "Repair of personal and household goods"
    9521 = "Repair of consumer electronics"
    9522 = "Repair of household appliances and home and garden equipment"
    9523 = "Repair of footwear and leather goods"
    9524 = "Repair of furniture and home furnishings"
    9529 = "Repair of other personal and household goods"
    96 = "Other personal service activities"
    960 = "Other personal service activities"
    9601 = "Washing and (dry-) cleaning of textile and fur products"
    9602 = "Hairdressing and other beauty treatment"
    9603 = "Funeral and related activities"
    9609 = "Other personal service activities n.e.c."
    97 = "Activities of households as employers of domestic personnel"
    970 = "Activities of households as employers of domestic personnel"
    9700 = "Activities of households as employers of domestic personnel"
    98 = "Undifferentiated goods- and services-producing activities of private households for own use"
    981 = "Undifferentiated goods-producing activities of private households for own use"
    9810 = "Undifferentiated goods-producing activities of private households for own use"
    982 = "Undifferentiated service-producing activities of private households for own use"
    9820 = "Undifferentiated service-producing activities of private households for own use"
    99 = "Activities of extraterritorial organizations and bodies"
    990 = "Activities of extraterritorial organizations and bodies"
    9900 = "Activities of extraterritorial organizations and bodies"
    9995 = "No paid work for past 5 years"
    9996 = "Valid skip"
    9997 = "Don't know"
    9998 = "Refused"
    9999 = "Not stated or inferred"
    A = "Agriculture, forestry and fishing"
    B = "Mining and quarrying"
    C = "Manufacturing"
    D = "Electricity, gas, steam and air conditioning supply"
    E = "Water supply; sewerage, waste management and remediation activities"
    F = "Construction"
    G = "Wholesale and retail trade; repair of motor vehicles and motorcycles"
    H = "Transportation and storage"
    I = "Accommodation and food service activities"
    J = "Information and communication"
    K = "Financial and insurance activities"
    L = "Real estate activities"
    M = "Professional, scientific and technical activities"
    N = "Administrative and support service activities"
    O = "Public administration and defence; compulsory social security"
    P = "Education"
    Q = "Human health and social work activities"
    R = "Arts, entertainment and recreation"
    S = "Other service activities"
    T = "Activities of households as employers; undifferentiated goods- and services-producing activ. of households for own use"
    U = "Activities of extraterritorial organizations and bodies"
  ;
  VALUE $ISIC4_LUSP_C
    01 = "Crop and animal production, hunting and related service activities"
    011 = "Growing of non-perennial crops"
    0111 = "Growing of cereals (except rice), leguminous crops and oil seeds"
    0112 = "Growing of rice"
    0113 = "Growing of vegetables and melons, roots and tubers"
    0114 = "Growing of sugar cane"
    0115 = "Growing of tobacco"
    0116 = "Growing of fibre crops"
    0119 = "Growing of other non-perennial crops"
    012 = "Growing of perennial crops"
    0121 = "Growing of grapes"
    0122 = "Growing of tropical and subtropical fruits"
    0123 = "Growing of citrus fruits"
    0124 = "Growing of pome fruits and stone fruits"
    0125 = "Growing of other tree and bush fruits and nuts"
    0126 = "Growing of oleaginous fruits"
    0127 = "Growing of beverage crops"
    0128 = "Growing of spices, aromatic, drug and pharmaceutical crops"
    0129 = "Growing of other perennial crops"
    013 = "Plant propagation"
    0130 = "Plant propagation"
    014 = "Animal production"
    0141 = "Raising of cattle and buffaloes"
    0142 = "Raising of horses and other equines"
    0143 = "Raising of camels and camelids"
    0144 = "Raising of sheep and goats"
    0145 = "Raising of swine/pigs"
    0146 = "Raising of poultry"
    0149 = "Raising of other animals"
    015 = "Mixed farming"
    0150 = "Mixed farming"
    016 = "Support activities to agriculture and post-harvest crop activities"
    0161 = "Support activities for crop production"
    0162 = "Support activities for animal production"
    0163 = "Post-harvest crop activities"
    0164 = "Seed processing for propagation"
    017 = "Hunting, trapping and related service activities"
    0170 = "Hunting, trapping and related service activities"
    02 = "Forestry and logging"
    021 = "Silviculture and other forestry activities"
    0210 = "Silviculture and other forestry activities"
    022 = "Logging"
    0220 = "Logging"
    023 = "Gathering of non-wood forest products"
    0230 = "Gathering of non-wood forest products"
    024 = "Support services to forestry"
    0240 = "Support services to forestry"
    03 = "Fishing and aquaculture"
    031 = "Fishing"
    0311 = "Marine fishing"
    0312 = "Freshwater fishing"
    032 = "Aquaculture"
    0321 = "Marine aquaculture"
    0322 = "Freshwater aquaculture"
    05 = "Mining of coal and lignite"
    051 = "Mining of hard coal"
    0510 = "Mining of hard coal"
    052 = "Mining of lignite"
    0520 = "Mining of lignite"
    06 = "Extraction of crude petroleum and natural gas"
    061 = "Extraction of crude petroleum"
    0610 = "Extraction of crude petroleum"
    062 = "Extraction of natural gas"
    0620 = "Extraction of natural gas"
    07 = "Mining of metal ores"
    071 = "Mining of iron ores"
    0710 = "Mining of iron ores"
    072 = "Mining of non-ferrous metal ores"
    0721 = "Mining of uranium and thorium ores"
    0729 = "Mining of other non-ferrous metal ores"
    08 = "Other mining and quarrying"
    081 = "Quarrying of stone, sand and clay"
    0810 = "Quarrying of stone, sand and clay"
    089 = "Mining and quarrying n.e.c."
    0891 = "Mining of chemical and fertilizer minerals"
    0892 = "Extraction of peat"
    0893 = "Extraction of salt"
    0899 = "Other mining and quarrying n.e.c."
    09 = "Mining support service activities"
    091 = "Support activities for petroleum and natural gas extraction"
    0910 = "Support activities for petroleum and natural gas extraction"
    099 = "Support activities for other mining and quarrying"
    0990 = "Support activities for other mining and quarrying"
    10 = "Manufacture of food products"
    101 = "Processing and preserving of meat"
    1010 = "Processing and preserving of meat"
    102 = "Processing and preserving of fish, crustaceans and molluscs"
    1020 = "Processing and preserving of fish, crustaceans and molluscs"
    103 = "Processing and preserving of fruit and vegetables"
    1030 = "Processing and preserving of fruit and vegetables"
    104 = "Manufacture of vegetable and animal oils and fats"
    1040 = "Manufacture of vegetable and animal oils and fats"
    105 = "Manufacture of dairy products"
    1050 = "Manufacture of dairy products"
    106 = "Manufacture of grain mill products, starches and starch products"
    1061 = "Manufacture of grain mill products"
    1062 = "Manufacture of starches and starch products"
    107 = "Manufacture of other food products"
    1071 = "Manufacture of bakery products"
    1072 = "Manufacture of sugar"
    1073 = "Manufacture of cocoa, chocolate and sugar confectionery"
    1074 = "Manufacture of macaroni, noodles, couscous and similar farinaceous products"
    1075 = "Manufacture of prepared meals and dishes"
    1079 = "Manufacture of other food products n.e.c."
    108 = "Manufacture of prepared animal feeds"
    1080 = "Manufacture of prepared animal feeds"
    11 = "Manufacture of beverages"
    110 = "Manufacture of beverages"
    1101 = "Distilling, rectifying and blending of spirits"
    1102 = "Manufacture of wines"
    1103 = "Manufacture of malt liquors and malt"
    1104 = "Manufacture of soft drinks; production of mineral waters and other bottled waters"
    12 = "Manufacture of tobacco products"
    120 = "Manufacture of tobacco products"
    1200 = "Manufacture of tobacco products"
    13 = "Manufacture of textiles"
    131 = "Spinning, weaving and finishing of textiles"
    1311 = "Preparation and spinning of textile fibres"
    1312 = "Weaving of textiles"
    1313 = "Finishing of textiles"
    139 = "Manufacture of other textiles"
    1391 = "Manufacture of knitted and crocheted fabrics"
    1392 = "Manufacture of made-up textile articles, except apparel"
    1393 = "Manufacture of carpets and rugs"
    1394 = "Manufacture of cordage, rope, twine and netting"
    1399 = "Manufacture of other textiles n.e.c."
    14 = "Manufacture of wearing apparel"
    141 = "Manufacture of wearing apparel, except fur apparel"
    1410 = "Manufacture of wearing apparel, except fur apparel"
    142 = "Manufacture of articles of fur"
    1420 = "Manufacture of articles of fur"
    143 = "Manufacture of knitted and crocheted apparel"
    1430 = "Manufacture of knitted and crocheted apparel"
    15 = "Manufacture of leather and related products"
    151 = "Tanning and dressing of leather; manufacture of luggage, handbags, saddlery and harness; dressing and dyeing of fur"
    1511 = "Tanning and dressing of leather; dressing and dyeing of fur"
    1512 = "Manufacture of luggage, handbags and the like, saddlery and harness"
    152 = "Manufacture of footwear"
    1520 = "Manufacture of footwear"
    16 = "Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plait"
    161 = "Sawmilling and planing of wood"
    1610 = "Sawmilling and planing of wood"
    162 = "Manufacture of products of wood, cork, straw and plaiting materials"
    1621 = "Manufacture of veneer sheets and wood-based panels"
    1622 = "Manufacture of builders' carpentry and joinery"
    1623 = "Manufacture of wooden containers"
    1629 = "Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials"
    17 = "Manufacture of paper and paper products"
    170 = "Manufacture of paper and paper products"
    1701 = "Manufacture of pulp, paper and paperboard"
    1702 = "Manufacture of corrugated paper and paperboard and of containers of paper and paperboard"
    1709 = "Manufacture of other articles of paper and paperboard"
    18 = "Printing and reproduction of recorded media"
    181 = "Printing and service activities related to printing"
    1811 = "Printing"
    1812 = "Service activities related to printing"
    182 = "Reproduction of recorded media"
    1820 = "Reproduction of recorded media"
    19 = "Manufacture of coke and refined petroleum products"
    191 = "Manufacture of coke oven products"
    1910 = "Manufacture of coke oven products"
    192 = "Manufacture of refined petroleum products"
    1920 = "Manufacture of refined petroleum products"
    20 = "Manufacture of chemicals and chemical products"
    201 = "Manufacture of basic chemicals, fertilizers and nitrogen compounds, plastics and synthetic rubber in primary forms"
    2011 = "Manufacture of basic chemicals"
    2012 = "Manufacture of fertilizers and nitrogen compounds"
    2013 = "Manufacture of plastics and synthetic rubber in primary forms"
    202 = "Manufacture of other chemical products"
    2021 = "Manufacture of pesticides and other agrochemical products"
    2022 = "Manufacture of paints, varnishes and similar coatings, printing ink and mastics"
    2023 = "Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations"
    2029 = "Manufacture of other chemical products n.e.c."
    203 = "Manufacture of man-made fibres"
    2030 = "Manufacture of man-made fibres"
    21 = "Manufacture of basic pharmaceutical products and pharmaceutical preparations"
    210 = "Manufacture of pharmaceuticals, medicinal chemical and botanical products"
    2100 = "Manufacture of pharmaceuticals, medicinal chemical and botanical products"
    22 = "Manufacture of rubber and plastics products"
    221 = "Manufacture of rubber products"
    2211 = "Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres"
    2219 = "Manufacture of other rubber products"
    222 = "Manufacture of plastics products"
    2220 = "Manufacture of plastics products"
    23 = "Manufacture of other non-metallic mineral products"
    231 = "Manufacture of glass and glass products"
    2310 = "Manufacture of glass and glass products"
    239 = "Manufacture of non-metallic mineral products n.e.c."
    2391 = "Manufacture of refractory products"
    2392 = "Manufacture of clay building materials"
    2393 = "Manufacture of other porcelain and ceramic products"
    2394 = "Manufacture of cement, lime and plaster"
    2395 = "Manufacture of articles of concrete, cement and plaster"
    2396 = "Cutting, shaping and finishing of stone"
    2399 = "Manufacture of other non-metallic mineral products n.e.c."
    24 = "Manufacture of basic metals"
    241 = "Manufacture of basic iron and steel"
    2410 = "Manufacture of basic iron and steel"
    242 = "Manufacture of basic precious and other non-ferrous metals"
    2420 = "Manufacture of basic precious and other non-ferrous metals"
    243 = "Casting of metals"
    2431 = "Casting of iron and steel"
    2432 = "Casting of non-ferrous metals"
    25 = "Manufacture of fabricated metal products, except machinery and equipment"
    251 = "Manufacture of structural metal products, tanks, reservoirs and steam generators"
    2511 = "Manufacture of structural metal products"
    2512 = "Manufacture of tanks, reservoirs and containers of metal"
    2513 = "Manufacture of steam generators, except central heating hot water boilers"
    252 = "Manufacture of weapons and ammunition"
    2520 = "Manufacture of weapons and ammunition"
    259 = "Manufacture of other fabricated metal products; metalworking service activities"
    2591 = "Forging, pressing, stamping and roll-forming of metal; powder metallurgy"
    2592 = "Treatment and coating of metals; machining"
    2593 = "Manufacture of cutlery, hand tools and general hardware"
    2599 = "Manufacture of other fabricated metal products n.e.c."
    26 = "Manufacture of computer, electronic and optical products"
    261 = "Manufacture of electronic components and boards"
    2610 = "Manufacture of electronic components and boards"
    262 = "Manufacture of computers and peripheral equipment"
    2620 = "Manufacture of computers and peripheral equipment"
    263 = "Manufacture of communication equipment"
    2630 = "Manufacture of communication equipment"
    264 = "Manufacture of consumer electronics"
    2640 = "Manufacture of consumer electronics"
    265 = "Manufacture of measuring, testing, navigating and control equipment; watches and clocks"
    2651 = "Manufacture of measuring, testing, navigating and control equipment"
    2652 = "Manufacture of watches and clocks"
    266 = "Manufacture of irradiation, electromedical and electrotherapeutic equipment"
    2660 = "Manufacture of irradiation, electromedical and electrotherapeutic equipment"
    267 = "Manufacture of optical instruments and photographic equipment"
    2670 = "Manufacture of optical instruments and photographic equipment"
    268 = "Manufacture of magnetic and optical media"
    2680 = "Manufacture of magnetic and optical media"
    27 = "Manufacture of electrical equipment"
    271 = "Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus"
    2710 = "Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus"
    272 = "Manufacture of batteries and accumulators"
    2720 = "Manufacture of batteries and accumulators"
    273 = "Manufacture of wiring and wiring devices"
    2731 = "Manufacture of fibre optic cables"
    2732 = "Manufacture of other electronic and electric wires and cables"
    2733 = "Manufacture of wiring devices"
    274 = "Manufacture of electric lighting equipment"
    2740 = "Manufacture of electric lighting equipment"
    275 = "Manufacture of domestic appliances"
    2750 = "Manufacture of domestic appliances"
    279 = "Manufacture of other electrical equipment"
    2790 = "Manufacture of other electrical equipment"
    28 = "Manufacture of machinery and equipment n.e.c."
    281 = "Manufacture of general-purpose machinery"
    2811 = "Manufacture of engines and turbines, except aircraft, vehicle and cycle engines"
    2812 = "Manufacture of fluid power equipment"
    2813 = "Manufacture of other pumps, compressors, taps and valves"
    2814 = "Manufacture of bearings, gears, gearing and driving elements"
    2815 = "Manufacture of ovens, furnaces and furnace burners"
    2816 = "Manufacture of lifting and handling equipment"
    2817 = "Manufacture of office machinery and equipment (except computers and peripheral equipment)"
    2818 = "Manufacture of power-driven hand tools"
    2819 = "Manufacture of other general-purpose machinery"
    282 = "Manufacture of special-purpose machinery"
    2821 = "Manufacture of agricultural and forestry machinery"
    2822 = "Manufacture of metal-forming machinery and machine tools"
    2823 = "Manufacture of machinery for metallurgy"
    2824 = "Manufacture of machinery for mining, quarrying and construction"
    2825 = "Manufacture of machinery for food, beverage and tobacco processing"
    2826 = "Manufacture of machinery for textile, apparel and leather production"
    2829 = "Manufacture of other special-purpose machinery"
    29 = "Manufacture of motor vehicles, trailers and semi-trailers"
    291 = "Manufacture of motor vehicles"
    2910 = "Manufacture of motor vehicles"
    292 = "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers"
    2920 = "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers"
    293 = "Manufacture of parts and accessories for motor vehicles"
    2930 = "Manufacture of parts and accessories for motor vehicles"
    30 = "Manufacture of other transport equipment"
    301 = "Building of ships and boats"
    3011 = "Building of ships and floating structures"
    3012 = "Building of pleasure and sporting boats"
    302 = "Manufacture of railway locomotives and rolling stock"
    3020 = "Manufacture of railway locomotives and rolling stock"
    303 = "Manufacture of air and spacecraft and related machinery"
    3030 = "Manufacture of air and spacecraft and related machinery"
    304 = "Manufacture of military fighting vehicles"
    3040 = "Manufacture of military fighting vehicles"
    309 = "Manufacture of transport equipment n.e.c."
    3091 = "Manufacture of motorcycles"
    3092 = "Manufacture of bicycles and invalid carriages"
    3099 = "Manufacture of other transport equipment n.e.c."
    31 = "Manufacture of furniture"
    310 = "Manufacture of furniture"
    3100 = "Manufacture of furniture"
    32 = "Other manufacturing"
    321 = "Manufacture of jewellery, bijouterie and related articles"
    3211 = "Manufacture of jewellery and related articles"
    3212 = "Manufacture of imitation jewellery and related articles"
    322 = "Manufacture of musical instruments"
    3220 = "Manufacture of musical instruments"
    323 = "Manufacture of sports goods"
    3230 = "Manufacture of sports goods"
    324 = "Manufacture of games and toys"
    3240 = "Manufacture of games and toys"
    325 = "Manufacture of medical and dental instruments and supplies"
    3250 = "Manufacture of medical and dental instruments and supplies"
    329 = "Other manufacturing n.e.c."
    3290 = "Other manufacturing n.e.c."
    33 = "Repair and installation of machinery and equipment"
    331 = "Repair of fabricated metal products, machinery and equipment"
    3311 = "Repair of fabricated metal products"
    3312 = "Repair of machinery"
    3313 = "Repair of electronic and optical equipment"
    3314 = "Repair of electrical equipment"
    3315 = "Repair of transport equipment, except motor vehicles"
    3319 = "Repair of other equipment"
    332 = "Installation of industrial machinery and equipment"
    3320 = "Installation of industrial machinery and equipment"
    35 = "Electricity, gas, steam and air conditioning supply"
    351 = "Electric power generation, transmission and distribution"
    3510 = "Electric power generation, transmission and distribution"
    352 = "Manufacture of gas; distribution of gaseous fuels through mains"
    3520 = "Manufacture of gas; distribution of gaseous fuels through mains"
    353 = "Steam and air conditioning supply"
    3530 = "Steam and air conditioning supply"
    36 = "Water collection, treatment and supply"
    360 = "Water collection, treatment and supply"
    3600 = "Water collection, treatment and supply"
    37 = "Sewerage"
    370 = "Sewerage"
    3700 = "Sewerage"
    38 = "Waste collection, treatment and disposal activities; materials recovery"
    381 = "Waste collection"
    3811 = "Collection of non-hazardous waste"
    3812 = "Collection of hazardous waste"
    382 = "Waste treatment and disposal"
    3821 = "Treatment and disposal of non-hazardous waste"
    3822 = "Treatment and disposal of hazardous waste"
    383 = "Materials recovery"
    3830 = "Materials recovery"
    39 = "Remediation activities and other waste management services"
    390 = "Remediation activities and other waste management services"
    3900 = "Remediation activities and other waste management services"
    41 = "Construction of buildings"
    410 = "Construction of buildings"
    4100 = "Construction of buildings"
    42 = "Civil engineering"
    421 = "Construction of roads and railways"
    4210 = "Construction of roads and railways"
    422 = "Construction of utility projects"
    4220 = "Construction of utility projects"
    429 = "Construction of other civil engineering projects"
    4290 = "Construction of other civil engineering projects"
    43 = "Specialized construction activities"
    431 = "Demolition and site preparation"
    4311 = "Demolition"
    4312 = "Site preparation"
    432 = "Electrical, plumbing and other construction installation activities"
    4321 = "Electrical installation"
    4322 = "Plumbing, heat and air-conditioning installation"
    4329 = "Other construction installation"
    433 = "Building completion and finishing"
    4330 = "Building completion and finishing"
    439 = "Other specialized construction activities"
    4390 = "Other specialized construction activities"
    45 = "Wholesale and retail trade and repair of motor vehicles and motorcycles"
    451 = "Sale of motor vehicles"
    4510 = "Sale of motor vehicles"
    452 = "Maintenance and repair of motor vehicles"
    4520 = "Maintenance and repair of motor vehicles"
    453 = "Sale of motor vehicle parts and accessories"
    4530 = "Sale of motor vehicle parts and accessories"
    454 = "Sale, maintenance and repair of motorcycles and related parts and accessories"
    4540 = "Sale, maintenance and repair of motorcycles and related parts and accessories"
    46 = "Wholesale trade, except of motor vehicles and motorcycles"
    461 = "Wholesale on a fee or contract basis"
    4610 = "Wholesale on a fee or contract basis"
    462 = "Wholesale of agricultural raw materials and live animals"
    4620 = "Wholesale of agricultural raw materials and live animals"
    463 = "Wholesale of food, beverages and tobacco"
    4630 = "Wholesale of food, beverages and tobacco"
    464 = "Wholesale of household goods"
    4641 = "Wholesale of textiles, clothing and footwear"
    4649 = "Wholesale of other household goods"
    465 = "Wholesale of machinery, equipment and supplies"
    4651 = "Wholesale of computers, computer peripheral equipment and software"
    4652 = "Wholesale of electronic and telecommunications equipment and parts"
    4653 = "Wholesale of agricultural machinery, equipment and supplies"
    4659 = "Wholesale of other machinery and equipment"
    466 = "Other specialized wholesale"
    4661 = "Wholesale of solid, liquid and gaseous fuels and related products"
    4662 = "Wholesale of metals and metal ores"
    4663 = "Wholesale of construction materials, hardware, plumbing and heating equipment and supplies"
    4669 = "Wholesale of waste and scrap and other products n.e.c."
    469 = "Non-specialized wholesale trade"
    4690 = "Non-specialized wholesale trade"
    47 = "Retail trade, except of motor vehicles and motorcycles"
    471 = "Retail sale in non-specialized stores"
    4711 = "Retail sale in non-specialized stores with food, beverages or tobacco predominating"
    4719 = "Other retail sale in non-specialized stores"
    472 = "Retail sale of food, beverages and tobacco in specialized stores"
    4721 = "Retail sale of food in specialized stores"
    4722 = "Retail sale of beverages in specialized stores"
    4723 = "Retail sale of tobacco products in specialized stores"
    473 = "Retail sale of automotive fuel in specialized stores"
    4730 = "Retail sale of automotive fuel in specialized stores"
    474 = "Retail sale of information and communications equipment in specialized stores"
    4741 = "Retail sale of computers, peripheral units, software and telecommunications equipment in specialized stores"
    4742 = "Retail sale of audio and video equipment in specialized stores"
    475 = "Retail sale of other household equipment in specialized stores"
    4751 = "Retail sale of textiles in specialized stores"
    4752 = "Retail sale of hardware, paints and glass in specialized stores"
    4753 = "Retail sale of carpets, rugs, wall and floor coverings in specialized stores"
    4759 = "Retail sale of electrical household appliances, furniture, lighting equipm. and other household articles in spec. stores"
    476 = "Retail sale of cultural and recreation goods in specialized stores"
    4761 = "Retail sale of books, newspapers and stationary in specialized stores"
    4762 = "Retail sale of music and video recordings in specialized stores"
    4763 = "Retail sale of sporting equipment in specialized stores"
    4764 = "Retail sale of games and toys in specialized stores"
    477 = "Retail sale of other goods in specialized stores"
    4771 = "Retail sale of clothing, footwear and leather articles in specialized stores"
    4772 = "Retail sale of pharmaceutical and medical goods, cosmetic and toilet articles in specialized stores"
    4773 = "Other retail sale of new goods in specialized stores"
    4774 = "Retail sale of second-hand goods"
    478 = "Retail sale via stalls and markets"
    4781 = "Retail sale via stalls and markets of food, beverages and tobacco products"
    4782 = "Retail sale via stalls and markets of textiles, clothing and footwear"
    4789 = "Retail sale via stalls and markets of other goods"
    479 = "Retail trade not in stores, stalls or markets"
    4791 = "Retail sale via mail order houses or via Internet"
    4799 = "Other retail sale not in stores, stalls or markets"
    49 = "Land transport and transport via pipelines"
    491 = "Transport via railways"
    4911 = "Passenger rail transport, interurban"
    4912 = "Freight rail transport"
    492 = "Other land transport"
    4921 = "Urban and suburban passenger land transport"
    4922 = "Other passenger land transport"
    4923 = "Freight transport by road"
    493 = "Transport via pipeline"
    4930 = "Transport via pipeline"
    50 = "Water transport"
    501 = "Sea and coastal water transport"
    5011 = "Sea and coastal passenger water transport"
    5012 = "Sea and coastal freight water transport"
    502 = "Inland water transport"
    5021 = "Inland passenger water transport"
    5022 = "Inland freight water transport"
    51 = "Air transport"
    511 = "Passenger air transport"
    5110 = "Passenger air transport"
    512 = "Freight air transport"
    5120 = "Freight air transport"
    52 = "Warehousing and support activities for transportation"
    521 = "Warehousing and storage"
    5210 = "Warehousing and storage"
    522 = "Support activities for transportation"
    5221 = "Service activities incidental to land transportation"
    5222 = "Service activities incidental to water transportation"
    5223 = "Service activities incidental to air transportation"
    5224 = "Cargo handling"
    5229 = "Other transportation support activities"
    53 = "Postal and courier activities"
    531 = "Postal activities"
    5310 = "Postal activities"
    532 = "Courier activities"
    5320 = "Courier activities"
    55 = "Accommodation"
    551 = "Short term accommodation activities"
    5510 = "Short term accommodation activities"
    552 = "Camping grounds, recreational vehicle parks and trailer parks"
    5520 = "Camping grounds, recreational vehicle parks and trailer parks"
    559 = "Other accommodation"
    5590 = "Other accommodation"
    56 = "Food and beverage service activities"
    561 = "Restaurants and mobile food service activities"
    5610 = "Restaurants and mobile food service activities"
    562 = "Event catering and other food service activities"
    5621 = "Event catering"
    5629 = "Other food service activities"
    563 = "Beverage serving activities"
    5630 = "Beverage serving activities"
    58 = "Publishing activities"
    581 = "Publishing of books, periodicals and other publishing activities"
    5811 = "Book publishing"
    5812 = "Publishing of directories and mailing lists"
    5813 = "Publishing of newspapers, journals and periodicals"
    5819 = "Other publishing activities"
    582 = "Software publishing"
    5820 = "Software publishing"
    59 = "Motion picture, video and television programme production, sound recording and music publishing activities"
    591 = "Motion picture, video and television programme activities"
    5911 = "Motion picture, video and television programme production activities"
    5912 = "Motion picture, video and television programme post-production activities"
    5913 = "Motion picture, video and television programme distribution activities"
    5914 = "Motion picture projection activities"
    592 = "Sound recording and music publishing activities"
    5920 = "Sound recording and music publishing activities"
    60 = "Programming and broadcasting activities"
    601 = "Radio broadcasting"
    6010 = "Radio broadcasting"
    602 = "Television programming and broadcasting activities"
    6020 = "Television programming and broadcasting activities"
    61 = "Telecommunications"
    611 = "Wired telecommunications activities"
    6110 = "Wired telecommunications activities"
    612 = "Wireless telecommunications activities"
    6120 = "Wireless telecommunications activities"
    613 = "Satellite telecommunications activities"
    6130 = "Satellite telecommunications activities"
    619 = "Other telecommunications activities"
    6190 = "Other telecommunications activities"
    62 = "Computer programming, consultancy and related activities"
    620 = "Computer programming, consultancy and related activities"
    6201 = "Computer programming activities"
    6202 = "Computer consultancy and computer facilities management activities"
    6209 = "Other information technology and computer service activities"
    63 = "Information service activities"
    631 = "Data processing, hosting and related activities; web portals"
    6311 = "Data processing, hosting and related activities"
    6312 = "Web portals"
    639 = "Other information service activities"
    6391 = "News agency activities"
    6399 = "Other information service activities n.e.c."
    64 = "Financial service activities, except insurance and pension funding"
    641 = "Monetary intermediation"
    6411 = "Central banking"
    6419 = "Other monetary intermediation"
    642 = "Activities of holding companies"
    6420 = "Activities of holding companies"
    643 = "Trusts, funds and similar financial entities"
    6430 = "Trusts, funds and similar financial entities"
    649 = "Other financial service activities, except insurance and pension funding activities"
    6491 = "Financial leasing"
    6492 = "Other credit granting"
    6499 = "Other financial service activities, except insurance and pension funding activities, n.e.c."
    65 = "Insurance, reinsurance and pension funding, except compulsory social security"
    651 = "Insurance"
    6511 = "Life insurance"
    6512 = "Non-life insurance"
    652 = "Reinsurance"
    6520 = "Reinsurance"
    653 = "Pension funding"
    6530 = "Pension funding"
    66 = "Activities auxiliary to financial service and insurance activities"
    661 = "Activities auxiliary to financial service activities, except insurance and pension funding"
    6611 = "Administration of financial markets"
    6612 = "Security and commodity contracts brokerage"
    6619 = "Other activities auxiliary to financial service activities"
    662 = "Activities auxiliary to insurance and pension funding"
    6621 = "Risk and damage evaluation"
    6622 = "Activities of insurance agents and brokers"
    6629 = "Other activities auxiliary to insurance and pension funding"
    663 = "Fund management activities"
    6630 = "Fund management activities"
    68 = "Real estate activities"
    681 = "Real estate activities with own or leased property"
    6810 = "Real estate activities with own or leased property"
    682 = "Real estate activities on a fee or contract basis"
    6820 = "Real estate activities on a fee or contract basis"
    69 = "Legal and accounting activities"
    691 = "Legal activities"
    6910 = "Legal activities"
    692 = "Accounting, bookkeeping and auditing activities; tax consultancy"
    6920 = "Accounting, bookkeeping and auditing activities; tax consultancy"
    70 = "Activities of head offices; management consultancy activities"
    701 = "Activities of head offices"
    7010 = "Activities of head offices"
    702 = "Management consultancy activities"
    7020 = "Management consultancy activities"
    71 = "Architectural and engineering activities; technical testing and analysis"
    711 = "Architectural and engineering activities and related technical consultancy"
    7110 = "Architectural and engineering activities and related technical consultancy"
    712 = "Technical testing and analysis"
    7120 = "Technical testing and analysis"
    72 = "Scientific research and development"
    721 = "Research and experimental development on natural sciences and engineering"
    7210 = "Research and experimental development on natural sciences and engineering"
    722 = "Research and experimental development on social sciences and humanities"
    7220 = "Research and experimental development on social sciences and humanities"
    73 = "Advertising and market research"
    731 = "Advertising"
    7310 = "Advertising"
    732 = "Market research and public opinion polling"
    7320 = "Market research and public opinion polling"
    74 = "Other professional, scientific and technical activities"
    741 = "Specialized design activities"
    7410 = "Specialized design activities"
    742 = "Photographic activities"
    7420 = "Photographic activities"
    749 = "Other professional, scientific and technical activities n.e.c."
    7490 = "Other professional, scientific and technical activities n.e.c."
    75 = "Veterinary activities"
    750 = "Veterinary activities"
    7500 = "Veterinary activities"
    77 = "Rental and leasing activities"
    771 = "Renting and leasing of motor vehicles"
    7710 = "Renting and leasing of motor vehicles"
    772 = "Renting and leasing of personal and household goods"
    7721 = "Renting and leasing of recreational and sports goods"
    7722 = "Renting of video tapes and disks"
    7729 = "Renting and leasing of other personal and household goods"
    773 = "Renting and leasing of other machinery, equipment and tangible goods"
    7730 = "Renting and leasing of other machinery, equipment and tangible goods"
    774 = "Leasing of intellectual property and similar products, except copyrighted works"
    7740 = "Leasing of intellectual property and similar products, except copyrighted works"
    78 = "Employment activities"
    781 = "Activities of employment placement agencies"
    7810 = "Activities of employment placement agencies"
    782 = "Temporary employment agency activities"
    7820 = "Temporary employment agency activities"
    783 = "Other human resources provision"
    7830 = "Other human resources provision"
    79 = "Travel agency, tour operator, reservation service and related activities"
    791 = "Travel agency and tour operator activities"
    7911 = "Travel agency activities"
    7912 = "Tour operator activities"
    799 = "Other reservation service and related activities"
    7990 = "Other reservation service and related activities"
    80 = "Security and investigation activities"
    801 = "Private security activities"
    8010 = "Private security activities"
    802 = "Security systems service activities"
    8020 = "Security systems service activities"
    803 = "Investigation activities"
    8030 = "Investigation activities"
    81 = "Services to buildings and landscape activities"
    811 = "Combined facilities support activities"
    8110 = "Combined facilities support activities"
    812 = "Cleaning activities"
    8121 = "General cleaning of buildings"
    8129 = "Other building and industrial cleaning activities"
    813 = "Landscape care and maintenance service activities"
    8130 = "Landscape care and maintenance service activities"
    82 = "Office administrative, office support and other business support activities"
    821 = "Office administrative and support activities"
    8211 = "Combined office administrative service activities"
    8219 = "Photocopying, document preparation and other specialized office support activities"
    822 = "Activities of call centres"
    8220 = "Activities of call centres"
    823 = "Organization of conventions and trade shows"
    8230 = "Organization of conventions and trade shows"
    829 = "Business support service activities n.e.c."
    8291 = "Activities of collection agencies and credit bureaus"
    8292 = "Packaging activities"
    8299 = "Other business support service activities n.e.c."
    84 = "Public administration and defence; compulsory social security"
    841 = "Administration of the State and the economic and social policy of the community"
    8411 = "General public administration activities"
    8412 = "Regulation of the act. of providing health care, education, cultural serv. and other social serv., excl. social security"
    8413 = "Regulation of and contribution to more efficient operation of businesses"
    842 = "Provision of services to the community as a whole"
    8421 = "Foreign affairs"
    8422 = "Defence activities"
    8423 = "Public order and safety activities"
    843 = "Compulsory social security activities"
    8430 = "Compulsory social security activities"
    85 = "Education"
    851 = "Pre-primary and primary education"
    8510 = "Pre-primary and primary education"
    852 = "Secondary education"
    8521 = "General secondary education"
    8522 = "Technical and vocational secondary education"
    853 = "Higher education"
    8530 = "Higher education"
    854 = "Other education"
    8541 = "Sports and recreation education"
    8542 = "Cultural education"
    8549 = "Other education n.e.c."
    855 = "Educational support activities"
    8550 = "Educational support activities"
    86 = "Human health activities"
    861 = "Hospital activities"
    8610 = "Hospital activities"
    862 = "Medical and dental practice activities"
    8620 = "Medical and dental practice activities"
    869 = "Other human health activities"
    8690 = "Other human health activities"
    87 = "Residential care activities"
    871 = "Residential nursing care facilities"
    8710 = "Residential nursing care facilities"
    872 = "Residential care activities for mental retardation, mental health and substance abuse"
    8720 = "Residential care activities for mental retardation, mental health and substance abuse"
    873 = "Residential care activities for the elderly and disabled"
    8730 = "Residential care activities for the elderly and disabled"
    879 = "Other residential care activities"
    8790 = "Other residential care activities"
    88 = "Social work activities without accommodation"
    881 = "Social work activities without accommodation for the elderly and disabled"
    8810 = "Social work activities without accommodation for the elderly and disabled"
    889 = "Other social work activities without accommodation"
    8890 = "Other social work activities without accommodation"
    90 = "Creative, arts and entertainment activities"
    900 = "Creative, arts and entertainment activities"
    9000 = "Creative, arts and entertainment activities"
    91 = "Libraries, archives, museums and other cultural activities"
    910 = "Libraries, archives, museums and other cultural activities"
    9101 = "Library and archives activities"
    9102 = "Museums activities and operation of historical sites and buildings"
    9103 = "Botanical and zoological gardens and nature reserves activities"
    92 = "Gambling and betting activities"
    920 = "Gambling and betting activities"
    9200 = "Gambling and betting activities"
    93 = "Sports activities and amusement and recreation activities"
    931 = "Sports activities"
    9311 = "Operation of sports facilities"
    9312 = "Activities of sports clubs"
    9319 = "Other sports activities"
    932 = "Other amusement and recreation activities"
    9321 = "Activities of amusement parks and theme parks"
    9329 = "Other amusement and recreation activities n.e.c."
    94 = "Activities of membership organizations"
    941 = "Activities of business, employers and professional membership organizations"
    9411 = "Activities of business and employers membership organizations"
    9412 = "Activities of professional membership organizations"
    942 = "Activities of trade unions"
    9420 = "Activities of trade unions"
    949 = "Activities of other membership organizations"
    9491 = "Activities of religious organizations"
    9492 = "Activities of political organizations"
    9499 = "Activities of other membership organizations n.e.c."
    95 = "Repair of computers and personal and household goods"
    951 = "Repair of computers and communication equipment"
    9511 = "Repair of computers and peripheral equipment"
    9512 = "Repair of communication equipment"
    952 = "Repair of personal and household goods"
    9521 = "Repair of consumer electronics"
    9522 = "Repair of household appliances and home and garden equipment"
    9523 = "Repair of footwear and leather goods"
    9524 = "Repair of furniture and home furnishings"
    9529 = "Repair of other personal and household goods"
    96 = "Other personal service activities"
    960 = "Other personal service activities"
    9601 = "Washing and (dry-) cleaning of textile and fur products"
    9602 = "Hairdressing and other beauty treatment"
    9603 = "Funeral and related activities"
    9609 = "Other personal service activities n.e.c."
    97 = "Activities of households as employers of domestic personnel"
    970 = "Activities of households as employers of domestic personnel"
    9700 = "Activities of households as employers of domestic personnel"
    98 = "Undifferentiated goods- and services-producing activities of private households for own use"
    981 = "Undifferentiated goods-producing activities of private households for own use"
    9810 = "Undifferentiated goods-producing activities of private households for own use"
    982 = "Undifferentiated service-producing activities of private households for own use"
    9820 = "Undifferentiated service-producing activities of private households for own use"
    99 = "Activities of extraterritorial organizations and bodies"
    990 = "Activities of extraterritorial organizations and bodies"
    9900 = "Activities of extraterritorial organizations and bodies"
    9995 = "No paid work for past 5 years"
    9996 = "Valid skip"
    9997 = "Don't know"
    9998 = "Refused"
    9999 = "Not stated or inferred"
    A = "Agriculture, forestry and fishing"
    B = "Mining and quarrying"
    C = "Manufacturing"
    D = "Electricity, gas, steam and air conditioning supply"
    E = "Water supply; sewerage, waste management and remediation activities"
    F = "Construction"
    G = "Wholesale and retail trade; repair of motor vehicles and motorcycles"
    H = "Transportation and storage"
    I = "Accommodation and food service activities"
    J = "Information and communication"
    K = "Financial and insurance activities"
    L = "Real estate activities"
    M = "Professional, scientific and technical activities"
    N = "Administrative and support service activities"
    O = "Public administration and defence; compulsory social security"
    P = "Education"
    Q = "Human health and social work activities"
    R = "Arts, entertainment and recreation"
    S = "Other service activities"
    T = "Activities of households as employers; undifferentiated goods- and services-producing activ. of households for own use"
    U = "Activities of extraterritorial organizations and bodies"
  ;
  VALUE I_Q04B
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q04D
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q04H
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q04J
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q04L
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q04M
    1 = "Not at all"
    2 = "Very little"
    3 = "To some extent"
    4 = "To a high extent"
    5 = "To a very high extent"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06A
    1 = "Strongly agree"
    2 = "Agree"
    3 = "Neither agree nor disagree"
    4 = "Disagree"
    5 = "Strongly disagree"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSP1G
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSX1A
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSX1B
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSX1D
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSX1E
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q06DUSX1F
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q07A
    1 = "Strongly agree"
    2 = "Agree"
    3 = "Neither agree nor disagree"
    4 = "Disagree"
    5 = "Strongly disagree"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q07B
    1 = "Strongly agree"
    2 = "Agree"
    3 = "Neither agree nor disagree"
    4 = "Disagree"
    5 = "Strongly disagree"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q08USX1_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q08USX2_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q08USX3_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q08_
    1 = "Excellent"
    2 = "Very good"
    3 = "Good"
    4 = "Fair"
    5 = "Poor"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSP2G
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2A
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2B
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2D
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2E
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2F
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE I_Q10BUSX2H
    1 = "A lot"
    2 = "Some"
    3 = "A little"
    4 = "None"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_N05A2_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q02C
    1 = "Full-time employed (self-employed, employee)"
    2 = "Part-time employed (self-employed, employee)"
    3 = "Unemployed"
    4 = "Pupil, student"
    5 = "Apprentice, internship"
    6 = "In retirement or early retirement"
    7 = "Permanently disabled"
    8 = "In compulsory military or community service"
    9 = "Fulfilling domestic tasks or looking after children/family"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Other"
  ;
  VALUE J_Q03A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03B_C
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03CUS_C
    1 = "age 0-2"
    2 = "age 3-5"
    3 = "age 6-12"
    4 = "age 13-17"
    5 = "age 18+"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03C_C
    1 = "Aged 2 or younger"
    2 = "Aged 3-5"
    3 = "Aged 6-12"
    4 = "Aged 13 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03D1US_C
    1 = "age 0-2"
    2 = "age 3-5"
    3 = "age 6-12"
    4 = "age 13-17"
    5 = "age 18+"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03D1_C
    1 = "Aged 2 or younger"
    2 = "Aged 3-5"
    3 = "Aged 6-12"
    4 = "Aged 13 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03D2US_C
    1 = "age 0-2"
    2 = "age 3-5"
    3 = "age 6-12"
    4 = "age 13-17"
    5 = "age 18+"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q03D2_C
    1 = "Aged 2 or younger"
    2 = "Aged 3-5"
    3 = "Aged 6-12"
    4 = "Aged 13 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q04A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q04C1_C
    1 = "Aged 0-5"
    2 = "Aged 6-10"
    3 = "Aged 11-15"
    4 = "Aged 16-20"
    5 = "Aged 21-25"
    6 = "Aged 26-30"
    7 = "Aged 31-35"
    8 = "Aged 36-40"
    9 = "Aged 41 or older"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q04C2US_C
    1 = "1959 - 1985"
    2 = "1986 - 1995"
    3 = "1996 - 2005"
    4 = "2006 - 2012"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q04DUSX1A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05A2USX2_
    1 = "1-4 years old"
    2 = "5-10 years old"
    3 = "11-15 years old"
    4 = "16-20 years old"
    5 = "21 years or older"
    6 = "Does not speak English"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSP4_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX2_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX3A
    1 = "Very well"
    2 = "Well"
    3 = "Not well"
    4 = "Not at all"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX3B
    1 = "Very well"
    2 = "Well"
    3 = "Not well"
    4 = "Not at all"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX3D
    1 = "Very well"
    2 = "Well"
    3 = "Not well"
    4 = "Not at all"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX3E
    1 = "Very well"
    2 = "Well"
    3 = "Not well"
    4 = "Not at all"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q05CUSX6_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q06A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q06B
    1 = "ISCED 1, 2, and 3C short"
    2 = "ISCED 3 (excluding 3C short) and 4"
    3 = "ISCED 5 and 6"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q06BUS
    1 = "Less than high school diploma"
    2 = "High school diploma/some college but no degree"
    3 = "College degree or higher (Associate, Bachelor, Doctorate)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q06B_ISCED11F
    1 = "No formal qualification or below ISCED 1, ISCED 1 and 2"
    2 = "ISCED 3 and 4"
    3 = "ISCED 5, 6, 7, and 8"
    6 = "Valid skip"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q07A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q07B
    1 = "ISCED 1, 2, and 3C short"
    2 = "ISCED 3 (excluding 3C short) and 4"
    3 = "ISCED 5 and 6"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q07BUS
    1 = "Less than high school diploma"
    2 = "High school diploma/some college but no degree"
    3 = "College degree or higher (Associate, Bachelor, Doctorate)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q07B_ISCED11F
    1 = "No formal qualification or below ISCED 1, ISCED 1 and 2"
    2 = "ISCED 3 and 4"
    3 = "ISCED 5, 6, 7, and 8"
    6 = "Valid skip"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE J_Q08_
    1 = "10 books or less"
    2 = "11 to 25 books"
    3 = "26 to 100 books"
    4 = "101 to 200 books"
    5 = "201 to 500 books"
    6 = "More than 500 books"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE LANGUAGE
    1 = "Learned english as the first language"
    2 = "Learned english when age 15 or younger"
    3 = "Learned english when age 16 or older"
    .N = "Not stated or inferred"
  ;
  VALUE LEAVER1624_
    0 = "Completed ISCED 3 or is still in education, aged 16 to 24"
    1 = "Not in education, did not complete ISCED 3, aged 16 to 24"
    .A = "Adults older than 24"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE LITSTATUS
    1 = "Has PV"
    2 = "Literacy Related Non-Response"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE $LNG_BQ
    996 = "Valid skip"
    997 = "Don't know"
    998 = "Refused"
    999 = "Not stated or inferred"
    aar = "Afar"
    abk = "Abkhazian"
    ace = "Achinese"
    ach = "Acoli"
    ada = "Adangme"
    ady = "Adyghe; Adygei"
    afa = "Afro-Asiatic languages"
    afh = "Afrihili"
    afr = "Afrikaans"
    ain = "Ainu"
    aka = "Akan"
    akk = "Akkadian"
    ale = "Aleut"
    alg = "Algonquian languages"
    alt = "Southern Altai"
    amh = "Amharic"
    ang = "English, Old (ca.450-1100)"
    anp = "Angika"
    apa = "Apache languages"
    ara = "Arabic"
    arc = "Official Aramaic (700-300 BCE); Imperial Aramaic (700-300 BCE)"
    arg = "Aragonese"
    arn = "Mapudungun; Mapuche"
    arp = "Arapaho"
    art = "Artificial languages"
    arw = "Arawak"
    asm = "Assamese"
    ast = "Asturian; Bable; Leonese; Asturleonese"
    ath = "Athapascan languages"
    aus = "Australian languages"
    ava = "Avaric"
    ave = "Avestan"
    awa = "Awadhi"
    aym = "Aymara"
    aze = "Azerbaijani"
    bad = "Banda languages"
    bai = "Bamileke languages"
    bak = "Bashkir"
    bal = "Baluchi"
    bam = "Bambara"
    ban = "Balinese"
    bas = "Basa"
    bat = "Baltic languages"
    bej = "Beja; Bedawiyet"
    bel = "Belarusian"
    bem = "Bemba"
    ben = "Bengali"
    ber = "Berber languages"
    bho = "Bhojpuri"
    bih = "Bihari"
    bik = "Bikol"
    bin = "Bini; Edo"
    bis = "Bislama"
    bla = "Siksika"
    bnt = "Bantu (Other)"
    bod = "Tibetan"
    bos = "Bosnian"
    bra = "Braj"
    bre = "Breton"
    btk = "Batak languages"
    bua = "Buriat"
    bug = "Buginese"
    bul = "Bulgarian"
    byn = "Blin; Bilin"
    cad = "Caddo"
    cai = "Central American Indian languages"
    car = "Galibi Carib"
    cat = "Catalan; Valencian"
    cau = "Caucasian languages"
    ceb = "Cebuano"
    cel = "Celtic languages"
    ces = "Czech"
    cha = "Chamorro"
    chb = "Chibcha"
    che = "Chechen"
    chg = "Chagatai"
    chk = "Chuukese"
    chm = "Mari"
    chn = "Chinook jargon"
    cho = "Choctaw"
    chp = "Chipewyan; Dene Suline"
    chr = "Cherokee"
    chu = "Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic"
    chv = "Chuvash"
    chy = "Cheyenne"
    cmc = "Chamic languages"
    cop = "Coptic"
    cor = "Cornish"
    cos = "Corsican"
    cpe = "Creoles and pidgins, English based"
    cpf = "Creoles and pidgins, French-based"
    cpp = "Creoles and pidgins, Portuguese-based"
    cre = "Cree"
    crh = "Crimean Tatar; Crimean Turkish"
    crp = "Creoles and pidgins"
    csb = "Kashubian"
    cus = "Cushitic languages"
    cym = "Welsh"
    dak = "Dakota"
    dan = "Danish"
    dar = "Dargwa"
    day = "Land Dayak languages"
    del = "Delaware"
    den = "Slave (Athapascan)"
    deu = "German"
    dgr = "Dogrib"
    din = "Dinka"
    div = "Divehi; Dhivehi; Maldivian"
    doi = "Dogri"
    dra = "Dravidian languages"
    dsb = "Lower Sorbian"
    dua = "Duala"
    dum = "Dutch, Middle (ca.1050-1350)"
    dyu = "Dyula"
    dzo = "Dzongkha"
    efi = "Efik"
    egy = "Egyptian (Ancient)"
    eka = "Ekajuk"
    ell = "Greek, Modern (1453-)"
    elx = "Elamite"
    eng = "English"
    enm = "English, Middle (1100-1500)"
    epo = "Esperanto"
    est = "Estonian"
    eus = "Basque"
    ewe = "Ewe"
    ewo = "Ewondo"
    fan = "Fang"
    fao = "Faroese"
    fas = "Persian"
    fat = "Fanti"
    fij = "Fijian"
    fil = "Filipino; Pilipino"
    fin = "Finnish"
    fiu = "Finno-Ugrian languages"
    fon = "Fon"
    fra = "French"
    frm = "French, Middle (ca.1400-1600)"
    fro = "French, Old (842-ca.1400)"
    frr = "Northern Frisian"
    frs = "Eastern Frisian"
    fry = "Western Frisian"
    ful = "Fulah"
    fur = "Friulian"
    gaa = "Ga"
    gay = "Gayo"
    gba = "Gbaya"
    gem = "Germanic languages"
    gez = "Geez"
    gil = "Gilbertese"
    gla = "Gaelic; Scottish Gaelic"
    gle = "Irish"
    glg = "Galician"
    glv = "Manx"
    gmh = "German, Middle High (ca.1050-1500)"
    goh = "German, Old High (ca.750-1050)"
    gon = "Gondi"
    gor = "Gorontalo"
    got = "Gothic"
    grb = "Grebo"
    grc = "Greek, Ancient (to 1453)"
    grn = "Guarani"
    gsw = "Swiss German; Alemannic; Alsatian"
    guj = "Gujarati"
    gwi = "Gwich'in"
    hai = "Haida"
    hat = "Haitian; Haitian Creole"
    hau = "Hausa"
    haw = "Hawaiian"
    heb = "Hebrew"
    her = "Herero"
    hil = "Hiligaynon"
    him = "Himachali"
    hin = "Hindi"
    hit = "Hittite"
    hmn = "Hmong"
    hmo = "Hiri Motu"
    hrv = "Croatian"
    hsb = "Upper Sorbian"
    hun = "Hungarian"
    hup = "Hupa"
    hye = "Armenian"
    iba = "Iban"
    ibo = "Igbo"
    ido = "Ido"
    iii = "Sichuan Yi; Nuosu"
    ijo = "Ijo languages"
    iku = "Inuktitut"
    ile = "Interlingue; Occidental"
    ilo = "Iloko"
    ina = "Interlingua (International Auxiliary Language Association)"
    inc = "Indic languages"
    ind = "Indonesian"
    ine = "Indo-European languages"
    inh = "Ingush"
    ipk = "Inupiaq"
    ira = "Iranian languages"
    iro = "Iroquoian languages"
    isl = "Icelandic"
    ita = "Italian"
    jav = "Javanese"
    jbo = "Lojban"
    jpn = "Japanese"
    jpr = "Judeo-Persian"
    jrb = "Judeo-Arabic"
    kaa = "Kara-Kalpak"
    kab = "Kabyle"
    kac = "Kachin; Jingpho"
    kal = "Kalaallisut; Greenlandic"
    kam = "Kamba"
    kan = "Kannada"
    kar = "Karen languages"
    kas = "Kashmiri"
    kat = "Georgian"
    kau = "Kanuri"
    kaw = "Kawi"
    kaz = "Kazakh"
    kbd = "Kabardian"
    kha = "Khasi"
    khi = "Khoisan languages"
    khm = "Central Khmer"
    kho = "Khotanese; Sakan"
    kik = "Kikuyu; Gikuyu"
    kin = "Kinyarwanda"
    kir = "Kirghiz; Kyrgyz"
    kmb = "Kimbundu"
    kok = "Konkani"
    kom = "Komi"
    kon = "Kongo"
    kor = "Korean"
    kos = "Kosraean"
    kpe = "Kpelle"
    krc = "Karachay-Balkar"
    krl = "Karelian"
    kro = "Kru languages"
    kru = "Kurukh"
    kua = "Kuanyama; Kwanyama"
    kum = "Kumyk"
    kur = "Kurdish"
    kut = "Kutenai"
    lad = "Ladino"
    lah = "Lahnda"
    lam = "Lamba"
    lao = "Lao"
    lat = "Latin"
    lav = "Latvian"
    lez = "Lezghian"
    lim = "Limburgan; Limburger; Limburgish"
    lin = "Lingala"
    lit = "Lithuanian"
    lol = "Mongo"
    loz = "Lozi"
    ltz = "Luxembourgish; Letzeburgesch"
    lua = "Luba-Lulua"
    lub = "Luba-Katanga"
    lug = "Ganda"
    lui = "Luiseno"
    lun = "Lunda"
    luo = "Luo (Kenya and Tanzania)"
    lus = "Lushai"
    mad = "Madurese"
    mag = "Magahi"
    mah = "Marshallese"
    mai = "Maithili"
    mak = "Makasar"
    mal = "Malayalam"
    man = "Mandingo"
    map = "Austronesian languages"
    mar = "Marathi"
    mas = "Masai"
    mdf = "Moksha"
    mdr = "Mandar"
    men = "Mende"
    mga = "Irish, Middle (900-1200)"
    mic = "Mi'kmaq; Micmac"
    min = "Minangkabau"
    mis = "Uncoded languages"
    mkd = "Macedonian"
    mkh = "Mon-Khmer languages"
    mlg = "Malagasy"
    mlt = "Maltese"
    mnc = "Manchu"
    mni = "Manipuri"
    mno = "Manobo languages"
    moh = "Mohawk"
    mon = "Mongolian"
    mos = "Mossi"
    mri = "Maori"
    msa = "Malay"
    mul = "Multiple languages"
    mun = "Munda languages"
    mus = "Creek"
    mwl = "Mirandese"
    mwr = "Marwari"
    mya = "Burmese"
    myn = "Mayan languages"
    myv = "Erzya"
    nah = "Nahuatl languages"
    nai = "North American Indian languages"
    nap = "Neapolitan"
    nau = "Nauru"
    nav = "Navajo; Navaho"
    nbl = "Ndebele, South; South Ndebele"
    nde = "Ndebele, North; North Ndebele"
    ndo = "Ndonga"
    nds = "Low German; Low Saxon; German, Low; Saxon, Low"
    nep = "Nepali"
    new = "Nepal Bhasa; Newari"
    nia = "Nias"
    nic = "Niger-Kordofanian languages"
    niu = "Niuean"
    nld = "Dutch; Flemish"
    nno = "Norwegian Nynorsk; Nynorsk, Norwegian"
    nob = "Bokmål, Norwegian; Norwegian Bokmål"
    nog = "Nogai"
    non = "Norse, Old"
    nor = "Norwegian"
    nqo = "N'Ko"
    nso = "Pedi; Sepedi; Northern Sotho"
    nub = "Nubian languages"
    nwc = "Classical Newari; Old Newari; Classical Nepal Bhasa"
    nya = "Chichewa; Chewa; Nyanja"
    nym = "Nyamwezi"
    nyn = "Nyankole"
    nyo = "Nyoro"
    nzi = "Nzima"
    oci = "Occitan (post 1500); Provençal"
    oji = "Ojibwa"
    ori = "Oriya"
    orm = "Oromo"
    osa = "Osage"
    oss = "Ossetian; Ossetic"
    ota = "Turkish, Ottoman (1500-1928)"
    oto = "Otomian languages"
    paa = "Papuan languages"
    pag = "Pangasinan"
    pal = "Pahlavi"
    pam = "Pampanga; Kapampangan"
    pan = "Panjabi; Punjabi"
    pap = "Papiamento"
    pau = "Palauan"
    peo = "Persian, Old (ca.600-400 B.C.)"
    phi = "Philippine languages"
    phn = "Phoenician"
    pli = "Pali"
    pol = "Polish"
    pon = "Pohnpeian"
    por = "Portuguese"
    pra = "Prakrit languages"
    pro = "Provençal, Old (to 1500)"
    pus = "Pushto; Pashto"
    que = "Quechua"
    raj = "Rajasthani"
    rap = "Rapanui"
    rar = "Rarotongan; Cook Islands Maori"
    roa = "Romance languages"
    roh = "Romansh"
    rom = "Romany"
    ron = "Romanian; Moldavian; Moldovan"
    run = "Rundi"
    rup = "Aromanian; Arumanian; Macedo-Romanian"
    rus = "Russian"
    sad = "Sandawe"
    sag = "Sango"
    sah = "Yakut"
    sai = "South American Indian (Other)"
    sal = "Salishan languages"
    sam = "Samaritan Aramaic"
    san = "Sanskrit"
    sas = "Sasak"
    sat = "Santali"
    scn = "Sicilian"
    sco = "Scots"
    sel = "Selkup"
    sem = "Semitic languages"
    sga = "Irish, Old (to 900)"
    sgn = "Sign Languages"
    shn = "Shan"
    sid = "Sidamo"
    sin = "Sinhala; Sinhalese"
    sio = "Siouan languages"
    sit = "Sino-Tibetan languages"
    sla = "Slavic languages"
    slk = "Slovak"
    slv = "Slovenian"
    sma = "Southern Sami"
    sme = "Northern Sami"
    smi = "Sami languages"
    smj = "Lule Sami"
    smn = "Inari Sami"
    smo = "Samoan"
    sms = "Skolt Sami"
    sna = "Shona"
    snd = "Sindhi"
    snk = "Soninke"
    sog = "Sogdian"
    som = "Somali"
    son = "Songhai languages"
    sot = "Sotho, Southern"
    spa = "Spanish; Castilian"
    sqi = "Albanian"
    srd = "Sardinian"
    srn = "Sranan Tongo"
    srp = "Serbian"
    srr = "Serer"
    ssa = "Nilo-Saharan languages"
    ssw = "Swati"
    suk = "Sukuma"
    sun = "Sundanese"
    sus = "Susu"
    sux = "Sumerian"
    swa = "Swahili"
    swe = "Swedish"
    syc = "Classical Syriac"
    syr = "Syriac"
    tah = "Tahitian"
    tai = "Tai languages"
    tam = "Tamil"
    tat = "Tatar"
    tel = "Telugu"
    tem = "Timne"
    ter = "Tereno"
    tet = "Tetum"
    tgk = "Tajik"
    tgl = "Tagalog"
    tha = "Thai"
    tig = "Tigre"
    tir = "Tigrinya"
    tiv = "Tiv"
    tkl = "Tokelau"
    tlh = "Klingon; tlhIngan-Hol"
    tli = "Tlingit"
    tmh = "Tamashek"
    tog = "Tonga (Nyasa)"
    ton = "Tonga (Tonga Islands)"
    tpi = "Tok Pisin"
    tsi = "Tsimshian"
    tsn = "Tswana"
    tso = "Tsonga"
    tuk = "Turkmen"
    tum = "Tumbuka"
    tup = "Tupi languages"
    tur = "Turkish"
    tut = "Altaic languages"
    tvl = "Tuvalu"
    twi = "Twi"
    tyv = "Tuvinian"
    udm = "Udmurt"
    uga = "Ugaritic"
    uig = "Uighur; Uyghur"
    ukr = "Ukrainian"
    umb = "Umbundu"
    und = "Undetermined"
    urd = "Urdu"
    uzb = "Uzbek"
    vai = "Vai"
    ven = "Venda"
    vie = "Vietnamese"
    vol = "Volapük"
    vot = "Votic"
    wak = "Wakashan languages"
    wal = "Walamo"
    war = "Waray"
    was = "Washo"
    wen = "Sorbian languages"
    wln = "Walloon"
    wol = "Wolof"
    xal = "Kalmyk; Oirat"
    xho = "Xhosa"
    yao = "Yao"
    yap = "Yapese"
    yid = "Yiddish"
    yor = "Yoruba"
    ypk = "Yupik languages"
    zap = "Zapotec"
    zbl = "Blissymbols; Blissymbolics; Bliss"
    zen = "Zenaga"
    zha = "Zhuang; Chuang"
    zho = "Chinese"
    znd = "Zande languages"
    zul = "Zulu"
    zun = "Zuni"
    zxx = "No linguistic content; Not applicable"
    zza = "Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki"
  ;
  VALUE $LNG_CI
    996 = "Valid skip"
    997 = "Don't know"
    998 = "Refused"
    999 = "Not stated or inferred"
    aar = "Afar"
    abk = "Abkhazian"
    ace = "Achinese"
    ach = "Acoli"
    ada = "Adangme"
    ady = "Adyghe; Adygei"
    afa = "Afro-Asiatic languages"
    afh = "Afrihili"
    afr = "Afrikaans"
    ain = "Ainu"
    aka = "Akan"
    akk = "Akkadian"
    ale = "Aleut"
    alg = "Algonquian languages"
    alt = "Southern Altai"
    amh = "Amharic"
    ang = "English, Old (ca.450-1100)"
    anp = "Angika"
    apa = "Apache languages"
    ara = "Arabic"
    arc = "Official Aramaic (700-300 BCE); Imperial Aramaic (700-300 BCE)"
    arg = "Aragonese"
    arn = "Mapudungun; Mapuche"
    arp = "Arapaho"
    art = "Artificial languages"
    arw = "Arawak"
    asm = "Assamese"
    ast = "Asturian; Bable; Leonese; Asturleonese"
    ath = "Athapascan languages"
    aus = "Australian languages"
    ava = "Avaric"
    ave = "Avestan"
    awa = "Awadhi"
    aym = "Aymara"
    aze = "Azerbaijani"
    bad = "Banda languages"
    bai = "Bamileke languages"
    bak = "Bashkir"
    bal = "Baluchi"
    bam = "Bambara"
    ban = "Balinese"
    bas = "Basa"
    bat = "Baltic languages"
    bej = "Beja; Bedawiyet"
    bel = "Belarusian"
    bem = "Bemba"
    ben = "Bengali"
    ber = "Berber languages"
    bho = "Bhojpuri"
    bih = "Bihari"
    bik = "Bikol"
    bin = "Bini; Edo"
    bis = "Bislama"
    bla = "Siksika"
    bnt = "Bantu (Other)"
    bod = "Tibetan"
    bos = "Bosnian"
    bra = "Braj"
    bre = "Breton"
    btk = "Batak languages"
    bua = "Buriat"
    bug = "Buginese"
    bul = "Bulgarian"
    byn = "Blin; Bilin"
    cad = "Caddo"
    cai = "Central American Indian languages"
    car = "Galibi Carib"
    cat = "Catalan; Valencian"
    cau = "Caucasian languages"
    ceb = "Cebuano"
    cel = "Celtic languages"
    ces = "Czech"
    cha = "Chamorro"
    chb = "Chibcha"
    che = "Chechen"
    chg = "Chagatai"
    chk = "Chuukese"
    chm = "Mari"
    chn = "Chinook jargon"
    cho = "Choctaw"
    chp = "Chipewyan; Dene Suline"
    chr = "Cherokee"
    chu = "Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic"
    chv = "Chuvash"
    chy = "Cheyenne"
    cmc = "Chamic languages"
    cop = "Coptic"
    cor = "Cornish"
    cos = "Corsican"
    cpe = "Creoles and pidgins, English based"
    cpf = "Creoles and pidgins, French-based"
    cpp = "Creoles and pidgins, Portuguese-based"
    cre = "Cree"
    crh = "Crimean Tatar; Crimean Turkish"
    crp = "Creoles and pidgins"
    csb = "Kashubian"
    cus = "Cushitic languages"
    cym = "Welsh"
    dak = "Dakota"
    dan = "Danish"
    dar = "Dargwa"
    day = "Land Dayak languages"
    del = "Delaware"
    den = "Slave (Athapascan)"
    deu = "German"
    dgr = "Dogrib"
    din = "Dinka"
    div = "Divehi; Dhivehi; Maldivian"
    doi = "Dogri"
    dra = "Dravidian languages"
    dsb = "Lower Sorbian"
    dua = "Duala"
    dum = "Dutch, Middle (ca.1050-1350)"
    dyu = "Dyula"
    dzo = "Dzongkha"
    efi = "Efik"
    egy = "Egyptian (Ancient)"
    eka = "Ekajuk"
    ell = "Greek, Modern (1453-)"
    elx = "Elamite"
    eng = "English"
    enm = "English, Middle (1100-1500)"
    epo = "Esperanto"
    est = "Estonian"
    eus = "Basque"
    ewe = "Ewe"
    ewo = "Ewondo"
    fan = "Fang"
    fao = "Faroese"
    fas = "Persian"
    fat = "Fanti"
    fij = "Fijian"
    fil = "Filipino; Pilipino"
    fin = "Finnish"
    fiu = "Finno-Ugrian languages"
    fon = "Fon"
    fra = "French"
    frm = "French, Middle (ca.1400-1600)"
    fro = "French, Old (842-ca.1400)"
    frr = "Northern Frisian"
    frs = "Eastern Frisian"
    fry = "Western Frisian"
    ful = "Fulah"
    fur = "Friulian"
    gaa = "Ga"
    gay = "Gayo"
    gba = "Gbaya"
    gem = "Germanic languages"
    gez = "Geez"
    gil = "Gilbertese"
    gla = "Gaelic; Scottish Gaelic"
    gle = "Irish"
    glg = "Galician"
    glv = "Manx"
    gmh = "German, Middle High (ca.1050-1500)"
    goh = "German, Old High (ca.750-1050)"
    gon = "Gondi"
    gor = "Gorontalo"
    got = "Gothic"
    grb = "Grebo"
    grc = "Greek, Ancient (to 1453)"
    grn = "Guarani"
    gsw = "Swiss German; Alemannic; Alsatian"
    guj = "Gujarati"
    gwi = "Gwich'in"
    hai = "Haida"
    hat = "Haitian; Haitian Creole"
    hau = "Hausa"
    haw = "Hawaiian"
    heb = "Hebrew"
    her = "Herero"
    hil = "Hiligaynon"
    him = "Himachali"
    hin = "Hindi"
    hit = "Hittite"
    hmn = "Hmong"
    hmo = "Hiri Motu"
    hrv = "Croatian"
    hsb = "Upper Sorbian"
    hun = "Hungarian"
    hup = "Hupa"
    hye = "Armenian"
    iba = "Iban"
    ibo = "Igbo"
    ido = "Ido"
    iii = "Sichuan Yi; Nuosu"
    ijo = "Ijo languages"
    iku = "Inuktitut"
    ile = "Interlingue; Occidental"
    ilo = "Iloko"
    ina = "Interlingua (International Auxiliary Language Association)"
    inc = "Indic languages"
    ind = "Indonesian"
    ine = "Indo-European languages"
    inh = "Ingush"
    ipk = "Inupiaq"
    ira = "Iranian languages"
    iro = "Iroquoian languages"
    isl = "Icelandic"
    ita = "Italian"
    jav = "Javanese"
    jbo = "Lojban"
    jpn = "Japanese"
    jpr = "Judeo-Persian"
    jrb = "Judeo-Arabic"
    kaa = "Kara-Kalpak"
    kab = "Kabyle"
    kac = "Kachin; Jingpho"
    kal = "Kalaallisut; Greenlandic"
    kam = "Kamba"
    kan = "Kannada"
    kar = "Karen languages"
    kas = "Kashmiri"
    kat = "Georgian"
    kau = "Kanuri"
    kaw = "Kawi"
    kaz = "Kazakh"
    kbd = "Kabardian"
    kha = "Khasi"
    khi = "Khoisan languages"
    khm = "Central Khmer"
    kho = "Khotanese; Sakan"
    kik = "Kikuyu; Gikuyu"
    kin = "Kinyarwanda"
    kir = "Kirghiz; Kyrgyz"
    kmb = "Kimbundu"
    kok = "Konkani"
    kom = "Komi"
    kon = "Kongo"
    kor = "Korean"
    kos = "Kosraean"
    kpe = "Kpelle"
    krc = "Karachay-Balkar"
    krl = "Karelian"
    kro = "Kru languages"
    kru = "Kurukh"
    kua = "Kuanyama; Kwanyama"
    kum = "Kumyk"
    kur = "Kurdish"
    kut = "Kutenai"
    lad = "Ladino"
    lah = "Lahnda"
    lam = "Lamba"
    lao = "Lao"
    lat = "Latin"
    lav = "Latvian"
    lez = "Lezghian"
    lim = "Limburgan; Limburger; Limburgish"
    lin = "Lingala"
    lit = "Lithuanian"
    lol = "Mongo"
    loz = "Lozi"
    ltz = "Luxembourgish; Letzeburgesch"
    lua = "Luba-Lulua"
    lub = "Luba-Katanga"
    lug = "Ganda"
    lui = "Luiseno"
    lun = "Lunda"
    luo = "Luo (Kenya and Tanzania)"
    lus = "Lushai"
    mad = "Madurese"
    mag = "Magahi"
    mah = "Marshallese"
    mai = "Maithili"
    mak = "Makasar"
    mal = "Malayalam"
    man = "Mandingo"
    map = "Austronesian languages"
    mar = "Marathi"
    mas = "Masai"
    mdf = "Moksha"
    mdr = "Mandar"
    men = "Mende"
    mga = "Irish, Middle (900-1200)"
    mic = "Mi'kmaq; Micmac"
    min = "Minangkabau"
    mis = "Uncoded languages"
    mkd = "Macedonian"
    mkh = "Mon-Khmer languages"
    mlg = "Malagasy"
    mlt = "Maltese"
    mnc = "Manchu"
    mni = "Manipuri"
    mno = "Manobo languages"
    moh = "Mohawk"
    mon = "Mongolian"
    mos = "Mossi"
    mri = "Maori"
    msa = "Malay"
    mul = "Multiple languages"
    mun = "Munda languages"
    mus = "Creek"
    mwl = "Mirandese"
    mwr = "Marwari"
    mya = "Burmese"
    myn = "Mayan languages"
    myv = "Erzya"
    nah = "Nahuatl languages"
    nai = "North American Indian languages"
    nap = "Neapolitan"
    nau = "Nauru"
    nav = "Navajo; Navaho"
    nbl = "Ndebele, South; South Ndebele"
    nde = "Ndebele, North; North Ndebele"
    ndo = "Ndonga"
    nds = "Low German; Low Saxon; German, Low; Saxon, Low"
    nep = "Nepali"
    new = "Nepal Bhasa; Newari"
    nia = "Nias"
    nic = "Niger-Kordofanian languages"
    niu = "Niuean"
    nld = "Dutch; Flemish"
    nno = "Norwegian Nynorsk; Nynorsk, Norwegian"
    nob = "Bokmål, Norwegian; Norwegian Bokmål"
    nog = "Nogai"
    non = "Norse, Old"
    nor = "Norwegian"
    nqo = "N'Ko"
    nso = "Pedi; Sepedi; Northern Sotho"
    nub = "Nubian languages"
    nwc = "Classical Newari; Old Newari; Classical Nepal Bhasa"
    nya = "Chichewa; Chewa; Nyanja"
    nym = "Nyamwezi"
    nyn = "Nyankole"
    nyo = "Nyoro"
    nzi = "Nzima"
    oci = "Occitan (post 1500); Provençal"
    oji = "Ojibwa"
    ori = "Oriya"
    orm = "Oromo"
    osa = "Osage"
    oss = "Ossetian; Ossetic"
    ota = "Turkish, Ottoman (1500-1928)"
    oto = "Otomian languages"
    paa = "Papuan languages"
    pag = "Pangasinan"
    pal = "Pahlavi"
    pam = "Pampanga; Kapampangan"
    pan = "Panjabi; Punjabi"
    pap = "Papiamento"
    pau = "Palauan"
    peo = "Persian, Old (ca.600-400 B.C.)"
    phi = "Philippine languages"
    phn = "Phoenician"
    pli = "Pali"
    pol = "Polish"
    pon = "Pohnpeian"
    por = "Portuguese"
    pra = "Prakrit languages"
    pro = "Provençal, Old (to 1500)"
    pus = "Pushto; Pashto"
    que = "Quechua"
    raj = "Rajasthani"
    rap = "Rapanui"
    rar = "Rarotongan; Cook Islands Maori"
    roa = "Romance languages"
    roh = "Romansh"
    rom = "Romany"
    ron = "Romanian; Moldavian; Moldovan"
    run = "Rundi"
    rup = "Aromanian; Arumanian; Macedo-Romanian"
    rus = "Russian"
    sad = "Sandawe"
    sag = "Sango"
    sah = "Yakut"
    sai = "South American Indian (Other)"
    sal = "Salishan languages"
    sam = "Samaritan Aramaic"
    san = "Sanskrit"
    sas = "Sasak"
    sat = "Santali"
    scn = "Sicilian"
    sco = "Scots"
    sel = "Selkup"
    sem = "Semitic languages"
    sga = "Irish, Old (to 900)"
    sgn = "Sign Languages"
    shn = "Shan"
    sid = "Sidamo"
    sin = "Sinhala; Sinhalese"
    sio = "Siouan languages"
    sit = "Sino-Tibetan languages"
    sla = "Slavic languages"
    slk = "Slovak"
    slv = "Slovenian"
    sma = "Southern Sami"
    sme = "Northern Sami"
    smi = "Sami languages"
    smj = "Lule Sami"
    smn = "Inari Sami"
    smo = "Samoan"
    sms = "Skolt Sami"
    sna = "Shona"
    snd = "Sindhi"
    snk = "Soninke"
    sog = "Sogdian"
    som = "Somali"
    son = "Songhai languages"
    sot = "Sotho, Southern"
    spa = "Spanish; Castilian"
    sqi = "Albanian"
    srd = "Sardinian"
    srn = "Sranan Tongo"
    srp = "Serbian"
    srr = "Serer"
    ssa = "Nilo-Saharan languages"
    ssw = "Swati"
    suk = "Sukuma"
    sun = "Sundanese"
    sus = "Susu"
    sux = "Sumerian"
    swa = "Swahili"
    swe = "Swedish"
    syc = "Classical Syriac"
    syr = "Syriac"
    tah = "Tahitian"
    tai = "Tai languages"
    tam = "Tamil"
    tat = "Tatar"
    tel = "Telugu"
    tem = "Timne"
    ter = "Tereno"
    tet = "Tetum"
    tgk = "Tajik"
    tgl = "Tagalog"
    tha = "Thai"
    tig = "Tigre"
    tir = "Tigrinya"
    tiv = "Tiv"
    tkl = "Tokelau"
    tlh = "Klingon; tlhIngan-Hol"
    tli = "Tlingit"
    tmh = "Tamashek"
    tog = "Tonga (Nyasa)"
    ton = "Tonga (Tonga Islands)"
    tpi = "Tok Pisin"
    tsi = "Tsimshian"
    tsn = "Tswana"
    tso = "Tsonga"
    tuk = "Turkmen"
    tum = "Tumbuka"
    tup = "Tupi languages"
    tur = "Turkish"
    tut = "Altaic languages"
    tvl = "Tuvalu"
    twi = "Twi"
    tyv = "Tuvinian"
    udm = "Udmurt"
    uga = "Ugaritic"
    uig = "Uighur; Uyghur"
    ukr = "Ukrainian"
    umb = "Umbundu"
    und = "Undetermined"
    urd = "Urdu"
    uzb = "Uzbek"
    vai = "Vai"
    ven = "Venda"
    vie = "Vietnamese"
    vol = "Volapük"
    vot = "Votic"
    wak = "Wakashan languages"
    wal = "Walamo"
    war = "Waray"
    was = "Washo"
    wen = "Sorbian languages"
    wln = "Walloon"
    wol = "Wolof"
    xal = "Kalmyk; Oirat"
    xho = "Xhosa"
    yao = "Yao"
    yap = "Yapese"
    yid = "Yiddish"
    yor = "Yoruba"
    ypk = "Yupik languages"
    zap = "Zapotec"
    zbl = "Blissymbols; Blissymbolics; Bliss"
    zen = "Zenaga"
    zha = "Zhuang; Chuang"
    zho = "Chinese"
    znd = "Zande languages"
    zul = "Zulu"
    zun = "Zuni"
    zxx = "No linguistic content; Not applicable"
    zza = "Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki"
  ;
  VALUE LNG_HOMEUS_C
    1 = "English"
    2 = "Spanish"
    3 = "Other language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE LNG_L1US_C
    1 = "English"
    2 = "Spanish"
    3 = "Other language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE LNG_L2US_C
    1 = "English"
    2 = "Spanish"
    3 = "Other language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE M300C02S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M301C05S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M305215S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M305218S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M309319S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M309320S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M309321S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M309322S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M310406S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M310407S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M313410S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M313411S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M313412S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M313413S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M313414S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M600C04S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M602501S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M602502S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M602503S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M604505S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M610515S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M615602S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M615603S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M618607S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M618608S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M620610S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M620612S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M623616S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M623617S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M623618S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M624619S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE M624620S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE MONTHLYINCPR
    1 = "Less than 10"
    2 = "10 to less than 25"
    3 = "25 to less than 50"
    4 = "50 to less than 75"
    5 = "75 to less than 90"
    6 = "90 or more"
    .N = "Not stated or inferred"
  ;
  VALUE N302C02S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE N306110S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE N306111S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE NATBILANG
    0 = "Monolingual or at least bilingual not including test language"
    1 = "At least bilingual including test language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE NATIVELANG
    0 = "Test language not same as native language"
    1 = "Test language same as native language"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE NATIVESPEAKER
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE NFE12JR
    0 = "Did not participate in NFE for JR reasons"
    1 = "Participated in NFE for JR reasons"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE NFE12NJR
    0 = "Did not participate in NFE for NJR reasons"
    1 = "Participated in NFE for NJR reasons"
    .N = "Not stated or inferred"
    .U = "Unknown"
  ;
  VALUE NFEHRS
    .A = "Did not participate"
    .N = "Not stated or inferred"
  ;
  VALUE NFEHRSJR
    .A = "Did not participate"
    .N = "Not stated or inferred"
  ;
  VALUE NFEHRSNJR
    .A = "Did not participate"
    .N = "Not stated or inferred"
  ;
  VALUE NUMHOMEUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE NUMSTATUS
    1 = "Has PV"
    2 = "Literacy Related Non-Response"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE NUMWORK_CUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE NUMWORK_CUSP_WLE_CA
    0 = "All zero response"
    1 = "Lowest to 20%"
    2 = "More than 20% to 40%"
    3 = "More than 40% to 60%"
    4 = "More than 60% to 80%"
    5 = "More than 80%"
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE NUMWORK_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE NUMWORK_SE_C
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE P317001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P317002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P317003S
    0 = "Question refused / not done"
    1 = "Correct response 1"
    2 = "Correct response 2"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P324002S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P324003S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P330001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P601C06S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P614601S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P640001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P645001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P655001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P664001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P666001S
    0 = "No response"
    1 = "Correct response"
    7 = "Incorrect response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901002R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901002S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901003R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901003S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901004R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901004S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901005R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901005S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901006R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901006S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901011R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901011S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901013R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901013S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901015R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901015S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901017R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901017S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901018R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901018S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901019R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901019S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901020R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901020S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901021R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901021S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901024R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901024S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901025R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P901025S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902014R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902014S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902021R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902021S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902022R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902022S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902024R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P902024S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903007R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903007S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903012R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903012S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903017R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903017S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903021R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903021S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903024R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P903024S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904009R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904009S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904010R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904010S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904012R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904012S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904014R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904014S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904015R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904015S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904020R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904020S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904021R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904021S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904022R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904022S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904024R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904024S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904025R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    3 = "Response 3 (third word choice)"
    4 = "Response 4 (fourth word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P904025S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911001R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911001S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911003R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911003S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911004R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911004S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911005R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911005S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911006R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911006S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911007R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911007S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911008R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911008S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911009R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911009S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911010R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911010S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911014R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911014S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911017R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911017S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911020R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P911020S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912002R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912002S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912011R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912011S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912013R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912013S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912019R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P912019S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P913013R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P913013S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914012R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914012S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914015R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914015S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914016R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914016S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914018R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914018S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914019R
    0 = "Question refused / not done"
    1 = "Response 1 (yes)"
    2 = "Response 2 (no)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P914019S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921002R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921002S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921003R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921003S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921004R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921004S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921005R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921005S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921007R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921007S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921008R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921008S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921009R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921009S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921010R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921010S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921011R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921011S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921013R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921013S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921014R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921014S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921015R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921015S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921016R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921016S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921017R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921017S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921018R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921018S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921019R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921019S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921020R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921020S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921021R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921021S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921035R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921035S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921036R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921036S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921037R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921037S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921038R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921038S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921040R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921040S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921041R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921041S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921042R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921042S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921043R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P921043S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922023R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922023S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922024R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922024S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922025R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922025S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922026R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922026S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922027R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922027S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922028R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922028S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922030R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922030S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922031R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922031S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922032R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922032S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922033R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P922033S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924035R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924035S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924036R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924036S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924037R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924037S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924038R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924038S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924040R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924040S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924041R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924041S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924042R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924042S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924043R
    0 = "Question refused / not done"
    1 = "Response 1 (first word choice)"
    2 = "Response 2 (second word choice)"
    7 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE P924043S
    0 = "Question refused / not done"
    1 = "Correct response"
    7 = "Incorrect response"
    8 = "Any other response"
    .N = "Not reached/Not attempted"
  ;
  VALUE PAPER
    0 = "Missing"
    1 = "PP1-LIT"
    2 = "PP2-NUM"
    3 = "Failed Paper Core"
    .N = "Not stated or inferred"
  ;
  VALUE PARED
    1 = "Neither parent has attained upper secondary"
    2 = "At least one parent has attained secondary and post-secondary, non-tertiary"
    3 = "At least one parent has attained tertiary"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE PBROUTE
    1 = "No computer experience"
    2 = "Failed ICT Core stage 1"
    3 = "Refused CBA"
    4 = "Took CBA"
    5 = "Uncategorized"
    .N = "Not stated or inferred"
  ;
  VALUE PLANNING_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE PPC_SCORE
    .N = "Not stated or inferred"
  ;
  VALUE PRC_PC_SCR
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_PF_Q1_
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_PF_Q2_
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_PF_Q3_
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_PV_Q1_
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_PV_SCR
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_SP_Q1_
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PRC_SP_SCR
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE PSLSTATUS
    1 = "Has PV"
    2 = "Literacy Related Non-Response"
    3 = "CBA Non-Response"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01A
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01B
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01C
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01D
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01E
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01F
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01G
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q01H
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q02A
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q02B
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q02C
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q02D
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03B
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03C
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03D
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03F
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03G
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q03H
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q04_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q05E
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q05F
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q05G
    1 = "Never"
    2 = "Less than once a month"
    3 = "Less than once a week but at least once a month"
    4 = "At least once a week but not every day"
    5 = "Every day"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q06_
    1 = "Straightforward"
    2 = "Moderate"
    3 = "Complex"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q07_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_G_Q08_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q010A
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q010B
    1 = "Hours"
    2 = "Days"
    3 = "Weeks"
    4 = "Months"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q020_
    1 = "offered in this prison, jail or another correctional facility"
    2 = "offered by a four-year college or university"
    3 = "offered by a community college"
    4 = "offered by a high school or vocational secondary school"
    5 = "offered through independent study"
    6 = "offered through correspondence or distance education"
    7 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q030_
    1 = "At this correctional facility"
    2 = "At another correctional facility"
    3 = "Other - for example, online"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q040_
    1 = "I was required to participate"
    2 = "To increase my knowledge or skills on a subject that interests me"
    3 = "To obtain a certificate"
    5 = "To increase my possibilities of getting a job when I am released"
    6 = "To increase possibilities of getting a job assignment"
    8 = "Family related reasons"
    9 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q050_
    1 = "Financial Problems"
    2 = "Did not do well in school"
    3 = "Did not like school or was bored in school"
    5 = "Expelled from school or asked to leave"
    6 = "Wanted to work"
    7 = "Wanted to go into the military"
    8 = "Personal illness, disability, or pregnancy"
    9 = "Family reasons such as illness or death of one of your parents, or child care responsibilities"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "School not available or not accessibile"
    11 = "Did not feel safe in school"
    12 = "Sent to jail, prison or detention center"
    13 = "Other"
  ;
  VALUE P_Q060_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q070_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q080_
    1 = "Grades 1-6"
    2 = "Grades 7-9"
    3 = "High school diploma or GED"
    4 = "Pre-associate education. Attended trade school, college, or university; no certificate or degree received."
    6 = "A certificate from a college or trade school for completion of a program prior to the associate/bachelor's degree."
    7 = "Associate degree"
    8 = "Bachelor's degree (e.g. BA, AB, BS)"
    9 = "Master's degree (e.g. MA, MS, MEng, MEd, MSW, MBA)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Professional degree (e.g. MD, DDS, DVM, LLB, JD)"
    11 = "Doctorate degree (e.g. PhD, EdD)"
  ;
  VALUE P_Q080_ISCED11F
    1 = "ISCED 1"
    2 = "ISCED 2"
    3 = "ISCED 3"
    4 = "ISCED 4"
    5 = "ISCED 5"
    6 = "ISCED 6"
    7 = "ISCED 7"
    8 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q090_
    1 = "I was required to participate"
    2 = "To increase my knowledge or skills on a subject that interests me"
    3 = "To obtain a certificate"
    5 = "To increase my possibilities of getting a job when I am released"
    6 = "To increase possibilities of getting a job assignment"
    8 = "Family related reasons"
    9 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q100_
    1 = "I do not have the qualifications necessary to enroll in this prison's program"
    2 = "I want to enroll in a higher level of classes than are available in this prison's program"
    3 = "I have a volunteer/work assignment I do not want to give up to attend classes"
    4 = "The waiting list is too long"
    5 = "The quality of the program being offered is poor"
    6 = "The academic classes/programs offered are not useful"
    7 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q120_
    1 = "Grades 1-6"
    2 = "Grades 7-9"
    3 = "High school diploma or GED"
    5 = "Pre-associate education. Attended trade school, college, or university; no certificate r degree received"
    6 = "A certificate from a college or trade school for completion of a program prior to the associate/bachelor's degree"
    7 = "Associate degree"
    8 = "Bachelor's degree (e.g. BA, AB, BS)"
    9 = "Master's degree (e.g. MA, MS, MEng, MEd, MSW, MBA)"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "Professional degree (e.g. MD, DDS, DVM, LLB, JD)"
    11 = "Doctorate degree (e.g. PhD, EdD)"
    12 = "No further education level completed"
  ;
  VALUE P_Q120_ISCED11F
    1 = "ISCED 1"
    2 = "ISCED 2"
    3 = "ISCED 3"
    4 = "ISCED 4"
    5 = "ISCED 5"
    6 = "ISCED 6"
    7 = "ISCED 7"
    8 = "ISCED 8"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    12 = "No further education level completed"
  ;
  VALUE P_Q130_
    1 = "offered in this prison, jail or other correctional facility"
    2 = "offered by a four-year college or university"
    3 = "offered by a community college"
    4 = "offered by a high school or vocational secondary school"
    5 = "offered through independent study"
    6 = "Offered through correspondence or distance education"
    7 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q140A
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q140B
    1 = "Hours"
    2 = "Days"
    3 = "Weeks"
    4 = "Years"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q150_
    1 = "I was required to participate"
    2 = "To increase my knowledge or skills on a subject that interests me"
    3 = "To obtain a certificate"
    4 = "To increase my possibilities of getting a job when I am released"
    5 = "To increase possibilities of getting a job assignment"
    6 = "Family related reasons"
    7 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q160_1_
    1 = "January"
    2 = "February"
    3 = "March"
    4 = "April"
    5 = "May"
    6 = "June"
    7 = "July"
    8 = "August"
    9 = "September"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
    10 = "October"
    11 = "November"
    12 = "Dember"
  ;
  VALUE P_Q160_2_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q170_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q180_
    1 = "Less than 6 months"
    2 = "6 to 12 months"
    3 = "1 to 2 years"
    4 = "More than 2 years"
    5 = "2 to 5 years"
    6 = "More than 5 years"
    7 = "Never"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190A
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190A_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190A_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190B
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190B_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190B_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190C
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190C_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190C_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190D
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190D_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190D_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190E
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190E_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190E_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190F
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190F_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190F_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190G
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190G_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190G_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190H
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190H_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190H_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190I
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190I_1_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190I_2_
    1 = "Self improvement"
    2 = "Family related reasons"
    3 = "To increase possibilities of getting a job assignment"
    4 = "To increase possibilities of getting a job when I am released"
    5 = "I was required to participate"
    6 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q190J
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q220_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q230_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_01_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_02_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_03_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_04_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_05_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q240_06_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q250_
    1 = "I do not have the educational qualifications to attend"
    2 = "I am not eligible to attend"
    3 = "I am currently on a waiting list to attend a course or program"
    4 = "I am not interested in the programs offered"
    5 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q260_
    1 = "Improve your English reading skills"
    2 = "Improve your English writing skills"
    3 = "Improve your arithmetic or mathematics skills"
    4 = "Improve your computer skills"
    5 = "Help you communicate or work better with other people"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q270_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q280_
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q290_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q300_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q310_
    1 = "A class offered in this prison, jail or another correctional facility"
    2 = "A class offered by a four-year college or university"
    3 = "A class offered by a community college"
    4 = "A class offered by a technical school or vendor"
    5 = "A class offered by a high school or vocational secondary school"
    6 = "A class offered directly by a hardware or software manufacturer"
    7 = "On the job training or apprenticeship"
    8 = "Independent study"
    9 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q320_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q330_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q340_
    1 = "A class offered in this prison, jail or another correctional facility"
    2 = "A class offered by a four-year college or university"
    3 = "A class offered by a community college"
    4 = "A class offered by a technical school or vendor"
    5 = "A class offered by a high school or vocational secondary school"
    6 = "On the job training or apprenticeship"
    7 = "Independent study"
    8 = "Other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q350A
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q350B
    1 = "Hours"
    2 = "Days"
    3 = "Weeks"
    4 = "Months"
    5 = "Years"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q360_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q370_
    1 = "Daily"
    2 = "Weekly"
    3 = "Monthly"
    4 = "Once or twice a year"
    5 = "Never"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q380_
    1 = "Less than two days"
    2 = "Two to six days"
    3 = "Seven to 10 days"
    4 = "More than 10 days"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q390_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q400_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q410_
    1 = "Yes"
    2 = "No"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q420_
    1 = "Current prison"
    2 = "Off-site"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_01_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_02_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_03_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_04_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_05_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_06_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_07_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q430_08_
    1 = "Marked"
    2 = "Not marked"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE P_Q440_
    1 = "Never married"
    2 = "Married"
    3 = "Legally separated or divorced"
    4 = "Widowed"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE RACETHN_4CAT
    1 = "Hispanic"
    2 = "White"
    3 = "Black"
    6 = "Other race"
    .N = "Not stated or inferred"
  ;
  VALUE READHOMEUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE READWORK_CUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE READWORK_CUSP_WLE_CA
    0 = "All zero response"
    1 = "Lowest to 20%"
    2 = "More than 20% to 40%"
    3 = "More than 40% to 60%"
    4 = "More than 60% to 80%"
    5 = "More than 80%"
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE READWORK_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE READWORK_SE_C
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE READYTOLEARN
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE REGION_US
    1 = "Northeast"
    2 = "Midwest"
    3 = "South"
    4 = "West"
  ;
  VALUE $REG_TL
    99999 = "Not stated or inferred"
  ;
  VALUE $REG_TL2_
    .N = "Not stated or inferred"
    AT11 = "Burgenland"
    AT12 = "Niederoesterreich"
    AT13 = "Wien"
    AT21 = "Karnten"
    AT22 = "Steiermark"
    AT31 = "Oberoesterreich"
    AT32 = "Salzburg"
    AT33 = "Tirol"
    AT34 = "Vorarlberg"
    AU1 = "New South Wales"
    AU2 = "Victoria"
    AU3 = "Qeensland"
    AU4 = "South Australia"
    AU5 = "Western Australia"
    AU6 = "Tasmania"
    AU7 = "Northern Territorry (Nt)"
    AU8 = "Australian Capital Territory (Act)"
    BE1 = "Reg -Bruxelles-Cap -/Brussels Hfdst -Gew -"
    BE2 = "Vlaams Gewest"
    BE3 = "Region Wallonne"
    CA10 = "Newfoundland And Labrador"
    CA11 = "Prince Edward Island"
    CA12 = "Nova Scotia"
    CA13 = "New Brunswick"
    CA24 = "Quebec"
    CA35 = "Ontario"
    CA46 = "Manitoba"
    CA47 = "Saskatchewan"
    CA48 = "Alberta"
    CA59 = "British Columbia"
    CA60 = "Yukon Territory"
    CA61 = "Northwest Territories And Nunavut"
    CH01 = "Region Lemanique"
    CH02 = "Espace Mittelland"
    CH03 = "Nordwestschweiz"
    CH04 = "Zürich"
    CH05 = "Ostschweiz"
    CH06 = "Zentralschweiz"
    CH07 = "Ticino"
    CL01 = "Tarapacá"
    CL02 = "Antofagasta"
    CL03 = "Atacama"
    CL04 = "Coquimbo"
    CL05 = "Valparaíso"
    CL06 = "O'Higgins"
    CL07 = "Maule"
    CL08 = "Bío-Bío"
    CL09 = "Araucanía"
    CL10 = "Los Lagos"
    CL11 = "Aysén"
    CL12 = "Magallanes"
    CL13 = "Santiago"
    CL14 = "Los Rios"
    CL15 = "Arica y Parinacota"
    CN010 = "Beijing"
    CN020 = "Tianjin"
    CN030 = "Hebei"
    CN040 = "Shanxi"
    CN050 = "Inner Mongolia"
    CN060 = "Liaoning"
    CN070 = "Jilin"
    CN080 = "Heilongjiang"
    CN090 = "Shanghai"
    CN100 = "Jiangsu"
    CN110 = "Zhejiang"
    CN120 = "Anhui"
    CN130 = "Fujian"
    CN140 = "Jiangxi"
    CN150 = "Shandong"
    CN160 = "Henan"
    CN170 = "Hubei"
    CN180 = "Hunan"
    CN190 = "Guangdong"
    CN191 = "Shenzhen - Guangdong"
    CN200 = "Guangxi"
    CN210 = "Hainan"
    CN220 = "Chongqing"
    CN230 = "Sichuan"
    CN240 = "Guizhou"
    CN250 = "Yunnan"
    CN260 = "Tibet"
    CN270 = "Shaanxi"
    CN280 = "Gansu"
    CN290 = "Qinghai"
    CN300 = "Ningxia"
    CN310 = "Xinjiang"
    CY00 = "Cyprus"
    CZ01 = "Praha"
    CZ02 = "Stredni Cechy"
    CZ03 = "Jihozapad"
    CZ04 = "Severozapad"
    CZ05 = "Severovychod"
    CZ06 = "Jihovyched"
    CZ07 = "Stredni Morava"
    CZ08 = "Moravskoslezko"
    DE1 = "Baden-Wuerttemberg"
    DE2 = "Bayern"
    DE3 = "Berlin"
    DE4 = "Brandenburg"
    DE5 = "Bremen"
    DE6 = "Hamburg"
    DE7 = "Hessen"
    DE8 = "Mecklenburg-Vorpommern"
    DE9 = "Niedersachsen"
    DEA = "Nordrhein-Westfalen"
    DEB = "Rheinland-Pfalz"
    DEC = "Saarland"
    DED = "Sachsen"
    DEE = "Sachsen-Anhalt"
    DEF = "Schleswig-Holstein"
    DEG = "Thueringen"
    DK01 = "Hovedstaden"
    DK02 = "Sjælland"
    DK03 = "Syddanmark"
    DK04 = "Midtjylland"
    DK05 = "Nordjylland"
    EE00 = "Estonia"
    ES11 = "Galicia"
    ES12 = "Asturias"
    ES13 = "Cantabria"
    ES21 = "Pais Vasco"
    ES22 = "Navarra"
    ES23 = "Rioja"
    ES24 = "Aragon"
    ES30 = "Madrid"
    ES41 = "Castilla-Leon"
    ES42 = "Castilla-La Mancha"
    ES43 = "Extremadura"
    ES51 = "Cataluna"
    ES52 = "Comunidad Valenciana"
    ES53 = "Baleares"
    ES61 = "Andalucia"
    ES62 = "Murcia"
    ES63 = "Ciudad Autónoma De Ceuta"
    ES64 = "Ciudad Autónoma De Melilla"
    ES70 = "Canarias"
    FI13 = "Ita-Suomi"
    FI18 = "Etela-Suomi"
    FI19 = "Lansi-Suomi"
    FI1A = "Pohjois-Suomi"
    FI20 = "Aland"
    FR10 = "Ile De France"
    FR21 = "Champagne-Ardenne"
    FR22 = "Picardie"
    FR23 = "Haute-Normandie"
    FR24 = "Centre"
    FR25 = "Basse-Normandie"
    FR26 = "Bourgogne"
    FR30 = "Nord-Pas-De-Calais"
    FR41 = "Lorraine"
    FR42 = "Alsace"
    FR43 = "Franche-Comte"
    FR51 = "Pays De La Loire"
    FR52 = "Bretagne"
    FR53 = "Poitou-Charentes"
    FR61 = "Aquitaine"
    FR62 = "Midi-Pyrenees"
    FR63 = "Limousin"
    FR71 = "Rhone-Alpes"
    FR72 = "Auvergne"
    FR81 = "Languedoc-Roussillon"
    FR82 = "Provence-Alpes-Cote D'Azur"
    FR83 = "Corse"
    GR1 = "Voreia Ellada"
    GR2 = "Kentriki Ellada"
    GR3 = "Attiki"
    GR4 = "Nisia Aigaiou - Kriti"
    HU10 = "Kosep-Magyarorszag"
    HU21 = "Kosep-Dunantul/Central Transdanubia"
    HU22 = "Nyugat-Dunantul/Western Transdanubia"
    HU23 = "Del-Dunantul/Southern Transdanubia"
    HU31 = "Eszak-Magyarorszag/Northern Hungary"
    HU32 = "Eszak-Alfold/Northern Great Plain"
    HU33 = "Del-Alfold/Southern Great Plain"
    IE01 = "Border - Midlands And Western"
    IE02 = "Southern And Eastern"
    IL01 = "Jerusalem district"
    IL02 = "Northern district"
    IL03 = "Haifa district"
    IL04 = "Central district"
    IL05 = "Tel Aviv district"
    IL06 = "Southern district"
    IL07 = "Judea and Samaria"
    IN010 = "Andhra Pradesh"
    IN030 = "Assam"
    IN040 = "Bihar"
    IN050 = "Chhattisgarh"
    IN060 = "National Capital Territory of Delhi"
    IN070 = "Goa"
    IN080 = "Gujarat"
    IN090 = "Haryana"
    IN100 = "Himachal Pradesh"
    IN110 = "Jammu and Kashmir"
    IN120 = "Jharkhand"
    IN130 = "Karnataka"
    IN140 = "Kerala"
    IN150 = "Madhya Pradesh"
    IN160 = "Maharashtra"
    IN210 = "Orissa"
    IN220 = "Punjab"
    IN230 = "Rajasthan"
    IN250 = "Tamil Nadu"
    IN270 = "Uttarakhand"
    IN280 = "Uttar Pradesh"
    IN290 = "West Bengal"
    IN330 = "Lakshadweep"
    IN340 = "Puducherry"
    IN350 = "Chandigarh"
    IS01 = "Capital Region"
    IS02 = "Other Regions"
    ITC1 = "Piemonte"
    ITC2 = "Valle D'Aosta"
    ITC3 = "Liguria"
    ITC4 = "Lombardia"
    ITD1 = "Provincia Autonoma Di Bolzano-Bozen"
    ITD2 = "Provincia Autonoma Di Trento"
    ITD3 = "Veneto"
    ITD4 = "Friuli-Venezia Giulia"
    ITD5 = "Emilia-Romagna"
    ITE1 = "Toscana"
    ITE2 = "Umbria"
    ITE3 = "Marche"
    ITE4 = "Lazio"
    ITF1 = "Abruzzo"
    ITF2 = "Molise"
    ITF3 = "Campania"
    ITF4 = "Puglia"
    ITF5 = "Basilicata"
    ITF6 = "Calabria"
    ITG1 = "Sicilia"
    ITG2 = "Sardegna"
    JPA = "Hokkaido"
    JPB = "Tohoku"
    JPC = "Southern-Kanto"
    JPD = "Northern-Kanto,Koshin"
    JPE = "Hokuriku"
    JPF = "Tokai"
    JPG = "Kinki"
    JPH = "Chugoku"
    JPI = "Shikoku"
    JPJ = "Kyusyu,Okinawa"
    KR01 = "Capital Region"
    KR02 = "Gyeongnam Region"
    KR03 = "Gyeonbuk Region"
    KR04 = "Jeolla Region"
    KR05 = "Chungcheong Region"
    KR06 = "Gangwon Region"
    KR07 = "Jeju"
    LU00 = "Luxembourg"
    ME01 = "Aguacalientes"
    ME02 = "Baja California Norte"
    ME03 = "Baja California Sur"
    ME04 = "Campeche"
    ME05 = "Coahuila"
    ME06 = "Colima"
    ME07 = "Chiapas"
    ME08 = "Chihuahua"
    ME09 = "Distrito Federal"
    ME10 = "Durango"
    ME11 = "Guanajuato"
    ME12 = "Guerrero"
    ME13 = "Hidalgo"
    ME14 = "Jalisco"
    ME15 = "Mexico"
    ME16 = "Michoacan"
    ME17 = "Morelos"
    ME18 = "Nayarit"
    ME19 = "Nuevo Leon"
    ME20 = "Oaxaca"
    ME21 = "Puebla"
    ME22 = "Queretaro"
    ME23 = "Quintana Roo"
    ME24 = "San Luis Potosi"
    ME25 = "Sinaloa"
    ME26 = "Sonora"
    ME27 = "Tabasco"
    ME28 = "Tamaulipas"
    ME29 = "Tlaxcala"
    ME30 = "Veracruz"
    ME31 = "Yucatan"
    ME32 = "Zacatecas"
    NO01 = "Oslo Og Akershus"
    NO02 = "Hedmark Og Oppland"
    NO03 = "Sør-Østlandet"
    NO04 = "Agder Og Rogaland"
    NO05 = "Vestlandet"
    NO06 = "Trøndelag"
    NO07 = "Nord-Norge"
    NZ01 = "North Island"
    NZ02 = "South Island"
    PL11 = "Lodzkie"
    PL12 = "Mazowieckie"
    PL21 = "Malopolskie"
    PL22 = "Slaskie"
    PL31 = "Lubelskie"
    PL32 = "Podkarpackie"
    PL33 = "Swietokrzyskie"
    PL34 = "Podlaskie"
    PL41 = "Wielkopolskie"
    PL42 = "Zachodniopomorskie"
    PL43 = "Lubuskie"
    PL51 = "Dolnoslaskie"
    PL52 = "Opolskie"
    PL61 = "Kujawsko-Pomorskie"
    PL62 = "Warminsko-Mazurskie"
    PL63 = "Pomorskie"
    PT11 = "Norte"
    PT15 = "Algarve"
    PT16 = "Centro (P)"
    PT17 = "Lisboa"
    PT18 = "Alentejo"
    PT20 = "Região Autónoma Dos Açores"
    PT30 = "Região Autónoma Da Madeira"
    RU01 = "Belgograd Oblast"
    RU02 = "Bryansk Oblast"
    RU03 = "Vladimir Oblast"
    RU04 = "Voronezh Oblast"
    RU05 = "Ivanovo Oblast"
    RU06 = "Kaluga Oblast"
    RU07 = "Kostroma Oblast"
    RU08 = "Kursk Oblast"
    RU09 = "Lipetsk Oblast"
    RU10 = "Moscow Oblast"
    RU11 = "Oryol Oblast"
    RU12 = "Ryazan Oblast"
    RU13 = "Smolensk Oblast"
    RU14 = "Tambov Oblast"
    RU15 = "Tversk Oblast"
    RU16 = "Tulsk Oblast"
    RU17 = "Yaroslavl Oblast"
    RU18 = "City of Moscow"
    RU19 = "Karelian republic"
    RU20 = "Komi republic"
    RU21 = "Komi republic"
    RU22 = "Vologda Oblast"
    RU23 = "Kaliningrad Oblast"
    RU24 = "Leningrad Oblast"
    RU25 = "Murmansk Oblast"
    RU26 = "Novgorod Oblast"
    RU27 = "Pskov Oblast"
    RU28 = "Federal City of Saint Petersburg"
    RU29 = "Republic of Adygea"
    RU30 = "Republic of Dagestan"
    RU31 = "Republic of Ingushetia"
    RU32 = "Balkar Republic"
    RU33 = "Republic of Kalmukia"
    RU34 = "Karachay-Cerkhess Republic"
    RU35 = "North Ossetia"
    RU36 = "Chechen Republic"
    RU37 = "Krasnodar Krai"
    RU38 = "Stavropol Krai"
    RU39 = "Astrachan Oblast"
    RU40 = "Volgograd Oblast"
    RU41 = "Rostov Oblast"
    RU42 = "Republic of Bashkorstostan"
    RU43 = "Mari El Republic"
    RU44 = "Republic of Mordovia"
    RU45 = "Republic of Tatarstan"
    RU46 = "Udmurt Republic"
    RU47 = "Chuvash Republic"
    RU48 = "Perm Krai"
    RU49 = "Kirov Oblast"
    RU50 = "Nizhny Novgorod Oblast"
    RU51 = "Orenburg Oblast"
    RU52 = "Penza Oblast"
    RU53 = "Samara Oblast"
    RU54 = "Saratov Oblast"
    RU55 = "Ulianov oblast"
    RU56 = "Kurgan Oblast"
    RU57 = "Sverdlov Oblast"
    RU58 = "Tiumen Oblast"
    RU59 = "Chelyabinsk Oblast"
    RU60 = "Republic of Altai"
    RU61 = "Buryat Republic"
    RU62 = "Tyva Republic"
    RU63 = "Republic of Khakassia"
    RU64 = "Altai Krai"
    RU65 = "Krasnoyarsk Krai"
    RU66 = "Irkutsk Oblast"
    RU67 = "Kemerovo oblast"
    RU68 = "Novosibirsk Obalst"
    RU69 = "Omsk Oblast"
    RU70 = "Tomsk Oblast"
    RU71 = "Chitinsk Oblast"
    RU72 = "Sakha Republic (Yakutia)"
    RU73 = "Primorsky Krai"
    RU74 = "Khabarovsk Krai"
    RU75 = "Amur Oblast"
    RU76 = "Kamchatka Krai"
    RU77 = "Magadan Oblast"
    RU78 = "Sakhalin Oblast"
    RU79 = "Jewish Autonomous Obalst"
    RU80 = "Chukotka Autonomous Okrug"
    SI01 = "Vzhodna Slovenija"
    SI02 = "Zahodna Slovenija"
    SK01 = "Bratislav Kraj"
    SK02 = "Zapadne Slovensko"
    SK03 = "Stredne Slovensko"
    SK04 = "Vychodne Slovensko"
    TR10 = "Istanbul"
    TR21 = "Tekirdag"
    TR22 = "Balikesir"
    TR31 = "Izmir"
    TR32 = "Aydin"
    TR33 = "Manisa"
    TR41 = "Bursa"
    TR42 = "Kocaeli"
    TR51 = "Ankara"
    TR52 = "Konya"
    TR61 = "Antalya"
    TR62 = "Adana"
    TR63 = "Hatay"
    TR71 = "Kirikkale"
    TR72 = "Kayseri"
    TR81 = "Zonguldak"
    TR82 = "Kastamonu"
    TR83 = "Samsun"
    TR90 = "Trabzon"
    TRA1 = "Erzurum"
    TRA2 = "Agri"
    TRB1 = "Malatya"
    TRB2 = "Van"
    TRC1 = "Gaziantep"
    TRC2 = "Sanliurfa"
    TRC3 = "Mardin"
    UKC = "North East"
    UKD = "North West (Including Merseyside)"
    UKE = "Yorkshire And Humberside"
    UKF = "East Midlands"
    UKG = "West Midlands"
    UKH = "Eastern"
    UKI = "London"
    UKJ = "South East"
    UKK = "South West"
    UKL = "Wales"
    UKM = "Scotland"
    UKN = "Northern Ireland"
    US01 = "Alabama"
    US02 = "Alaska"
    US04 = "Arizona"
    US05 = "Arkansas"
    US06 = "California"
    US08 = "Colorado"
    US09 = "Connecticut"
    US10 = "Delaware"
    US11 = "District Of Columbia"
    US12 = "Florida"
    US13 = "Georgia"
    US15 = "Hawaii"
    US16 = "Idaho"
    US17 = "Illinois"
    US18 = "Indiana"
    US19 = "Iowa"
    US20 = "Kansas"
    US21 = "Kentucky"
    US22 = "Louisiana"
    US23 = "Maine"
    US24 = "Maryland"
    US25 = "Massachusetts"
    US26 = "Michigan"
    US27 = "Minnesota"
    US28 = "Mississippi"
    US29 = "Missouri"
    US30 = "Montana"
    US31 = "Nebraska"
    US32 = "Nevada"
    US33 = "New Hampshire"
    US34 = "New Jersey"
    US35 = "New Mexico"
    US36 = "New York"
    US37 = "North Carolina"
    US38 = "North Dakota"
    US39 = "Ohio"
    US40 = "Oklahoma"
    US41 = "Oregon"
    US42 = "Pennsylvania"
    US44 = "Rhode Island"
    US45 = "South Carolina"
    US46 = "South Dakota"
    US47 = "Tennessee"
    US48 = "Texas"
    US49 = "Utah"
    US50 = "Vermont"
    US51 = "Virginia"
    US53 = "Washington"
    US54 = "West Virginia"
    US55 = "Wisconsin"
    US56 = "Wyoming"
    nl1 = "Noord-Nederland"
    nl2 = "Oost-Nederland"
    nl3 = "West-Nederland"
    nl4 = "Zuid-Nederland"
    se11 = "Stockholm"
    se12 = "Östra Mellansverige"
    se21 = "Småland med öarna"
    se22 = "Sydsverige"
    se23 = "Västsverige"
    se31 = "Norra Mellansverige"
    se32 = "Mellersta Norrland"
    se33 = "Övre Norrland"
  ;
  VALUE SAMPFLAG
    1 = "HH U.S. Main Study and National Supplement (NSHH)"
    2 = "Prison National Supplement (NSPR)"
  ;
  VALUE SECLGRGNUS_C
    1 = "North America and Western Europe"
    2 = "other"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE U01A000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U01A000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U01A000S
    0 = "Incorrect"
    1 = "Partial 1"
    2 = "Partial 2"
    3 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U01A000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U01B000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U01B000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U01B000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U01B000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U02X000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U02X000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U02X000S
    0 = "Incorrect"
    1 = "Partial 1"
    2 = "Partial 2"
    3 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U02X000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U03A000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U03A000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U03A000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U03A000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U04A000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U04A000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U04A000S
    0 = "Incorrect"
    1 = "Partial 1"
    2 = "Partial 2"
    3 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U04A000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U06A000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U06A000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U06A000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U06A000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U06B000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U06B000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U06B000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U06B000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U07X000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U07X000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U07X000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U07X000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U11B000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U11B000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U11B000S
    0 = "Incorrect"
    1 = "Partial 1"
    2 = "Partial 2"
    3 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U11B000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U16X000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U16X000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U16X000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U16X000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U19A000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U19A000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U19A000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U19A000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U19B000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U19B000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U19B000S
    0 = "Incorrect"
    1 = "Partial"
    2 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U19B000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U21X000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U21X000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U21X000S
    0 = "Missing"
    1 = "Correct"
    7 = "Incorrect"
    .N = "Not reached/Not attempted"
  ;
  VALUE U21X000T
    .N = "Not reached/Not attempted"
  ;
  VALUE U23X000A
    .N = "Not reached/Not attempted"
  ;
  VALUE U23X000F
    .N = "Not reached/Not attempted"
  ;
  VALUE U23X000S
    0 = "Incorrect"
    1 = "Partial 1"
    2 = "Partial 2"
    3 = "Correct"
    .N = "Not reached/Not attempted"
    .R = "No response"
  ;
  VALUE U23X000T
    .N = "Not reached/Not attempted"
  ;
  VALUE $USCIP_C_C
    01 = "Agriculture, agriculture operations, and related sciences"
    01.00 = "Agriculture, general"
    01.01 = "Agricultural business and management"
    01.02 = "Agricultural mechanization"
    01.03 = "Agricultural production operations"
    01.04 = "Agricultural and food products processing"
    01.05 = "Agricultural and domestic animal services"
    01.06 = "Applied horticulture and horticultural business services"
    01.07 = "International agriculture"
    01.08 = "Agricultural public services"
    01.09 = "Animal sciences"
    01.10 = "Food science and technology"
    01.11 = "Plant sciences"
    01.12 = "Soil sciences"
    01.99 = "Agriculture, agriculture operations, and related sciences, other"
    03 = "Natural resources and conservation"
    03.01 = "Natural resources conservation and research"
    03.02 = "Natural resources management and policy"
    03.03 = "Fishing and fisheries sciences and management"
    03.05 = "Forestry"
    03.06 = "Wildlife and wildlands science and management"
    03.99 = "Natural resources and conservation, other"
    04 = "Architecture and related services"
    04.02 = "Architecture"
    04.03 = "City/urban, community and regional planning"
    04.04 = "Environmental design"
    04.05 = "Interior architecture"
    04.06 = "Landscape architecture"
    04.08 = "Architectural history and criticism"
    04.09 = "Architectural sciences and technology"
    04.10 = "Real estate development"
    04.99 = "Architecture and related services, other"
    05 = "Area, ethnic, cultural, gender, and group studies"
    05.01 = "Area studies"
    05.02 = "Ethnic, cultural minority, gender, and group studies"
    09 = "Communication, journalism, and related programs"
    09.01 = "Communication and media studies"
    09.04 = "Journalism"
    09.07 = "Radio, television, and digital communication"
    09.09 = "Public relations, advertising, and applied communication"
    09.10 = "Publishing"
    09.99 = "Communication, journalism, and related programs, other"
    10 = "Communications technologies/technicians and support services"
    10.01 = "Communications technology/technician"
    10.02 = "Audiovisual communications technologies/technicians"
    10.03 = "Graphic communications"
    10.99 = "Communications technologies/technicians and support services, other"
    11 = "Computer and information sciences and support services"
    11.01 = "Computer and information sciences, general"
    11.02 = "Computer programming"
    11.03 = "Data processing"
    11.04 = "Information science/studies"
    11.05 = "Computer systems analysis"
    11.06 = "Data entry/microcomputer applications"
    11.07 = "Computer science"
    11.08 = "Computer software and media applications"
    11.09 = "Computer systems networking and telecommunications"
    11.10 = "Computer/information technology administration and management"
    11.99 = "Computer and information sciences and support services, other"
    12 = "Personal and culinary services"
    12.03 = "Funeral service and mortuary science"
    12.04 = "Cosmetology and related personal grooming services"
    12.05 = "Culinary arts and related services"
    12.99 = "Personal and culinary services, other"
    13 = "Education"
    13.01 = "Education, general"
    13.02 = "Bilingual, multilingual, and multicultural education"
    13.03 = "Curriculum and instruction"
    13.04 = "Educational administration and supervision"
    13.05 = "Educational/instructional media design"
    13.06 = "Educational assessment, evaluation, and research"
    13.07 = "International and comparative education"
    13.09 = "Social and philosophical foundations of education"
    13.10 = "Special education and teaching"
    13.11 = "Student counseling and personnel services"
    13.12 = "Teacher education and professional development, specific levels and methods"
    13.13 = "Teacher education and professional development, specific subject areas"
    13.14 = "Teaching english or french as a second or foreign language"
    13.15 = "Teaching assistants/aides"
    13.99 = "Education, other"
    14 = "Engineering"
    14.01 = "Engineering, general"
    14.02 = "Aerospace, aeronautical and astronautical engineering"
    14.03 = "Agricultural engineering"
    14.04 = "Architectural engineering"
    14.05 = "Biomedical/medical engineering"
    14.06 = "Ceramic sciences and engineering"
    14.07 = "Chemical engineering"
    14.08 = "Civil engineering"
    14.09 = "Computer engineering"
    14.10 = "Electrical, electronics and communications engineering"
    14.11 = "Engineering mechanics"
    14.12 = "Engineering physics"
    14.13 = "Engineering science"
    14.14 = "Environmental/environmental health engineering"
    14.18 = "Materials engineering"
    14.19 = "Mechanical engineering"
    14.20 = "Metallurgical engineering"
    14.21 = "Mining and mineral engineering"
    14.22 = "Naval architecture and marine engineering"
    14.23 = "Nuclear engineering"
    14.24 = "Ocean engineering"
    14.25 = "Petroleum engineering"
    14.27 = "Systems engineering"
    14.28 = "Textile sciences and engineering"
    14.32 = "Polymer/plastics engineering"
    14.33 = "Construction engineering"
    14.34 = "Forest engineering"
    14.35 = "Industrial engineering"
    14.36 = "Manufacturing engineering"
    14.37 = "Operations research"
    14.38 = "Surveying engineering"
    14.39 = "Geological/geophysical engineering"
    14.40 = "Paper science and engineering"
    14.41 = "Electromechanical engineering"
    14.42 = "Mechatronics, robotics, and automation engineering"
    14.43 = "Biochemical engineering"
    14.44 = "Engineering chemistry"
    14.45 = "Biological/biosystems engineering"
    14.99 = "Engineering, other"
    15 = "Engineering technologies and engineering-related fields"
    15.00 = "Engineering technology, general"
    15.01 = "Architectural engineering technologies/technicians"
    15.02 = "Civil engineering technologies/technicians"
    15.03 = "Electrical engineering technologies/technicians"
    15.04 = "Electromechanical instrumentation and maintenance technologies/technicians"
    15.05 = "Environmental control technologies/technicians"
    15.06 = "Industrial production technologies/technicians"
    15.07 = "Quality control and safety technologies/technicians"
    15.08 = "Mechanical engineering related technologies/technicians"
    15.09 = "Mining and petroleum technologies/technicians"
    15.10 = "Construction engineering technologies"
    15.11 = "Engineering-related technologies"
    15.12 = "Computer engineering technologies/technicians"
    15.13 = "Drafting/design engineering technologies/technicians"
    15.14 = "Nuclear engineering technologies/technicians"
    15.15 = "Engineering-related fields"
    15.16 = "Nanotechnology"
    15.99 = "Engineering technologies/technicians, other"
    16 = "Foreign languages, literatures, and linguistics"
    16.01 = "Linguistic, comparative, and related language studies and services"
    16.02 = "African languages, literatures, and linguistics"
    16.03 = "East asian languages, literatures, and linguistics"
    16.04 = "Slavic, baltic and albanian languages, literatures, and linguistics"
    16.05 = "Germanic languages, literatures, and linguistics"
    16.06 = "Modern greek language and literature"
    16.07 = "South asian languages, literatures, and linguistics"
    16.08 = "Iranian/persian languages, literatures, and linguistics"
    16.09 = "Romance languages, literatures, and linguistics"
    16.10 = "American indian/native american languages, literatures, and linguistics"
    16.11 = "Middle/near eastern and semitic languages, literatures, and linguistics"
    16.12 = "Classics and classical languages, literatures, and linguistics"
    16.13 = "Celtic languages, literatures, and linguistics"
    16.14 = "Southeast asian and australasian/pacific languages, literatures, and linguistics"
    16.15 = "Turkic, uralic-altaic, caucasian, and central asian languages, literatures, and linguistics"
    16.16 = "American sign language"
    16.99 = "Foreign languages, literatures, and linguistics, other"
    19 = "Family and consumer sciences/human sciences"
    19.00 = "Work and family studies"
    19.01 = "Family and consumer sciences/human sciences, general"
    19.02 = "Family and consumer sciences/human sciences business services"
    19.04 = "Family and consumer economics and related studies"
    19.05 = "Foods, nutrition, and related services"
    19.06 = "Housing and human environments"
    19.07 = "Human development, family studies, and related services"
    19.09 = "Apparel and textiles"
    19.99 = "Family and consumer sciences/human sciences, other"
    22 = "Legal professions and studies"
    22.00 = "Non-professional general legal studies (undergraduate)"
    22.01 = "Law"
    22.02 = "Legal research and advanced professional studies"
    22.03 = "Legal support services"
    22.99 = "Legal professions and studies, other"
    23 = "English language and literature/letters"
    23.01 = "English language and literature, general"
    23.13 = "Rhetoric and composition/writing studies"
    23.14 = "Literature"
    23.99 = "English language and literature/letters, other"
    24 = "Liberal arts and sciences, general studies and humanities"
    24.01 = "Liberal arts and sciences, general studies and humanities"
    25 = "Library science"
    25.01 = "Library science and administration"
    25.03 = "Library and archives assisting"
    25.99 = "Library science, other"
    26 = "Biological and biomedical sciences"
    26.01 = "Biology, general"
    26.02 = "Biochemistry, biophysics and molecular biology"
    26.03 = "Botany/plant biology"
    26.04 = "Cell/cellular biology and anatomical sciences"
    26.05 = "Microbiological sciences and immunology"
    26.07 = "Zoology/animal biology"
    26.08 = "Genetics"
    26.09 = "Physiology, pathology and related sciences"
    26.10 = "Pharmacology and toxicology"
    26.11 = "Biomathematics, bioinformatics, and computational biology"
    26.12 = "Biotechnology"
    26.13 = "Ecology, evolution, systematics, and population biology"
    26.14 = "Molecular medicine"
    26.15 = "Neurobiology and neurosciences"
    26.99 = "Biological and biomedical sciences, other"
    27 = "Mathematics and statistics"
    27.01 = "Mathematics"
    27.03 = "Applied mathematics"
    27.05 = "Statistics"
    27.99 = "Mathematics and statistics, other"
    28 = "Military science, leadership and operational art"
    28.01 = "Air force rotc, air science and operations"
    28.03 = "Army rotc, military science and operations"
    28.04 = "Navy/marine rotc, naval science and operations"
    28.05 = "Military science and operational studies"
    28.06 = "Security policy and strategy"
    28.07 = "Military economics and management"
    28.99 = "Military science, leadership and operational art, other"
    29 = "Military technologies and applied sciences"
    29.02 = "Intelligence, command control and information operations"
    29.03 = "Military applied sciences"
    29.04 = "Military systems and maintenance technology"
    29.99 = "Military technologies and applied sciences, other"
    30 = "Multi/interdisciplinary studies"
    30.00 = "Multi-/interdisciplinary studies, general"
    30.01 = "Biological and physical sciences"
    30.05 = "Peace studies and conflict resolution"
    30.06 = "Systems science and theory"
    30.08 = "Mathematics and computer science"
    30.10 = "Biopsychology"
    30.11 = "Gerontology"
    30.12 = "Historic preservation and conservation"
    30.13 = "Medieval and renaissance studies"
    30.14 = "Museology/museum studies"
    30.15 = "Science, technology and society"
    30.16 = "Accounting and computer science"
    30.17 = "Behavioral sciences"
    30.18 = "Natural sciences"
    30.19 = "Nutrition sciences"
    30.20 = "International/global studies"
    30.21 = "Holocaust and related studies"
    30.22 = "Classical and ancient studies"
    30.23 = "Intercultural/multicultural and diversity studies"
    30.25 = "Cognitive science"
    30.26 = "Cultural studies/critical theory and analysis"
    30.27 = "Human biology"
    30.28 = "Dispute resolution"
    30.29 = "Maritime studies"
    30.30 = "Computational science"
    30.31 = "Human computer interaction"
    30.32 = "Marine sciences"
    30.33 = "Sustainability studies"
    30.99 = "Multi/interdisciplinary studies, other"
    31 = "Parks, recreation, leisure, and fitness studies"
    31.01 = "Parks, recreation and leisure studies"
    31.03 = "Parks, recreation and leisure facilities management"
    31.05 = "Health and physical education/fitness"
    31.06 = "Outdoor education"
    31.99 = "Parks, recreation, leisure, and fitness studies, other"
    32 = "Basic skills and developmental/remedial education"
    32.01 = "Basic skills and developmental/remedial education"
    33 = "Citizenship activities"
    33.01 = "Citizenship activities"
    34 = "Health-related knowledge and skills"
    34.01 = "Health-related knowledge and skills"
    35 = "Interpersonal and social skills"
    35.01 = "Interpersonal and social skills"
    36 = "Leisure and recreational activities"
    36.01 = "Leisure and recreational activities"
    37 = "Personal awareness and self-improvement"
    37.01 = "Personal awareness and self-improvement"
    38 = "Philosophy and religious studies"
    38.00 = "Philosophy and religious studies, general"
    38.01 = "Philosophy"
    38.02 = "Religion/religious studies"
    38.99 = "Philosophy and religious studies, other"
    39 = "Theology and religious vocations"
    39.02 = "Bible/biblical studies"
    39.03 = "Missions/missionary studies and missiology"
    39.04 = "Religious education"
    39.05 = "Religious/sacred music"
    39.06 = "Theological and ministerial studies"
    39.07 = "Pastoral counseling and specialized ministries"
    39.99 = "Theology and religious vocations, other"
    40 = "Physical sciences"
    40.01 = "Physical sciences"
    40.02 = "Astronomy and astrophysics"
    40.04 = "Atmospheric sciences and meteorology"
    40.05 = "Chemistry"
    40.06 = "Geological and earth sciences/geosciences"
    40.08 = "Physics"
    40.10 = "Materials sciences"
    40.99 = "Physical sciences, other"
    41 = "Science technologies/technicians"
    41.00 = "Science technologies/technicians, general"
    41.01 = "Biology technician/biotechnology laboratory technician"
    41.02 = "Nuclear and industrial radiologic technologies/technicians"
    41.03 = "Physical science technologies/technicians"
    41.99 = "Science technologies/technicians, other"
    42 = "Psychology"
    42.01 = "Psychology, general"
    42.27 = "Research and experimental psychology"
    42.28 = "Clinical, counseling and applied psychology"
    42.99 = "Psychology, other"
    43 = "Homeland security, law enforcement, firefighting and related protective services"
    43.01 = "Criminal justice and corrections"
    43.02 = "Fire protection"
    43.03 = "Homeland security"
    43.99 = "Homeland security, law enforcement, firefighting and related protective services, other"
    44 = "Public administration and social service professions"
    44.00 = "Human services, general"
    44.02 = "Community organization and advocacy"
    44.04 = "Public administration"
    44.05 = "Public policy analysis"
    44.07 = "Social work"
    44.99 = "Public administration and social service professions, other"
    45 = "Social sciences"
    45.01 = "Social sciences, general"
    45.02 = "Anthropology"
    45.03 = "Archeology"
    45.04 = "Criminology"
    45.05 = "Demography and population studies"
    45.06 = "Economics"
    45.07 = "Geography and cartography"
    45.09 = "International relations and national security studies"
    45.10 = "Political science and government"
    45.11 = "Sociology"
    45.12 = "Urban studies/affairs"
    45.13 = "Sociology and anthropology"
    45.14 = "Rural sociology"
    45.99 = "Social sciences, other"
    46 = "Construction trades"
    46.00 = "Construction trades, general"
    46.01 = "Mason/masonry"
    46.02 = "Carpenters"
    46.03 = "Electrical and power transmission installers"
    46.04 = "Building/construction finishing, management, and inspection"
    46.05 = "Plumbing and related water supply services"
    46.99 = "Construction trades, other"
    47 = "Mechanic and repair technologies/technicians"
    47.00 = "Mechanics and repairers, general"
    47.01 = "Electrical/electronics maintenance and repair technology"
    47.02 = "Heating, air conditioning, ventilation and refrigeration maintenance technology/technician (hac, hacr, hvac, hvacr)"
    47.03 = "Heavy/industrial equipment maintenance technologies"
    47.04 = "Precision systems maintenance and repair technologies"
    47.06 = "Vehicle maintenance and repair technologies"
    47.99 = "Mechanic and repair technologies/technicians, other"
    48 = "Precision production"
    48.00 = "Precision production trades, general"
    48.03 = "Leatherworking and upholstery"
    48.05 = "Precision metal working"
    48.07 = "Woodworking"
    48.08 = "Boilermaking/boilermaker"
    48.99 = "Precision production, other"
    49 = "Transportation and materials moving"
    49.01 = "Air transportation"
    49.02 = "Ground transportation"
    49.03 = "Marine transportation"
    49.99 = "Transportation and materials moving, other"
    50 = "Visual and performing arts"
    50.01 = "Visual and performing arts, general"
    50.02 = "Crafts/craft design, folk art and artisanry"
    50.03 = "Dance"
    50.04 = "Design and applied arts"
    50.05 = "Drama/theatre arts and stagecraft"
    50.06 = "Film/video and photographic arts"
    50.07 = "Fine and studio arts"
    50.09 = "Music"
    50.10 = "Arts, entertainment,and media management"
    50.99 = "Visual and performing arts, other"
    51 = "Health professions and related programs"
    51.00 = "Health services/allied health/health sciences, general"
    51.01 = "Chiropractic"
    51.02 = "Communication disorders sciences and services"
    51.04 = "Dentistry"
    51.05 = "Advanced/graduate dentistry and oral sciences"
    51.06 = "Dental support services and allied professions"
    51.07 = "Health and medical administrative services"
    51.08 = "Allied health and medical assisting services"
    51.09 = "Allied health diagnostic, intervention, and treatment professions"
    51.10 = "Clinical/medical laboratory science/research and allied professions"
    51.11 = "Health/medical preparatory programs"
    51.12 = "Medicine"
    51.14 = "Medical clinical sciences/graduate medical studies"
    51.15 = "Mental and social health services and allied professions"
    51.17 = "Optometry"
    51.18 = "Ophthalmic and optometric support services and allied professions"
    51.19 = "Osteopathic medicine/osteopathy"
    51.20 = "Pharmacy, pharmaceutical sciences, and administration"
    51.21 = "Podiatric medicine/podiatry"
    51.22 = "Public health"
    51.23 = "Rehabilitation and therapeutic professions"
    51.24 = "Veterinary medicine"
    51.25 = "Veterinary biomedical and clinical sciences"
    51.26 = "Health aides/attendants/orderlies"
    51.27 = "Medical illustration and informatics"
    51.31 = "Dietetics and clinical nutrition services"
    51.32 = "Bioethics/medical ethics"
    51.33 = "Alternative and complementary medicine and medical systems"
    51.34 = "Alternative and complementary medical support services"
    51.35 = "Somatic bodywork and related therapeutic services"
    51.36 = "Movement and mind-body therapies and education"
    51.37 = "Energy and biologically based therapies"
    51.38 = "Registered nursing, nursing administration, nursing research and clinical nursing"
    51.39 = "Practical nursing, vocational nursing and nursing assistants"
    51.99 = "Health professions and related clinical sciences, other"
    52 = "Business, management, marketing, and related support services"
    52.01 = "Business/commerce, general"
    52.02 = "Business administration, management and operations"
    52.03 = "Accounting and related services"
    52.04 = "Business operations support and assistant services"
    52.05 = "Business/corporate communications"
    52.06 = "Business/managerial economics"
    52.07 = "Entrepreneurial and small business operations"
    52.08 = "Finance and financial management services"
    52.09 = "Hospitality administration/management"
    52.10 = "Human resources management and services"
    52.11 = "International business"
    52.12 = "Management information systems and services"
    52.13 = "Management sciences and quantitative methods"
    52.14 = "Marketing"
    52.15 = "Real estate"
    52.16 = "Taxation"
    52.17 = "Insurance"
    52.18 = "General sales, merchandising and related marketing operations"
    52.19 = "Specialized sales, merchandising and marketing operations"
    52.20 = "Construction management"
    52.21 = "Telecommunications management"
    52.99 = "Business, management, marketing, and related support services, other"
    53 = "High school/secondary diplomas and certificates"
    53.01 = "High school/secondary diploma programs"
    53.02 = "High school/secondary certificate programs"
    54 = "History"
    54.01 = "History"
    60 = "Residency programs"
    60.01 = "Dental residency programs"
    60.03 = "Veterinary residency programs"
    60.04 = "Medical residency programs - general certificates"
    60.05 = "Medical residency programs - subspecialty certificates"
    60.06 = "Podiatric medicine residency programs"
    99996 = "Valid skip"
    99997 = "Don't know"
    99998 = "Refused"
    99999 = "Not stated or inferred"
  ;
  VALUE $USCIP_H_C
    01 = "Agriculture, agriculture operations, and related sciences"
    01.00 = "Agriculture, general"
    01.01 = "Agricultural business and management"
    01.02 = "Agricultural mechanization"
    01.03 = "Agricultural production operations"
    01.04 = "Agricultural and food products processing"
    01.05 = "Agricultural and domestic animal services"
    01.06 = "Applied horticulture and horticultural business services"
    01.07 = "International agriculture"
    01.08 = "Agricultural public services"
    01.09 = "Animal sciences"
    01.10 = "Food science and technology"
    01.11 = "Plant sciences"
    01.12 = "Soil sciences"
    01.99 = "Agriculture, agriculture operations, and related sciences, other"
    03 = "Natural resources and conservation"
    03.01 = "Natural resources conservation and research"
    03.02 = "Natural resources management and policy"
    03.03 = "Fishing and fisheries sciences and management"
    03.05 = "Forestry"
    03.06 = "Wildlife and wildlands science and management"
    03.99 = "Natural resources and conservation, other"
    04 = "Architecture and related services"
    04.02 = "Architecture"
    04.03 = "City/urban, community and regional planning"
    04.04 = "Environmental design"
    04.05 = "Interior architecture"
    04.06 = "Landscape architecture"
    04.08 = "Architectural history and criticism"
    04.09 = "Architectural sciences and technology"
    04.10 = "Real estate development"
    04.99 = "Architecture and related services, other"
    05 = "Area, ethnic, cultural, gender, and group studies"
    05.01 = "Area studies"
    05.02 = "Ethnic, cultural minority, gender, and group studies"
    09 = "Communication, journalism, and related programs"
    09.01 = "Communication and media studies"
    09.04 = "Journalism"
    09.07 = "Radio, television, and digital communication"
    09.09 = "Public relations, advertising, and applied communication"
    09.10 = "Publishing"
    09.99 = "Communication, journalism, and related programs, other"
    10 = "Communications technologies/technicians and support services"
    10.01 = "Communications technology/technician"
    10.02 = "Audiovisual communications technologies/technicians"
    10.03 = "Graphic communications"
    10.99 = "Communications technologies/technicians and support services, other"
    11 = "Computer and information sciences and support services"
    11.01 = "Computer and information sciences, general"
    11.02 = "Computer programming"
    11.03 = "Data processing"
    11.04 = "Information science/studies"
    11.05 = "Computer systems analysis"
    11.06 = "Data entry/microcomputer applications"
    11.07 = "Computer science"
    11.08 = "Computer software and media applications"
    11.09 = "Computer systems networking and telecommunications"
    11.10 = "Computer/information technology administration and management"
    11.99 = "Computer and information sciences and support services, other"
    12 = "Personal and culinary services"
    12.03 = "Funeral service and mortuary science"
    12.04 = "Cosmetology and related personal grooming services"
    12.05 = "Culinary arts and related services"
    12.99 = "Personal and culinary services, other"
    13 = "Education"
    13.01 = "Education, general"
    13.02 = "Bilingual, multilingual, and multicultural education"
    13.03 = "Curriculum and instruction"
    13.04 = "Educational administration and supervision"
    13.05 = "Educational/instructional media design"
    13.06 = "Educational assessment, evaluation, and research"
    13.07 = "International and comparative education"
    13.09 = "Social and philosophical foundations of education"
    13.10 = "Special education and teaching"
    13.11 = "Student counseling and personnel services"
    13.12 = "Teacher education and professional development, specific levels and methods"
    13.13 = "Teacher education and professional development, specific subject areas"
    13.14 = "Teaching english or french as a second or foreign language"
    13.15 = "Teaching assistants/aides"
    13.99 = "Education, other"
    14 = "Engineering"
    14.01 = "Engineering, general"
    14.02 = "Aerospace, aeronautical and astronautical engineering"
    14.03 = "Agricultural engineering"
    14.04 = "Architectural engineering"
    14.05 = "Biomedical/medical engineering"
    14.06 = "Ceramic sciences and engineering"
    14.07 = "Chemical engineering"
    14.08 = "Civil engineering"
    14.09 = "Computer engineering"
    14.10 = "Electrical, electronics and communications engineering"
    14.11 = "Engineering mechanics"
    14.12 = "Engineering physics"
    14.13 = "Engineering science"
    14.14 = "Environmental/environmental health engineering"
    14.18 = "Materials engineering"
    14.19 = "Mechanical engineering"
    14.20 = "Metallurgical engineering"
    14.21 = "Mining and mineral engineering"
    14.22 = "Naval architecture and marine engineering"
    14.23 = "Nuclear engineering"
    14.24 = "Ocean engineering"
    14.25 = "Petroleum engineering"
    14.27 = "Systems engineering"
    14.28 = "Textile sciences and engineering"
    14.32 = "Polymer/plastics engineering"
    14.33 = "Construction engineering"
    14.34 = "Forest engineering"
    14.35 = "Industrial engineering"
    14.36 = "Manufacturing engineering"
    14.37 = "Operations research"
    14.38 = "Surveying engineering"
    14.39 = "Geological/geophysical engineering"
    14.40 = "Paper science and engineering"
    14.41 = "Electromechanical engineering"
    14.42 = "Mechatronics, robotics, and automation engineering"
    14.43 = "Biochemical engineering"
    14.44 = "Engineering chemistry"
    14.45 = "Biological/biosystems engineering"
    14.99 = "Engineering, other"
    15 = "Engineering technologies and engineering-related fields"
    15.00 = "Engineering technology, general"
    15.01 = "Architectural engineering technologies/technicians"
    15.02 = "Civil engineering technologies/technicians"
    15.03 = "Electrical engineering technologies/technicians"
    15.04 = "Electromechanical instrumentation and maintenance technologies/technicians"
    15.05 = "Environmental control technologies/technicians"
    15.06 = "Industrial production technologies/technicians"
    15.07 = "Quality control and safety technologies/technicians"
    15.08 = "Mechanical engineering related technologies/technicians"
    15.09 = "Mining and petroleum technologies/technicians"
    15.10 = "Construction engineering technologies"
    15.11 = "Engineering-related technologies"
    15.12 = "Computer engineering technologies/technicians"
    15.13 = "Drafting/design engineering technologies/technicians"
    15.14 = "Nuclear engineering technologies/technicians"
    15.15 = "Engineering-related fields"
    15.16 = "Nanotechnology"
    15.99 = "Engineering technologies/technicians, other"
    16 = "Foreign languages, literatures, and linguistics"
    16.01 = "Linguistic, comparative, and related language studies and services"
    16.02 = "African languages, literatures, and linguistics"
    16.03 = "East asian languages, literatures, and linguistics"
    16.04 = "Slavic, baltic and albanian languages, literatures, and linguistics"
    16.05 = "Germanic languages, literatures, and linguistics"
    16.06 = "Modern greek language and literature"
    16.07 = "South asian languages, literatures, and linguistics"
    16.08 = "Iranian/persian languages, literatures, and linguistics"
    16.09 = "Romance languages, literatures, and linguistics"
    16.10 = "American indian/native american languages, literatures, and linguistics"
    16.11 = "Middle/near eastern and semitic languages, literatures, and linguistics"
    16.12 = "Classics and classical languages, literatures, and linguistics"
    16.13 = "Celtic languages, literatures, and linguistics"
    16.14 = "Southeast asian and australasian/pacific languages, literatures, and linguistics"
    16.15 = "Turkic, uralic-altaic, caucasian, and central asian languages, literatures, and linguistics"
    16.16 = "American sign language"
    16.99 = "Foreign languages, literatures, and linguistics, other"
    19 = "Family and consumer sciences/human sciences"
    19.00 = "Work and family studies"
    19.01 = "Family and consumer sciences/human sciences, general"
    19.02 = "Family and consumer sciences/human sciences business services"
    19.04 = "Family and consumer economics and related studies"
    19.05 = "Foods, nutrition, and related services"
    19.06 = "Housing and human environments"
    19.07 = "Human development, family studies, and related services"
    19.09 = "Apparel and textiles"
    19.99 = "Family and consumer sciences/human sciences, other"
    22 = "Legal professions and studies"
    22.00 = "Non-professional general legal studies (undergraduate)"
    22.01 = "Law"
    22.02 = "Legal research and advanced professional studies"
    22.03 = "Legal support services"
    22.99 = "Legal professions and studies, other"
    23 = "English language and literature/letters"
    23.01 = "English language and literature, general"
    23.13 = "Rhetoric and composition/writing studies"
    23.14 = "Literature"
    23.99 = "English language and literature/letters, other"
    24 = "Liberal arts and sciences, general studies and humanities"
    24.01 = "Liberal arts and sciences, general studies and humanities"
    25 = "Library science"
    25.01 = "Library science and administration"
    25.03 = "Library and archives assisting"
    25.99 = "Library science, other"
    26 = "Biological and biomedical sciences"
    26.01 = "Biology, general"
    26.02 = "Biochemistry, biophysics and molecular biology"
    26.03 = "Botany/plant biology"
    26.04 = "Cell/cellular biology and anatomical sciences"
    26.05 = "Microbiological sciences and immunology"
    26.07 = "Zoology/animal biology"
    26.08 = "Genetics"
    26.09 = "Physiology, pathology and related sciences"
    26.10 = "Pharmacology and toxicology"
    26.11 = "Biomathematics, bioinformatics, and computational biology"
    26.12 = "Biotechnology"
    26.13 = "Ecology, evolution, systematics, and population biology"
    26.14 = "Molecular medicine"
    26.15 = "Neurobiology and neurosciences"
    26.99 = "Biological and biomedical sciences, other"
    27 = "Mathematics and statistics"
    27.01 = "Mathematics"
    27.03 = "Applied mathematics"
    27.05 = "Statistics"
    27.99 = "Mathematics and statistics, other"
    28 = "Military science, leadership and operational art"
    28.01 = "Air force rotc, air science and operations"
    28.03 = "Army rotc, military science and operations"
    28.04 = "Navy/marine rotc, naval science and operations"
    28.05 = "Military science and operational studies"
    28.06 = "Security policy and strategy"
    28.07 = "Military economics and management"
    28.99 = "Military science, leadership and operational art, other"
    29 = "Military technologies and applied sciences"
    29.02 = "Intelligence, command control and information operations"
    29.03 = "Military applied sciences"
    29.04 = "Military systems and maintenance technology"
    29.99 = "Military technologies and applied sciences, other"
    30 = "Multi/interdisciplinary studies"
    30.00 = "Multi-/interdisciplinary studies, general"
    30.01 = "Biological and physical sciences"
    30.05 = "Peace studies and conflict resolution"
    30.06 = "Systems science and theory"
    30.08 = "Mathematics and computer science"
    30.10 = "Biopsychology"
    30.11 = "Gerontology"
    30.12 = "Historic preservation and conservation"
    30.13 = "Medieval and renaissance studies"
    30.14 = "Museology/museum studies"
    30.15 = "Science, technology and society"
    30.16 = "Accounting and computer science"
    30.17 = "Behavioral sciences"
    30.18 = "Natural sciences"
    30.19 = "Nutrition sciences"
    30.20 = "International/global studies"
    30.21 = "Holocaust and related studies"
    30.22 = "Classical and ancient studies"
    30.23 = "Intercultural/multicultural and diversity studies"
    30.25 = "Cognitive science"
    30.26 = "Cultural studies/critical theory and analysis"
    30.27 = "Human biology"
    30.28 = "Dispute resolution"
    30.29 = "Maritime studies"
    30.30 = "Computational science"
    30.31 = "Human computer interaction"
    30.32 = "Marine sciences"
    30.33 = "Sustainability studies"
    30.99 = "Multi/interdisciplinary studies, other"
    31 = "Parks, recreation, leisure, and fitness studies"
    31.01 = "Parks, recreation and leisure studies"
    31.03 = "Parks, recreation and leisure facilities management"
    31.05 = "Health and physical education/fitness"
    31.06 = "Outdoor education"
    31.99 = "Parks, recreation, leisure, and fitness studies, other"
    32 = "Basic skills and developmental/remedial education"
    32.01 = "Basic skills and developmental/remedial education"
    33 = "Citizenship activities"
    33.01 = "Citizenship activities"
    34 = "Health-related knowledge and skills"
    34.01 = "Health-related knowledge and skills"
    35 = "Interpersonal and social skills"
    35.01 = "Interpersonal and social skills"
    36 = "Leisure and recreational activities"
    36.01 = "Leisure and recreational activities"
    37 = "Personal awareness and self-improvement"
    37.01 = "Personal awareness and self-improvement"
    38 = "Philosophy and religious studies"
    38.00 = "Philosophy and religious studies, general"
    38.01 = "Philosophy"
    38.02 = "Religion/religious studies"
    38.99 = "Philosophy and religious studies, other"
    39 = "Theology and religious vocations"
    39.02 = "Bible/biblical studies"
    39.03 = "Missions/missionary studies and missiology"
    39.04 = "Religious education"
    39.05 = "Religious/sacred music"
    39.06 = "Theological and ministerial studies"
    39.07 = "Pastoral counseling and specialized ministries"
    39.99 = "Theology and religious vocations, other"
    40 = "Physical sciences"
    40.01 = "Physical sciences"
    40.02 = "Astronomy and astrophysics"
    40.04 = "Atmospheric sciences and meteorology"
    40.05 = "Chemistry"
    40.06 = "Geological and earth sciences/geosciences"
    40.08 = "Physics"
    40.10 = "Materials sciences"
    40.99 = "Physical sciences, other"
    41 = "Science technologies/technicians"
    41.00 = "Science technologies/technicians, general"
    41.01 = "Biology technician/biotechnology laboratory technician"
    41.02 = "Nuclear and industrial radiologic technologies/technicians"
    41.03 = "Physical science technologies/technicians"
    41.99 = "Science technologies/technicians, other"
    42 = "Psychology"
    42.01 = "Psychology, general"
    42.27 = "Research and experimental psychology"
    42.28 = "Clinical, counseling and applied psychology"
    42.99 = "Psychology, other"
    43 = "Homeland security, law enforcement, firefighting and related protective services"
    43.01 = "Criminal justice and corrections"
    43.02 = "Fire protection"
    43.03 = "Homeland security"
    43.99 = "Homeland security, law enforcement, firefighting and related protective services, other"
    44 = "Public administration and social service professions"
    44.00 = "Human services, general"
    44.02 = "Community organization and advocacy"
    44.04 = "Public administration"
    44.05 = "Public policy analysis"
    44.07 = "Social work"
    44.99 = "Public administration and social service professions, other"
    45 = "Social sciences"
    45.01 = "Social sciences, general"
    45.02 = "Anthropology"
    45.03 = "Archeology"
    45.04 = "Criminology"
    45.05 = "Demography and population studies"
    45.06 = "Economics"
    45.07 = "Geography and cartography"
    45.09 = "International relations and national security studies"
    45.10 = "Political science and government"
    45.11 = "Sociology"
    45.12 = "Urban studies/affairs"
    45.13 = "Sociology and anthropology"
    45.14 = "Rural sociology"
    45.99 = "Social sciences, other"
    46 = "Construction trades"
    46.00 = "Construction trades, general"
    46.01 = "Mason/masonry"
    46.02 = "Carpenters"
    46.03 = "Electrical and power transmission installers"
    46.04 = "Building/construction finishing, management, and inspection"
    46.05 = "Plumbing and related water supply services"
    46.99 = "Construction trades, other"
    47 = "Mechanic and repair technologies/technicians"
    47.00 = "Mechanics and repairers, general"
    47.01 = "Electrical/electronics maintenance and repair technology"
    47.02 = "Heating, air conditioning, ventilation and refrigeration maintenance technology/technician (hac, hacr, hvac, hvacr)"
    47.03 = "Heavy/industrial equipment maintenance technologies"
    47.04 = "Precision systems maintenance and repair technologies"
    47.06 = "Vehicle maintenance and repair technologies"
    47.99 = "Mechanic and repair technologies/technicians, other"
    48 = "Precision production"
    48.00 = "Precision production trades, general"
    48.03 = "Leatherworking and upholstery"
    48.05 = "Precision metal working"
    48.07 = "Woodworking"
    48.08 = "Boilermaking/boilermaker"
    48.99 = "Precision production, other"
    49 = "Transportation and materials moving"
    49.01 = "Air transportation"
    49.02 = "Ground transportation"
    49.03 = "Marine transportation"
    49.99 = "Transportation and materials moving, other"
    50 = "Visual and performing arts"
    50.01 = "Visual and performing arts, general"
    50.02 = "Crafts/craft design, folk art and artisanry"
    50.03 = "Dance"
    50.04 = "Design and applied arts"
    50.05 = "Drama/theatre arts and stagecraft"
    50.06 = "Film/video and photographic arts"
    50.07 = "Fine and studio arts"
    50.09 = "Music"
    50.10 = "Arts, entertainment,and media management"
    50.99 = "Visual and performing arts, other"
    51 = "Health professions and related programs"
    51.00 = "Health services/allied health/health sciences, general"
    51.01 = "Chiropractic"
    51.02 = "Communication disorders sciences and services"
    51.04 = "Dentistry"
    51.05 = "Advanced/graduate dentistry and oral sciences"
    51.06 = "Dental support services and allied professions"
    51.07 = "Health and medical administrative services"
    51.08 = "Allied health and medical assisting services"
    51.09 = "Allied health diagnostic, intervention, and treatment professions"
    51.10 = "Clinical/medical laboratory science/research and allied professions"
    51.11 = "Health/medical preparatory programs"
    51.12 = "Medicine"
    51.14 = "Medical clinical sciences/graduate medical studies"
    51.15 = "Mental and social health services and allied professions"
    51.17 = "Optometry"
    51.18 = "Ophthalmic and optometric support services and allied professions"
    51.19 = "Osteopathic medicine/osteopathy"
    51.20 = "Pharmacy, pharmaceutical sciences, and administration"
    51.21 = "Podiatric medicine/podiatry"
    51.22 = "Public health"
    51.23 = "Rehabilitation and therapeutic professions"
    51.24 = "Veterinary medicine"
    51.25 = "Veterinary biomedical and clinical sciences"
    51.26 = "Health aides/attendants/orderlies"
    51.27 = "Medical illustration and informatics"
    51.31 = "Dietetics and clinical nutrition services"
    51.32 = "Bioethics/medical ethics"
    51.33 = "Alternative and complementary medicine and medical systems"
    51.34 = "Alternative and complementary medical support services"
    51.35 = "Somatic bodywork and related therapeutic services"
    51.36 = "Movement and mind-body therapies and education"
    51.37 = "Energy and biologically based therapies"
    51.38 = "Registered nursing, nursing administration, nursing research and clinical nursing"
    51.39 = "Practical nursing, vocational nursing and nursing assistants"
    51.99 = "Health professions and related clinical sciences, other"
    52 = "Business, management, marketing, and related support services"
    52.01 = "Business/commerce, general"
    52.02 = "Business administration, management and operations"
    52.03 = "Accounting and related services"
    52.04 = "Business operations support and assistant services"
    52.05 = "Business/corporate communications"
    52.06 = "Business/managerial economics"
    52.07 = "Entrepreneurial and small business operations"
    52.08 = "Finance and financial management services"
    52.09 = "Hospitality administration/management"
    52.10 = "Human resources management and services"
    52.11 = "International business"
    52.12 = "Management information systems and services"
    52.13 = "Management sciences and quantitative methods"
    52.14 = "Marketing"
    52.15 = "Real estate"
    52.16 = "Taxation"
    52.17 = "Insurance"
    52.18 = "General sales, merchandising and related marketing operations"
    52.19 = "Specialized sales, merchandising and marketing operations"
    52.20 = "Construction management"
    52.21 = "Telecommunications management"
    52.99 = "Business, management, marketing, and related support services, other"
    53 = "High school/secondary diplomas and certificates"
    53.01 = "High school/secondary diploma programs"
    53.02 = "High school/secondary certificate programs"
    54 = "History"
    54.01 = "History"
    60 = "Residency programs"
    60.01 = "Dental residency programs"
    60.03 = "Veterinary residency programs"
    60.04 = "Medical residency programs - general certificates"
    60.05 = "Medical residency programs - subspecialty certificates"
    60.06 = "Podiatric medicine residency programs"
    99996 = "Valid skip"
    99997 = "Don't know"
    99998 = "Refused"
    99999 = "Not stated or inferred"
  ;
  VALUE $VEMETHOD
    BRR = "Balanced Repeated Replication"
    FAY = "Balanced Repeated Replication w Fay's adjustment"
    JK1 = "Jackknife 1"
    JK2 = "Jackknife 2"
  ;
  VALUE VEMETHODN
    1 = "JK1 - Jackknife 1"
    2 = "JK2 - Jackknife 2"
    3 = "BRR - Balanced Repeated Replication"
    4 = "FAY - Balanced Repeated Replication w Fay's adjustment"
  ;
  VALUE VET
    0 = "False"
    1 = "True"
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE WRITHOMEUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE WRITHOMEUSP_WLE_CA
    0 = "All zero response"
    1 = "Lowest to 20%"
    2 = "More than 20% to 40%"
    3 = "More than 40% to 60%"
    4 = "More than 60% to 80%"
    5 = "More than 80%"
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE WRITWORK_CUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE WRITWORK_CUSP_WLE_CA
    0 = "All zero response"
    1 = "Lowest to 20%"
    2 = "More than 20% to 40%"
    3 = "More than 40% to 60%"
    4 = "More than 60% to 80%"
    5 = "More than 80%"
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE WRITWORK_LUSP
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE WRITWORK_LUSP_WLE_CA
    0 = "All zero response"
    1 = "Lowest to 20%"
    2 = "More than 20% to 40%"
    3 = "More than 40% to 60%"
    4 = "More than 60% to 80%"
    5 = "More than 80%"
    .N = "Not stated or inferred"
    .V = "Valid skip"
  ;
  VALUE WRITWORK_SE_C
    .N = "All zero response"
    .V = "Valid skip"
  ;
  VALUE YEARLYINCPR
    1 = "Less than 10"
    2 = "10 to less than 25"
    3 = "25 to less than 50"
    4 = "50 to less than 75"
    5 = "75 to less than 90"
    6 = "90 or more"
    .N = "Not stated or inferred"
  ;
  VALUE YRSQUAL
    .D = "Don't know"
    .N = "Not stated or inferred"
    .R = "Refused"
    .V = "Valid skip"
  ;
  VALUE ZZ1A
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ2_
    1 = "Never"
    2 = "Almost never"
    3 = "Now and then"
    4 = "Often"
    5 = "Very Often"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ3_
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ4_01_
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ4_05_
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ4_06_
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ5_
    1 = "Yes"
    2 = "No"
    .N = "Not stated or inferred"
  ;
  VALUE ZZ6USP
    1 = "Living/Dining Room (HH only)"
    2 = "Kitchen (HH only)"
    3 = "Bedroom (HH only)"
    4 = "Entrance (HH only)"
    5 = "Hallway or corridor (HH only)"
    6 = "Office (HH & prison)"
    7 = "Other space in the household/facility (HH & prison)"
    8 = "Other space outside of the household (HH only)"
    .N = "Not stated or inferred"
    10 = "Facility Library (Prison only)"
    11 = "Facility Cafeteria (Prison only)"
  ;
RUN ;



DATA DATALIB.&DATAFILE ;
  SET DATALIB.&DATAFILE ;

  FORMAT
    AGE1634 AGE1634_.
    AGE6674 AGE6674_.
    AGEG10LFSEXT AGEG10LFSEXT.
    AGEG5LFSEXT AGEG5LFSEXT.
    BIRTHRGNUS_C BIRTHRGNUS_C.
    BORNLANG BORNLANG.
    B_D01D_C B_D01D_C.
    B_Q01A B_Q01A.
    B_Q01AUS_C B_Q01AUS_C.
    B_Q01A_C B_Q01A_C.
    B_Q01A_ISCED11 B_Q01A_ISCED11F.
    B_Q01B B_Q01B.
    B_Q01C1_C B_Q01C1_C.
    B_Q02A B_Q02A.
    B_Q02BUS_C B_Q02BUS_C.
    B_Q02CUS_C B_Q02CUS_C.
    B_Q03A B_Q03A.
    B_Q03BUS_C B_Q03BUS_C.
    B_Q27AUSP B_Q27AUSP.
    B_Q27BUSP B_Q27BUSP.
    B_Q27CUSP B_Q27CUSP.
    C300C02A C300C02A.
    C300C02F C300C02F.
    C300C02S C300C02S.
    C300C02T C300C02T.
    C301C05A C301C05A.
    C301C05F C301C05F.
    C301C05S C301C05S.
    C301C05T C301C05T.
    C305215A C305215A.
    C305215F C305215F.
    C305215S C305215S.
    C305215T C305215T.
    C305218A C305218A.
    C305218F C305218F.
    C305218S C305218S.
    C305218T C305218T.
    C308116A C308116A.
    C308116F C308116F.
    C308116S C308116S.
    C308116T C308116T.
    C308117A C308117A.
    C308117F C308117F.
    C308117S C308117S.
    C308117T C308117T.
    C308118A C308118A.
    C308118F C308118F.
    C308118S C308118S.
    C308118T C308118T.
    C308119A C308119A.
    C308119F C308119F.
    C308119S C308119S.
    C308119T C308119T.
    C308120A C308120A.
    C308120F C308120F.
    C308120S C308120S.
    C308120T C308120T.
    C308121A C308121A.
    C308121F C308121F.
    C308121S C308121S.
    C308121T C308121T.
    C309319A C309319A.
    C309319F C309319F.
    C309319S C309319S.
    C309319T C309319T.
    C309320A C309320A.
    C309320F C309320F.
    C309320S C309320S.
    C309320T C309320T.
    C309321A C309321A.
    C309321F C309321F.
    C309321S C309321S.
    C309321T C309321T.
    C309322A C309322A.
    C309322F C309322F.
    C309322S C309322S.
    C309322T C309322T.
    C310406A C310406A.
    C310406F C310406F.
    C310406S C310406S.
    C310406T C310406T.
    C310407A C310407A.
    C310407F C310407F.
    C310407S C310407S.
    C310407T C310407T.
    C313410A C313410A.
    C313410F C313410F.
    C313410S C313410S.
    C313410T C313410T.
    C313411A C313411A.
    C313411F C313411F.
    C313411S C313411S.
    C313411T C313411T.
    C313412A C313412A.
    C313412F C313412F.
    C313412S C313412S.
    C313412T C313412T.
    C313413A C313413A.
    C313413F C313413F.
    C313413S C313413S.
    C313413T C313413T.
    C313414A C313414A.
    C313414F C313414F.
    C313414S C313414S.
    C313414T C313414T.
    C600C04A C600C04A.
    C600C04F C600C04F.
    C600C04S C600C04S.
    C600C04T C600C04T.
    C601C06A C601C06A.
    C601C06F C601C06F.
    C601C06S C601C06S.
    C601C06T C601C06T.
    C602501A C602501A.
    C602501F C602501F.
    C602501S C602501S.
    C602501T C602501T.
    C602502A C602502A.
    C602502F C602502F.
    C602502S C602502S.
    C602502T C602502T.
    C602503A C602503A.
    C602503F C602503F.
    C602503S C602503S.
    C602503T C602503T.
    C604505A C604505A.
    C604505F C604505F.
    C604505S C604505S.
    C604505T C604505T.
    C605506A C605506A.
    C605506F C605506F.
    C605506S C605506S.
    C605506T C605506T.
    C605507A C605507A.
    C605507F C605507F.
    C605507S C605507S.
    C605507T C605507T.
    C605508A C605508A.
    C605508F C605508F.
    C605508S C605508S.
    C605508T C605508T.
    C606509A C606509A.
    C606509F C606509F.
    C606509S C606509S.
    C606509T C606509T.
    C607510A C607510A.
    C607510F C607510F.
    C607510S C607510S.
    C607510T C607510T.
    C608513A C608513A.
    C608513F C608513F.
    C608513S C608513S.
    C608513T C608513T.
    C611516A C611516A.
    C611516F C611516F.
    C611516S C611516S.
    C611516T C611516T.
    C611517A C611517A.
    C611517F C611517F.
    C611517S C611517S.
    C611517T C611517T.
    C612518A C612518A.
    C612518F C612518F.
    C612518S C612518S.
    C612518T C612518T.
    C613520A C613520A.
    C613520F C613520F.
    C613520S C613520S.
    C613520T C613520T.
    C614601A C614601A.
    C614601F C614601F.
    C614601S C614601S.
    C614601T C614601T.
    C615602A C615602A.
    C615602F C615602F.
    C615602S C615602S.
    C615602T C615602T.
    C615603A C615603A.
    C615603F C615603F.
    C615603S C615603S.
    C615603T C615603T.
    C617605A C617605A.
    C617605F C617605F.
    C617605S C617605S.
    C617605T C617605T.
    C617606A C617606A.
    C617606F C617606F.
    C617606S C617606S.
    C617606T C617606T.
    C618607A C618607A.
    C618607F C618607F.
    C618607S C618607S.
    C618607T C618607T.
    C618608A C618608A.
    C618608F C618608F.
    C618608S C618608S.
    C618608T C618608T.
    C619609A C619609A.
    C619609F C619609F.
    C619609S C619609S.
    C619609T C619609T.
    C620610A C620610A.
    C620610F C620610F.
    C620610S C620610S.
    C620610T C620610T.
    C620612A C620612A.
    C620612F C620612F.
    C620612S C620612S.
    C620612T C620612T.
    C622615A C622615A.
    C622615F C622615F.
    C622615S C622615S.
    C622615T C622615T.
    C623616A C623616A.
    C623616F C623616F.
    C623616S C623616S.
    C623616T C623616T.
    C623617A C623617A.
    C623617F C623617F.
    C623617S C623617S.
    C623617T C623617T.
    C624619A C624619A.
    C624619F C624619F.
    C624619S C624619S.
    C624619T C624619T.
    C624620A C624620A.
    C624620F C624620F.
    C624620S C624620S.
    C624620T C624620T.
    CBAMOD1STG1 CBAMOD1STG1_.
    CBAMOD1STG2 CBAMOD1STG2_.
    CBAMOD1 CBAMOD1_.
    CBAMOD2ALT CBAMOD2ALT.
    CBAMOD2STG1 CBAMOD2STG1_.
    CBAMOD2STG2 CBAMOD2STG2_.
    CBAMOD2 CBAMOD2_.
    CBA_CORE_STAGE1_SCORE CBA_CORE_STAGE1_SCORE.
    CBA_CORE_STAGE2_SCORE CBA_CORE_STAGE2_SCORE.
    CBA_START CBA_START.
    CILANG CILANG.
    CNTRY $CNTRY.
    CNTRYID CNTRYID.
    CNTRYID_E CNTRYID_E.
    CNTRY_E $CNTRY_E.
    CNT_BRTHUS_C CNT_BRTHUS_C.
    COMPUTEREXPERIENCEUSP COMPUTEREXPERIENCEUSP.
    CORESTAGE1_PASS CORESTAGE1_PASS.
    CORESTAGE2_PASS CORESTAGE2_PASS.
    CTRYRGN CTRYRGN.
    C_Q07USP C_Q07USP.
    C_Q08AUSP C_Q08AUSP.
    C_Q09_C C_Q09_C.
    C_Q10AUSP_C C_Q10AUSP_C.
    D302C02A D302C02A.
    D302C02F D302C02F.
    D302C02S D302C02S.
    D302C02T D302C02T.
    D304710A D304710A.
    D304710F D304710F.
    D304710S D304710S.
    D304710T D304710T.
    D304711A D304711A.
    D304711F D304711F.
    D304711S D304711S.
    D304711T D304711T.
    D306110A D306110A.
    D306110F D306110F.
    D306110S D306110S.
    D306110T D306110T.
    D306111A D306111A.
    D306111F D306111F.
    D306111S D306111S.
    D306111T D306111T.
    D307401A D307401A.
    D307401F D307401F.
    D307401S D307401S.
    D307401T D307401T.
    D307402A D307402A.
    D307402F D307402F.
    D307402S D307402S.
    D307402T D307402T.
    D311701A D311701A.
    D311701F D311701F.
    D311701S D311701S.
    D311701T D311701T.
    D315512A D315512A.
    D315512F D315512F.
    D315512S D315512S.
    D315512T D315512T.
    DISP_BQ DISP_BQ.
    DISP_CIBQ DISP_CIBQ.
    D_Q10USP D_Q10USP_.
    D_Q10USP_C D_Q10USP_C.
    E318001A E318001A.
    E318001F E318001F.
    E318001S E318001S.
    E318001T E318001T.
    E318003A E318003A.
    E318003F E318003F.
    E318003S E318003S.
    E318003T E318003T.
    E320001A E320001A.
    E320001F E320001F.
    E320001S E320001S.
    E320001T E320001T.
    E320003A E320003A.
    E320003F E320003F.
    E320003S E320003S.
    E320003T E320003T.
    E320004A E320004A.
    E320004F E320004F.
    E320004S E320004S.
    E320004T E320004T.
    E321001A E321001A.
    E321001F E321001F.
    E321001S E321001S.
    E321001T E321001T.
    E321002A E321002A.
    E321002F E321002F.
    E321002S E321002S.
    E321002T E321002T.
    E322001A E322001A.
    E322001F E322001F.
    E322001S E322001S.
    E322001T E322001T.
    E322002A E322002A.
    E322002F E322002F.
    E322002S E322002S.
    E322002T E322002T.
    E322003A E322003A.
    E322003F E322003F.
    E322003S E322003S.
    E322003T E322003T.
    E322004A E322004A.
    E322004F E322004F.
    E322004S E322004S.
    E322004T E322004T.
    E322005A E322005A.
    E322005F E322005F.
    E322005S E322005S.
    E322005T E322005T.
    E323002A E323002A.
    E323002F E323002F.
    E323002S E323002S.
    E323002T E323002T.
    E323003A E323003A.
    E323003F E323003F.
    E323003S E323003S.
    E323003T E323003T.
    E323004A E323004A.
    E323004F E323004F.
    E323004S E323004S.
    E323004T E323004T.
    E323005A E323005A.
    E323005F E323005F.
    E323005S E323005S.
    E323005T E323005T.
    E327001A E327001A.
    E327001F E327001F.
    E327001S E327001S.
    E327001T E327001T.
    E327002A E327002A.
    E327002F E327002F.
    E327002S E327002S.
    E327002T E327002T.
    E327003A E327003A.
    E327003F E327003F.
    E327003S E327003S.
    E327003T E327003T.
    E327004A E327004A.
    E327004F E327004F.
    E327004S E327004S.
    E327004T E327004T.
    E329002A E329002A.
    E329002F E329002F.
    E329002S E329002S.
    E329002T E329002T.
    E329003A E329003A.
    E329003F E329003F.
    E329003S E329003S.
    E329003T E329003T.
    E632001A E632001A.
    E632001F E632001F.
    E632001S E632001S.
    E632001T E632001T.
    E632002A E632002A.
    E632002F E632002F.
    E632002S E632002S.
    E632002T E632002T.
    E634001A E634001A.
    E634001F E634001F.
    E634001S E634001S.
    E634001T E634001T.
    E634002A E634002A.
    E634002F E634002F.
    E634002S E634002S.
    E634002T E634002T.
    E635001A E635001A.
    E635001F E635001F.
    E635001S E635001S.
    E635001T E635001T.
    E636001A E636001A.
    E636001F E636001F.
    E636001S E636001S.
    E636001T E636001T.
    E641001A E641001A.
    E641001F E641001F.
    E641001S E641001S.
    E641001T E641001T.
    E644002A E644002A.
    E644002F E644002F.
    E644002S E644002S.
    E644002T E644002T.
    E645001A E645001A.
    E645001F E645001F.
    E645001S E645001S.
    E645001T E645001T.
    E646002A E646002A.
    E646002F E646002F.
    E646002S E646002S.
    E646002T E646002T.
    E650001A E650001A.
    E650001F E650001F.
    E650001S E650001S.
    E650001T E650001T.
    E651002A E651002A.
    E651002F E651002F.
    E651002S E651002S.
    E651002T E651002T.
    E655001A E655001A.
    E655001F E655001F.
    E655001S E655001S.
    E655001T E655001T.
    E657001A E657001A.
    E657001F E657001F.
    E657001S E657001S.
    E657001T E657001T.
    E660003A E660003A.
    E660003F E660003F.
    E660003S E660003S.
    E660003T E660003T.
    E660004A E660004A.
    E660004F E660004F.
    E660004S E660004S.
    E660004T E660004T.
    E661001A E661001A.
    E661001F E661001F.
    E661001S E661001S.
    E661001T E661001T.
    E661002A E661002A.
    E661002F E661002F.
    E661002S E661002S.
    E661002T E661002T.
    E664001A E664001A.
    E664001F E664001F.
    E664001S E664001S.
    E664001T E664001T.
    E665001A E665001A.
    E665001F E665001F.
    E665001S E665001S.
    E665001T E665001T.
    E665002A E665002A.
    E665002F E665002F.
    E665002S E665002S.
    E665002T E665002T.
    EDCAT6 EDCAT6_.
    EDCAT7 EDCAT7_.
    EDCAT8 EDCAT8_.
    EDLEVEL3 EDLEVEL3_.
    E_Q03US_P E_Q03US_P.
    E_Q03USP E_Q03USP_.
    E_Q04USP E_Q04USP_.
    E_Q05A1USP_C E_Q05A1USP_C.
    E_Q05A2USP_C E_Q05A2USP_C.
    E_Q05B1USP_C E_Q05B1USP_C.
    E_Q05B2USP_C E_Q05B2USP_C.
    E_Q06USP E_Q06USP_.
    E_Q08USP_C E_Q08USP_C.
    E_Q09USP E_Q09USP_.
    E_Q09USP_C E_Q09USP_C.
    E_Q10USP E_Q10USP.
    FIRLGRGNUS_C FIRLGRGNUS_C.
    FORBILANG FORBILANG.
    FORBORNLANG FORBORNLANG.
    F_Q01BUSP F_Q01BUSP.
    F_Q02AUSP F_Q02AUSP.
    F_Q02BUSP F_Q02BUSP.
    F_Q02CUSP F_Q02CUSP.
    F_Q02DUSP F_Q02DUSP.
    F_Q02EUSP F_Q02EUSP.
    F_Q03AUSP F_Q03AUSP.
    F_Q03BUSP F_Q03BUSP.
    F_Q03CUSP F_Q03CUSP.
    F_Q04AUSP F_Q04AUSP.
    F_Q04BUSP F_Q04BUSP.
    F_Q05AUSP F_Q05AUSP.
    F_Q05BUSP F_Q05BUSP.
    F_Q06BUSP F_Q06BUSP.
    F_Q06CUSP F_Q06CUSP.
    F_Q07AUSP F_Q07AUSP.
    F_Q07BUSP F_Q07BUSP.
    GENDER_R GENDER_R.
    G_Q01AUSP G_Q01AUSP.
    G_Q01BUSP G_Q01BUSP.
    G_Q01CUSP G_Q01CUSP.
    G_Q01DUSP G_Q01DUSP.
    G_Q01EUSP G_Q01EUSP.
    G_Q01FUSP G_Q01FUSP.
    G_Q01GUSP G_Q01GUSP.
    G_Q01HUSP G_Q01HUSP.
    G_Q02AUSP G_Q02AUSP.
    G_Q02BUSP G_Q02BUSP.
    G_Q02CUSP G_Q02CUSP.
    G_Q02DUSP G_Q02DUSP.
    G_Q03BUSP G_Q03BUSP.
    G_Q03CUSP G_Q03CUSP.
    G_Q03DUSP G_Q03DUSP.
    G_Q03FUSP G_Q03FUSP.
    G_Q03GUSP G_Q03GUSP.
    G_Q03HUSP G_Q03HUSP.
    G_Q04USP G_Q04USP.
    G_Q05AUSP G_Q05AUSP.
    G_Q05CUSP G_Q05CUSP.
    G_Q05DUSP G_Q05DUSP.
    G_Q05EUSP G_Q05EUSP.
    G_Q05FUSP G_Q05FUSP.
    G_Q05GUSP G_Q05GUSP.
    G_Q05HUSP G_Q05HUSP.
    G_Q06USP G_Q06USP.
    G_Q07USP G_Q07USP.
    G_Q08USP G_Q08USP.
    HOMLANG HOMLANG.
    HOMLGRGNUS_C HOMLGRGNUS_C.
    H_Q01AUSP H_Q01AUSP.
    H_Q01BUSP H_Q01BUSP.
    H_Q01CUSP H_Q01CUSP.
    H_Q01DUSP H_Q01DUSP.
    H_Q01EUSP H_Q01EUSP.
    H_Q01FUSP H_Q01FUSP.
    H_Q01GUSP H_Q01GUSP.
    H_Q01HUSP H_Q01HUSP.
    H_Q02AUSP H_Q02AUSP.
    H_Q02BUSP H_Q02BUSP.
    H_Q02CUSP H_Q02CUSP.
    H_Q02DUSP H_Q02DUSP.
    H_Q03BUSP H_Q03BUSP.
    H_Q03CUSP H_Q03CUSP.
    H_Q03DUSP H_Q03DUSP.
    H_Q03FUSP H_Q03FUSP.
    H_Q03GUSP H_Q03GUSP.
    H_Q03HUSP H_Q03HUSP.
    H_Q04AUSP H_Q04AUSP.
    H_Q04BUSP H_Q04BUSP.
    H_Q05EUSP H_Q05EUSP.
    H_Q05FUSP H_Q05FUSP.
    H_Q05GUSP H_Q05GUSP.
    ICTWORK_LUSP ICTWORK_LUSP.
    IMGEN IMGEN.
    IMPAR IMPAR.
    IMYRCAT IMYRCAT.
    IMYRS_C IMYRS_C.
    INFLUENCE_LUSP INFLUENCE_LUSP.
    INPIAAC INPIAAC.
    INTLFLAG INTLFLAG.
    ISCO08_CUSP_C $ISCO08_CUSP_C.
    ISCO08_LUSP_C $ISCO08_LUSP_C.
    ISIC4_LUSP_C $ISIC4_LUSP_C.
    I_Q04B I_Q04B.
    I_Q04D I_Q04D.
    I_Q04H I_Q04H.
    I_Q04J I_Q04J.
    I_Q04L I_Q04L.
    I_Q04M I_Q04M.
    I_Q06A I_Q06A.
    I_Q06DUSP1G I_Q06DUSP1G.
    I_Q06DUSX1A I_Q06DUSX1A.
    I_Q06DUSX1B I_Q06DUSX1B.
    I_Q06DUSX1D I_Q06DUSX1D.
    I_Q06DUSX1E I_Q06DUSX1E.
    I_Q06DUSX1F I_Q06DUSX1F.
    I_Q07A I_Q07A.
    I_Q07B I_Q07B.
    I_Q08USX1 I_Q08USX1_.
    I_Q08USX2 I_Q08USX2_.
    I_Q08USX3 I_Q08USX3_.
    I_Q08 I_Q08_.
    I_Q10BUSP2G I_Q10BUSP2G.
    I_Q10BUSX2A I_Q10BUSX2A.
    I_Q10BUSX2B I_Q10BUSX2B.
    I_Q10BUSX2D I_Q10BUSX2D.
    I_Q10BUSX2E I_Q10BUSX2E.
    I_Q10BUSX2F I_Q10BUSX2F.
    I_Q10BUSX2H I_Q10BUSX2H.
    J_N05A2 J_N05A2_.
    P_Q440 P_Q440_.
    J_Q02C J_Q02C.
    J_Q03A J_Q03A.
    J_Q03B_C J_Q03B_C.
    J_Q03CUS_C J_Q03CUS_C.
    J_Q03C_C J_Q03C_C.
    J_Q03D1US_C J_Q03D1US_C.
    J_Q03D1_C J_Q03D1_C.
    J_Q03D2US_C J_Q03D2US_C.
    J_Q03D2_C J_Q03D2_C.
    J_Q04A J_Q04A.
    J_Q04C1_C J_Q04C1_C.
    J_Q04C2US_C J_Q04C2US_C.
    J_Q04DUSX1A J_Q04DUSX1A.
    J_Q05A2USX2 J_Q05A2USX2_.
    J_Q05CUSP4 J_Q05CUSP4_.
    J_Q05CUSX2 J_Q05CUSX2_.
    J_Q05CUSX3A J_Q05CUSX3A.
    J_Q05CUSX3B J_Q05CUSX3B.
    J_Q05CUSX3D J_Q05CUSX3D.
    J_Q05CUSX3E J_Q05CUSX3E.
    J_Q05CUSX6 J_Q05CUSX6_.
    J_Q06A J_Q06A.
    J_Q06B J_Q06B.
    J_Q06BUS J_Q06BUS.
    J_Q06B_ISCED11 J_Q06B_ISCED11F.
    J_Q07A J_Q07A.
    J_Q07B J_Q07B.
    J_Q07BUS J_Q07BUS.
    J_Q07B_ISCED11 J_Q07B_ISCED11F.
    J_Q08 J_Q08_.
    LANGUAGE LANGUAGE.
    LEAVER1624 LEAVER1624_.
    LITSTATUS LITSTATUS.
    LNG_BQ $LNG_BQ.
    LNG_CI $LNG_CI.
    LNG_HOMEUS_C LNG_HOMEUS_C.
    LNG_L1US_C LNG_L1US_C.
    LNG_L2US_C LNG_L2US_C.
    M300C02S M300C02S.
    M301C05S M301C05S.
    M305215S M305215S.
    M305218S M305218S.
    M309319S M309319S.
    M309320S M309320S.
    M309321S M309321S.
    M309322S M309322S.
    M310406S M310406S.
    M310407S M310407S.
    M313410S M313410S.
    M313411S M313411S.
    M313412S M313412S.
    M313413S M313413S.
    M313414S M313414S.
    M600C04S M600C04S.
    M602501S M602501S.
    M602502S M602502S.
    M602503S M602503S.
    M604505S M604505S.
    M610515S M610515S.
    M615602S M615602S.
    M615603S M615603S.
    M618607S M618607S.
    M618608S M618608S.
    M620610S M620610S.
    M620612S M620612S.
    M623616S M623616S.
    M623617S M623617S.
    M623618S M623618S.
    M624619S M624619S.
    M624620S M624620S.
    N302C02S N302C02S.
    N306110S N306110S.
    N306111S N306111S.
    NATBILANG NATBILANG.
    NATIVELANG NATIVELANG.
    NATIVESPEAKER NATIVESPEAKER.
    NUMHOMEUSP NUMHOMEUSP.
    NUMSTATUS NUMSTATUS.
    NUMWORK_LUSP NUMWORK_LUSP.
    NUMWORK_CUSP NUMWORK_CUSP.
    NUMWORK_CUSP_WLE_CA NUMWORK_CUSP_WLE_CA.
    P317001S P317001S.
    P317002S P317002S.
    P317003S P317003S.
    P324002S P324002S.
    P324003S P324003S.
    P330001S P330001S.
    P601C06S P601C06S.
    P614601S P614601S.
    P640001S P640001S.
    P645001S P645001S.
    P655001S P655001S.
    P664001S P664001S.
    P666001S P666001S.
    P901002R P901002R.
    P901002S P901002S.
    P901003R P901003R.
    P901003S P901003S.
    P901004R P901004R.
    P901004S P901004S.
    P901005R P901005R.
    P901005S P901005S.
    P901006R P901006R.
    P901006S P901006S.
    P901011R P901011R.
    P901011S P901011S.
    P901013R P901013R.
    P901013S P901013S.
    P901015R P901015R.
    P901015S P901015S.
    P901017R P901017R.
    P901017S P901017S.
    P901018R P901018R.
    P901018S P901018S.
    P901019R P901019R.
    P901019S P901019S.
    P901020R P901020R.
    P901020S P901020S.
    P901021R P901021R.
    P901021S P901021S.
    P901024R P901024R.
    P901024S P901024S.
    P901025R P901025R.
    P901025S P901025S.
    P902014R P902014R.
    P902014S P902014S.
    P902021R P902021R.
    P902021S P902021S.
    P902022R P902022R.
    P902022S P902022S.
    P902024R P902024R.
    P902024S P902024S.
    P903007R P903007R.
    P903007S P903007S.
    P903012R P903012R.
    P903012S P903012S.
    P903017R P903017R.
    P903017S P903017S.
    P903021R P903021R.
    P903021S P903021S.
    P903024R P903024R.
    P903024S P903024S.
    P904009R P904009R.
    P904009S P904009S.
    P904010R P904010R.
    P904010S P904010S.
    P904012R P904012R.
    P904012S P904012S.
    P904014R P904014R.
    P904014S P904014S.
    P904015R P904015R.
    P904015S P904015S.
    P904020R P904020R.
    P904020S P904020S.
    P904021R P904021R.
    P904021S P904021S.
    P904022R P904022R.
    P904022S P904022S.
    P904024R P904024R.
    P904024S P904024S.
    P904025R P904025R.
    P904025S P904025S.
    P911001R P911001R.
    P911001S P911001S.
    P911003R P911003R.
    P911003S P911003S.
    P911004R P911004R.
    P911004S P911004S.
    P911005R P911005R.
    P911005S P911005S.
    P911006R P911006R.
    P911006S P911006S.
    P911007R P911007R.
    P911007S P911007S.
    P911008R P911008R.
    P911008S P911008S.
    P911009R P911009R.
    P911009S P911009S.
    P911010R P911010R.
    P911010S P911010S.
    P911014R P911014R.
    P911014S P911014S.
    P911017R P911017R.
    P911017S P911017S.
    P911020R P911020R.
    P911020S P911020S.
    P912002R P912002R.
    P912002S P912002S.
    P912011R P912011R.
    P912011S P912011S.
    P912013R P912013R.
    P912013S P912013S.
    P912019R P912019R.
    P912019S P912019S.
    P913013R P913013R.
    P913013S P913013S.
    P914012R P914012R.
    P914012S P914012S.
    P914015R P914015R.
    P914015S P914015S.
    P914016R P914016R.
    P914016S P914016S.
    P914018R P914018R.
    P914018S P914018S.
    P914019R P914019R.
    P914019S P914019S.
    P921002R P921002R.
    P921002S P921002S.
    P921003R P921003R.
    P921003S P921003S.
    P921004R P921004R.
    P921004S P921004S.
    P921005R P921005R.
    P921005S P921005S.
    P921007R P921007R.
    P921007S P921007S.
    P921008R P921008R.
    P921008S P921008S.
    P921009R P921009R.
    P921009S P921009S.
    P921010R P921010R.
    P921010S P921010S.
    P921011R P921011R.
    P921011S P921011S.
    P921013R P921013R.
    P921013S P921013S.
    P921014R P921014R.
    P921014S P921014S.
    P921015R P921015R.
    P921015S P921015S.
    P921016R P921016R.
    P921016S P921016S.
    P921017R P921017R.
    P921017S P921017S.
    P921018R P921018R.
    P921018S P921018S.
    P921019R P921019R.
    P921019S P921019S.
    P921020R P921020R.
    P921020S P921020S.
    P921021R P921021R.
    P921021S P921021S.
    P921035R P921035R.
    P921035S P921035S.
    P921036R P921036R.
    P921036S P921036S.
    P921037R P921037R.
    P921037S P921037S.
    P921038R P921038R.
    P921038S P921038S.
    P921040R P921040R.
    P921040S P921040S.
    P921041R P921041R.
    P921041S P921041S.
    P921042R P921042R.
    P921042S P921042S.
    P921043R P921043R.
    P921043S P921043S.
    P922023R P922023R.
    P922023S P922023S.
    P922024R P922024R.
    P922024S P922024S.
    P922025R P922025R.
    P922025S P922025S.
    P922026R P922026R.
    P922026S P922026S.
    P922027R P922027R.
    P922027S P922027S.
    P922028R P922028R.
    P922028S P922028S.
    P922030R P922030R.
    P922030S P922030S.
    P922031R P922031R.
    P922031S P922031S.
    P922032R P922032R.
    P922032S P922032S.
    P922033R P922033R.
    P922033S P922033S.
    P924035R P924035R.
    P924035S P924035S.
    P924036R P924036R.
    P924036S P924036S.
    P924037R P924037R.
    P924037S P924037S.
    P924038R P924038R.
    P924038S P924038S.
    P924040R P924040R.
    P924040S P924040S.
    P924041R P924041R.
    P924041S P924041S.
    P924042R P924042R.
    P924042S P924042S.
    P924043R P924043R.
    P924043S P924043S.
    PAPER PAPER.
    PARED PARED.
    PBROUTE PBROUTE.
    PLANNING_LUSP PLANNING_LUSP.
    PPC_SCORE PPC_SCORE.
    PRC_PC_SCR PRC_PC_SCR.
    PRC_PF_Q1 PRC_PF_Q1_.
    PRC_PF_Q2 PRC_PF_Q2_.
    PRC_PF_Q3 PRC_PF_Q3_.
    PRC_PV_Q1 PRC_PV_Q1_.
    PRC_PV_SCR PRC_PV_SCR.
    PRC_SP_Q1 PRC_SP_Q1_.
    PRC_SP_SCR PRC_SP_SCR.
    PSLSTATUS PSLSTATUS.
    P_G_Q01A P_G_Q01A.
    P_G_Q01B P_G_Q01B.
    P_G_Q01C P_G_Q01C.
    P_G_Q01D P_G_Q01D.
    P_G_Q01E P_G_Q01E.
    P_G_Q01F P_G_Q01F.
    P_G_Q01G P_G_Q01G.
    P_G_Q01H P_G_Q01H.
    P_G_Q02A P_G_Q02A.
    P_G_Q02B P_G_Q02B.
    P_G_Q02C P_G_Q02C.
    P_G_Q02D P_G_Q02D.
    P_G_Q03B P_G_Q03B.
    P_G_Q03C P_G_Q03C.
    P_G_Q03D P_G_Q03D.
    P_G_Q03F P_G_Q03F.
    P_G_Q03G P_G_Q03G.
    P_G_Q03H P_G_Q03H.
    P_G_Q04 P_G_Q04_.
    P_G_Q05E P_G_Q05E.
    P_G_Q05F P_G_Q05F.
    P_G_Q05G P_G_Q05G.
    P_G_Q06 P_G_Q06_.
    P_G_Q07 P_G_Q07_.
    P_G_Q08 P_G_Q08_.
    P_Q010A P_Q010A.
    P_Q010B P_Q010B.
    P_Q020 P_Q020_.
    P_Q030 P_Q030_.
    P_Q040 P_Q040_.
    P_Q050 P_Q050_.
    P_Q060 P_Q060_.
    P_Q070 P_Q070_.
    P_Q080 P_Q080_.
    P_Q080_ISCED11 P_Q080_ISCED11F.
    P_Q090 P_Q090_.
    P_Q100 P_Q100_.
    P_Q120 P_Q120_.
    P_Q120_ISCED11 P_Q120_ISCED11F.
    P_Q130 P_Q130_.
    P_Q140A P_Q140A.
    P_Q140B P_Q140B.
    P_Q150 P_Q150_.
    P_Q160_1 P_Q160_1_.
    P_Q160_2 P_Q160_2_.
    P_Q170 P_Q170_.
    P_Q180 P_Q180_.
    P_Q190A P_Q190A.
    P_Q190A_1 P_Q190A_1_.
    P_Q190A_2 P_Q190A_2_.
    P_Q190B P_Q190B.
    P_Q190B_1 P_Q190B_1_.
    P_Q190B_2 P_Q190B_2_.
    P_Q190C P_Q190C.
    P_Q190C_1 P_Q190C_1_.
    P_Q190C_2 P_Q190C_2_.
    P_Q190D P_Q190D.
    P_Q190D_1 P_Q190D_1_.
    P_Q190D_2 P_Q190D_2_.
    P_Q190E P_Q190E.
    P_Q190E_1 P_Q190E_1_.
    P_Q190E_2 P_Q190E_2_.
    P_Q190F P_Q190F.
    P_Q190F_1 P_Q190F_1_.
    P_Q190F_2 P_Q190F_2_.
    P_Q190G P_Q190G.
    P_Q190G_1 P_Q190G_1_.
    P_Q190G_2 P_Q190G_2_.
    P_Q190H P_Q190H.
    P_Q190H_1 P_Q190H_1_.
    P_Q190H_2 P_Q190H_2_.
    P_Q190I P_Q190I.
    P_Q190I_1 P_Q190I_1_.
    P_Q190I_2 P_Q190I_2_.
    P_Q190J P_Q190J.
    P_Q220 P_Q220_.
    P_Q230 P_Q230_.
    P_Q240_01 P_Q240_01_.
    P_Q240_02 P_Q240_02_.
    P_Q240_03 P_Q240_03_.
    P_Q240_04 P_Q240_04_.
    P_Q240_05 P_Q240_05_.
    P_Q240_06 P_Q240_06_.
    P_Q250 P_Q250_.
    P_Q260 P_Q260_.
    P_Q270 P_Q270_.
    P_Q280 P_Q280_.
    P_Q290 P_Q290_.
    P_Q300 P_Q300_.
    P_Q310 P_Q310_.
    P_Q320 P_Q320_.
    P_Q330 P_Q330_.
    P_Q340 P_Q340_.
    P_Q350A P_Q350A.
    P_Q350B P_Q350B.
    P_Q360 P_Q360_.
    P_Q370 P_Q370_.
    P_Q380 P_Q380_.
    P_Q390 P_Q390_.
    P_Q400 P_Q400_.
    P_Q410 P_Q410_.
    P_Q420 P_Q420_.
    P_Q430_01 P_Q430_01_.
    P_Q430_02 P_Q430_02_.
    P_Q430_03 P_Q430_03_.
    P_Q430_04 P_Q430_04_.
    P_Q430_05 P_Q430_05_.
    P_Q430_06 P_Q430_06_.
    P_Q430_07 P_Q430_07_.
    P_Q430_08 P_Q430_08_.
    RACETHN_4CAT RACETHN_4CAT.
    READHOMEUSP READHOMEUSP.
    READWORK_LUSP READWORK_LUSP.
    READWORK_CUSP READWORK_CUSP.
    READWORK_CUSP_WLE_CA READWORK_CUSP_WLE_CA.
    READYTOLEARN READYTOLEARN.
    REGION_US REGION_US.
    REG_TL2 $REG_TL.
    SAMPFLAG SAMPFLAG.
    SECLGRGNUS_C SECLGRGNUS_C.
    U01A000A U01A000A.
    U01A000F U01A000F.
    U01A000S U01A000S.
    U01A000T U01A000T.
    U01B000A U01B000A.
    U01B000F U01B000F.
    U01B000S U01B000S.
    U01B000T U01B000T.
    U02X000A U02X000A.
    U02X000F U02X000F.
    U02X000S U02X000S.
    U02X000T U02X000T.
    U03A000A U03A000A.
    U03A000F U03A000F.
    U03A000S U03A000S.
    U03A000T U03A000T.
    U04A000A U04A000A.
    U04A000F U04A000F.
    U04A000S U04A000S.
    U04A000T U04A000T.
    U06A000A U06A000A.
    U06A000F U06A000F.
    U06A000S U06A000S.
    U06A000T U06A000T.
    U06B000A U06B000A.
    U06B000F U06B000F.
    U06B000S U06B000S.
    U06B000T U06B000T.
    U07X000A U07X000A.
    U07X000F U07X000F.
    U07X000S U07X000S.
    U07X000T U07X000T.
    U11B000A U11B000A.
    U11B000F U11B000F.
    U11B000S U11B000S.
    U11B000T U11B000T.
    U16X000A U16X000A.
    U16X000F U16X000F.
    U16X000S U16X000S.
    U16X000T U16X000T.
    U19A000A U19A000A.
    U19A000F U19A000F.
    U19A000S U19A000S.
    U19A000T U19A000T.
    U19B000A U19B000A.
    U19B000F U19B000F.
    U19B000S U19B000S.
    U19B000T U19B000T.
    U21X000A U21X000A.
    U21X000F U21X000F.
    U21X000S U21X000S.
    U21X000T U21X000T.
    U23X000A U23X000A.
    U23X000F U23X000F.
    U23X000S U23X000S.
    U23X000T U23X000T.
    USCIP_C_C $USCIP_C_C.
    USCIP_H_C $USCIP_H_C.
    VEMETHOD $VEMETHOD.
    VEMETHODN VEMETHODN.
    VET VET.
    WRITHOMEUSP WRITHOMEUSP.
    WRITHOMEUSP_WLE_CA WRITHOMEUSP_WLE_CA.
    WRITWORK_LUSP WRITWORK_LUSP.
    WRITWORK_CUSP WRITWORK_CUSP.
    ICTWORK_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    INFLUENCE_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    NUMHOMEUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    NUMWORK_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    PLANNING_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    READHOMEUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    READWORK_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    READYTOLEARN_WLE_CA WRITWORK_LUSP_WLE_CA.
    WRITWORK_LUSP_WLE_CA WRITWORK_LUSP_WLE_CA.
    WRITWORK_CUSP_WLE_CA WRITWORK_CUSP_WLE_CA.
    YRSQUAL YRSQUAL.
    ZZ1A ZZ1A.
    ZZ2 ZZ2_.
    ZZ3 ZZ3_.
    ZZ4_01 ZZ4_01_.
    ZZ4_05 ZZ4_05_.
    ZZ4_06 ZZ4_06_.
    ZZ5 ZZ5_.
    ZZ6USP ZZ6USP.
  ;
RUN ;
