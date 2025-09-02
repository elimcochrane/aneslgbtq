"""
dictionary of anes weight variables
prefers post-election weights when both pre- and post- exist
"""

weights_dict = {
    "ftf": {
        "weight": "V240101b",
        "psu": "V240101c",
        "stratum": "V240101d"
    },
    "web": {
        "weight": "V240102b",
        "psu": "V240102c",
        "stratum": "V240102d"
    },
    "ftf_web": {
        "weight": "V240103b",
        "psu": "V240103c",
        "stratum": "V240103d"
    },
    "web_papi": {
        "weight": "V240104b",
        "psu": "V240104c",
        "stratum": "V240104d"
    },
    "ftf_web_papi": {
        "weight": "V240105b",
        "psu": "V240105c",
        "stratum": "V240105d"
    },
    "panel": {
        "weight": "V240106b",
        "psu": "V240106c",
        "stratum": "V240106d"
    },
    "panel_ftf_web_papi": {
        "weight": "V240107b",
        "psu": "V240107c",
        "stratum": "V240107d"
    },
    "ftf_web_panel": {
        "weight": "V240108b",
        "psu": "V240108c",
        "stratum": "V240108d"
    }
}