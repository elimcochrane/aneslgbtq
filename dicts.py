var_dict = {     
    # information
    'V240001': 'case_id',
    'V240002a': 'int_mode',
    'V240002c': 'prepost_status',
    'V240003': 'sample_type',

     # trans questions
    'V241552': 'trans_id',
    'V242510': 'trans_contact',
    'V242151': 'trans_therm',
    'V242364x': 'trans_military',
    'V241372x': 'trans_bathroom',
    'V241375x': 'trans_sports_pre',
    'V242457': 'trans_sports_post',
    'V242458x': 'trans_sports_prepost',
    'V242558': 'trans_discrim',
        
    # gay questions
    'V241553': 'gay_id',
    'V242508': 'gay_contact',
    'V242144': 'gay_therm',
    'V241381x': 'gay_adoption',
    'V241385x': 'gay_marriage',
    'V242211': 'gay_elect',        
    'V241378x': 'gay_discrim',
        
    # demographics
    'V241227x': 'resp_partyid',
    'V241501x': 'resp_race',
    'V241458x': 'resp_age',
    'V241463': 'resp_edu'
    }

ans_dict = {
    # trans questions
    'trans_id': {
        -9: 'Refused', -1: 'Inapplicable', 1: 'Yes', 2: 'No'
    },
    'trans_contact': {
        -9: 'Refused', -7: 'Insufficient partial', -6: 'No post interview', -5: 'Sufficient partial', -1: 'Inapplicable', 
        1: 'Yes', 2: 'No'
    },
    'trans_therm': {
        -9: 'Refused', -7: 'Insufficient partial', -6: 'No post interview', -5: 'Sufficient partial', -1: 'Inapplicable', 
        998: "Don't know rating", 999: "Don't recognize"
    },
    'trans_military': {
        -7: 'Insufficient partial', -6: 'No post interview', -5: 'Sufficient partial',
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'trans_bathroom': {
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'trans_sports_pre': {
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'trans_sports_post': {
        -7: 'Insufficient partial', -6: 'No post interview', -5: 'Sufficient partial',
        -1: 'Inapplicable',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'trans_sports_prepost': {
        -7: 'Insufficient partial', -6: 'No post interview', -5: 'Sufficient partial',
        -2: 'DK/RF',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'trans_discrim': {
        -9: 'Refused', -7: 'Insufficient partial', -6: 'No post interview',
        -5: 'Sufficient partial', -1: 'Inapplicable',
        1: 'A great deal', 2: 'A lot', 3: 'A moderate amount', 4: 'A little', 5: 'None at all'
    },

    # gay questions
    'gay_id': {
        -9: 'Refused', -5: 'Break off', -1: 'Inapplicable',
        1: 'Heterosexual', 2: 'Homosexual', 3: 'Bisexual', 4: 'Something else'
    },
    'gay_contact': {
        -9: 'Refused', -7: 'Insufficient partial', -6: 'No post interview',
        -5: 'Sufficient partial', -1: 'Inapplicable', 
        1: 'Yes', 2: 'No'
    },
    'gay_therm': {
        -9: 'Refused', -7: 'Insufficient partial', -6: 'No post interview',
        -5: 'Sufficient partial', -1: 'Inapplicable', 998: "Don't know rating",
        999: "Don't recognize"
    },
    'gay_adoption': {
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Strongly permit', 2: 'Somewhat strongly permit', 3: 'Not strongly permit',
        4: 'Not strongly not permit', 5: 'Somewhat strongly not permit', 6: 'Strongly oppose'
    },
    'gay_marriage': {
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Greatly favor', 2: 'Favor moderately', 3: 'Favor a little',
        4: 'Neither favor nor oppose', 5: 'Oppose a little', 6: 'Oppose moderately',
        7: 'Greatly oppose'
    },
    'gay_elect': {
        -9: 'Refused', -8: "Don't know", -7: 'Insufficient partial', -6: 'No post interview',
        -5: 'Sufficient partial', -1: 'Inapplicable',
        1: 'Extremely important', 2: 'Very important', 3: 'Moderately important',
        4: 'A little important', 5: 'Not important'
    },
    'gay_discrim': {
        -2: 'DK/RF', -1: 'Inapplicable',
        1: 'Strongly favor', 2: 'Favor not strongly', 3: 'Oppose not strongly', 4: 'Strongly oppose'
    },

    # demographics
    'resp_partyid': {
        -9: 'Refused', -8: "Don't know", -4: 'Error',
        1: 'Strong Democrat', 2: 'Not very strong Democrat', 3: 'Independent-Democrat',
        4: 'Independent', 5: 'Independent-Republican', 6: 'Not very strong Republican',
        7: 'Strong Republican'
    },
    'resp_race': {
        -9: 'Refused', -8: "Don't know", -4: 'Error',
        1: 'White, non-Hispanic', 2: 'Black, non-Hispanic', 3: 'Hispanic',
        4: 'Asian/Pacific Islander, non-Hispanic', 5: 'Native American/other, non-Hispanic',
        6: 'Multiple races, non-Hispanic'
    },
    'resp_age': {
        -2: 'Missing birth date', 80: '80 years or older'
    },
    'resp_edu': {
        -9: 'Refused', -8: "Don't know", -1: 'Inapplicable',
        1: 'Less than 1st grade', 2: '1st-4th grade', 3: '5th-6th grade', 4: '7th-8th grade',
        5: '9th grade', 6: '10th grade', 7: '11th grade', 8: '12th grade no diploma',
        9: 'High school graduate', 10: 'Some college', 11: 'Associate (vocational)',
        12: 'Associate (academic)', 13: "Bachelor's degree", 14: "Master's degree",
        15: 'Professional degree', 16: 'Doctorate degree', 95: 'Other'
    },
}

theme_dict = {
    'trans_qs': {
        'trans_id', 'trans_contact', 'trans_therm', 'trans_military', 'trans_bathroom',
        'trans_sports_pre', 'trans_sports_post', 'trans_sports_prepost', 'trans_discrim'},
    'gay_qs': {
        'gay_id', 'gay_contact', 'gay_therm', 'gay_adoption', 'gay_marriage', 'gay_elect', 'gay_discrim',
    }
}