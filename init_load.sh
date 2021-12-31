#!/bin/bash

LOG=./init_load.log

notes() {
    cat <<EOF
#
head  ./VIX.csv
Date,High,Low,Open,Close,Volume,Adj Close
2014-12-04,30096.900390625,27953.0,28200.400390625,28447.69921875,811330.0,28447.69921875
2014-12-05,27540.69921875,25974.0,26551.19921875,26056.5,377529.0,26056.5
2014-12-08,26056.5,23582.80078125,25231.900390625,23582.80078125,367585.0,23582.80078125

head -4 ./SPY.csv
Date,High,Low,Open,Close,Volume,Adj Close
1993-01-29,43.96875,43.75,43.96875,43.9375,1003200.0,25.62718963623047
1993-02-01,44.25,43.96875,43.96875,44.25,480500.0,25.809457778930664
1993-02-02,44.375,44.125,44.21875,44.34375,201300.0,25.8641300201416

head -4 ./FED_Soma.csv
"""As Of Date""","""CUSIP""","""Security Type""","""Security Description""","""Term""","""Maturity Date""","""Issuer""","""Spread (%)""","""Coupon (%)""","""Current Face Value""","""Par Value""","""Inflation Compensation""","""Percent Outstanding""","""Change From Prior Week""","""Change From Prior Year""","""is Aggregated"""
"""2021-12-22""","""'912796J75'""","""Bills""",,,"""2021-12-23""",,,,,"""3940710400""",,"""0.0296421052631579""","""0""",,
"""2021-12-22""","""'912796P86'""","""Bills""",,,"""2021-12-28""",,,,,"""3933790000""",,"""0.0570685177931555""","""0""",,
"""2021-12-22""","""'912796A90'""","""Bills""",,,"""2021-12-30""",,,,,"""20463170400""",,"""0.1359995374339547""","""0""",,
EOF
}

load_data() {
    # These have data
    ./pyalgofetcher.py -f FED_Soma -s 2020-01-01 -e 2021-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2019-01-01 -e 2020-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2018-01-01 -e 2019-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2017-01-01 -e 2018-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2016-01-01 -e 2017-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2015-01-01 -e 2016-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2014-01-01 -e 2015-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2013-01-01 -e 2014-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2012-01-01 -e 2013-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2011-01-01 -e 2012-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2010-01-01 -e 2011-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2009-01-01 -e 2010-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2008-01-01 -e 2009-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2007-01-01 -e 2008-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2006-01-01 -e 2007-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2005-01-01 -e 2006-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2004-01-01 -e 2005-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2003-01-01 -e 2004-01-01
    # The older files have no data
    ./pyalgofetcher.py -f FED_Soma -s 2002-01-01 -e 2003-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2001-01-01 -e 2002-01-01
    ./pyalgofetcher.py -f FED_Soma -s 2000-01-01 -e 2001-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1999-01-01 -e 2000-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1998-01-01 -e 1999-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1997-01-01 -e 1998-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1996-01-01 -e 1997-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1995-01-01 -e 1996-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1994-01-01 -e 1995-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1993-01-01 -e 1994-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1992-01-01 -e 1993-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1991-01-01 -e 1992-01-01
    ./pyalgofetcher.py -f FED_Soma -s 1990-01-01 -e 1991-01-01

    ./pyalgofetcher.py -f SPY -s 1990-01-01 -e 2020-01-31
    ./pyalgofetcher.py -f SPY -s 2021-01-01 -e 2021-11-30

    ./pyalgofetcher.py -f VIX -s 1990-01-01 -e 2020-01-31
}

load_data
