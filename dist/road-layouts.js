// Derived OpenStreetMap geometry © OpenStreetMap contributors, ODbL. Retrieved 2026-10-26.
// Study selection: user-supplied paper p.33. Planning lane geometry; not a site survey.
export const ROAD_LAYOUTS = [
  {
    "id": "J-A",
    "study_number": 1,
    "name": "1 · A.C. Cortes Avenue",
    "mapped_name": "A.C. Cortes Avenue × D.M. Cortes Avenue",
    "signal_node_id": "317764312 / 5634224004",
    "center": [
      10.3304625,
      123.9478423
    ],
    "arms": [
      {
        "id": "AC_NW_IN",
        "road_name": "A.C. Cortes · northwest approach",
        "approach": "N",
        "centerline": [
          [
            10.3304147,
            123.9478103
          ],
          [
            10.3304778,
            123.9477124
          ],
          [
            10.3307196,
            123.9473122
          ],
          [
            10.3311581,
            123.9466185
          ]
        ],
        "reference_m": 20,
        "inbound_lanes": 3,
        "outbound_lanes": 0,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 921916212, 1472504808; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "AC_NW_OUT",
        "road_name": "A.C. Cortes · northwest exit",
        "approach": "N",
        "centerline": [
          [
            10.3304892,
            123.9478644
          ],
          [
            10.330553,
            123.9477609
          ],
          [
            10.330789,
            123.9473878
          ],
          [
            10.3311304,
            123.9468421
          ],
          [
            10.3312367,
            123.9466743
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 0,
        "outbound_lanes": 3,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 1471743350, 97908347, 1472490698; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "AC_SE_IN",
        "road_name": "A.C. Cortes · southeast approach",
        "approach": "S",
        "centerline": [
          [
            10.3304892,
            123.9478644
          ],
          [
            10.3304653,
            123.9479056
          ],
          [
            10.3304248,
            123.9479808
          ],
          [
            10.3303082,
            123.9481728
          ],
          [
            10.3300724,
            123.9485494
          ],
          [
            10.3297875,
            123.9490042
          ],
          [
            10.3296089,
            123.949288
          ],
          [
            10.3293259,
            123.9497291
          ],
          [
            10.3291107,
            123.9500252
          ],
          [
            10.3288805,
            123.9503141
          ],
          [
            10.3286437,
            123.9505863
          ]
        ],
        "reference_m": 20,
        "inbound_lanes": 3,
        "outbound_lanes": 0,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 97908344, 1472487881; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "AC_SE_OUT",
        "road_name": "A.C. Cortes · southeast exit",
        "approach": "S",
        "centerline": [
          [
            10.3304147,
            123.9478103
          ],
          [
            10.3303864,
            123.9478555
          ],
          [
            10.3303416,
            123.9479295
          ],
          [
            10.329699,
            123.9489492
          ],
          [
            10.3295223,
            123.9492322
          ],
          [
            10.3292433,
            123.9496704
          ],
          [
            10.329009,
            123.9499934
          ],
          [
            10.3285682,
            123.9505141
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 0,
        "outbound_lanes": 3,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 1471743349, 725235886; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "DM_NE",
        "road_name": "D.M. Cortes · northeast",
        "approach": "E",
        "centerline": [
          [
            10.3304892,
            123.9478644
          ],
          [
            10.3305762,
            123.9479145
          ],
          [
            10.3307844,
            123.9480375
          ],
          [
            10.3310224,
            123.9481729
          ],
          [
            10.3311661,
            123.9482522
          ],
          [
            10.3311782,
            123.9482589
          ],
          [
            10.331246,
            123.9482986
          ],
          [
            10.3315026,
            123.9484434
          ],
          [
            10.3315839,
            123.9484917
          ],
          [
            10.3316191,
            123.9485135
          ],
          [
            10.3317425,
            123.9485892
          ],
          [
            10.331793,
            123.9486183
          ],
          [
            10.3318558,
            123.9486546
          ],
          [
            10.3322127,
            123.9488534
          ],
          [
            10.3323177,
            123.9489122
          ],
          [
            10.3327133,
            123.9491348
          ],
          [
            10.3327732,
            123.9491703
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 2,
        "outbound_lanes": 2,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 52253090, 1422961438, 894061264; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "DM_SW",
        "road_name": "D.M. Cortes · toward study site 2",
        "approach": "W",
        "centerline": [
          [
            10.3304147,
            123.9478103
          ],
          [
            10.3303482,
            123.9477692
          ],
          [
            10.3302386,
            123.9477045
          ],
          [
            10.3299188,
            123.9475085
          ],
          [
            10.3298429,
            123.9474614
          ],
          [
            10.32974,
            123.9474001
          ],
          [
            10.329682,
            123.9473696
          ],
          [
            10.3291097,
            123.9471002
          ],
          [
            10.3290256,
            123.9470612
          ],
          [
            10.3287803,
            123.9469526
          ],
          [
            10.3281809,
            123.9466796
          ],
          [
            10.3281606,
            123.9466677
          ],
          [
            10.3275188,
            123.9462236
          ],
          [
            10.3273388,
            123.946099
          ],
          [
            10.327328,
            123.946091
          ],
          [
            10.3273098,
            123.9460775
          ],
          [
            10.3270664,
            123.9458865
          ],
          [
            10.3267888,
            123.9456797
          ],
          [
            10.3264996,
            123.9454684
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 2,
        "outbound_lanes": 2,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 97908348, 238044525; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      }
    ]
  },
  {
    "id": "J-B",
    "study_number": 2,
    "name": "2 · D.M. Cortes Street",
    "mapped_name": "D.M. Cortes × C. Ouano / adjacent F. Mendoza",
    "signal_node_id": "581850114",
    "center": [
      10.3262472,
      123.9452764
    ],
    "arms": [
      {
        "id": "DM_NE",
        "road_name": "D.M. Cortes · toward study site 1",
        "approach": "E",
        "centerline": [
          [
            10.3262472,
            123.9452764
          ],
          [
            10.3263105,
            123.9453252
          ],
          [
            10.3263494,
            123.9453551
          ],
          [
            10.3264996,
            123.9454684
          ],
          [
            10.3267888,
            123.9456797
          ],
          [
            10.3270664,
            123.9458865
          ],
          [
            10.3273098,
            123.9460775
          ],
          [
            10.327328,
            123.946091
          ],
          [
            10.3273388,
            123.946099
          ],
          [
            10.3275188,
            123.9462236
          ],
          [
            10.3281606,
            123.9466677
          ],
          [
            10.3281809,
            123.9466796
          ],
          [
            10.3287803,
            123.9469526
          ],
          [
            10.3290256,
            123.9470612
          ],
          [
            10.3291097,
            123.9471002
          ],
          [
            10.329682,
            123.9473696
          ]
        ],
        "reference_m": 16,
        "inbound_lanes": 2,
        "outbound_lanes": 2,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 894056386, 238044525; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "DM_SW",
        "road_name": "D.M. Cortes · toward A. Soriano",
        "approach": "W",
        "centerline": [
          [
            10.3262472,
            123.9452764
          ],
          [
            10.3261588,
            123.9452069
          ],
          [
            10.3254527,
            123.9447226
          ],
          [
            10.3253438,
            123.9446487
          ],
          [
            10.3245593,
            123.9441106
          ],
          [
            10.3244536,
            123.9440407
          ],
          [
            10.3243981,
            123.9440007
          ],
          [
            10.3243136,
            123.9439447
          ],
          [
            10.3240225,
            123.94373
          ],
          [
            10.3239197,
            123.9436616
          ]
        ],
        "reference_m": 16,
        "inbound_lanes": 2,
        "outbound_lanes": 2,
        "lane_width_m": 3.1,
        "geometry_source": "OpenStreetMap ways 854426065, 594406447, 594406448; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "OUANO_NW",
        "road_name": "C. Ouano Street · northwest",
        "approach": "N",
        "centerline": [
          [
            10.3262472,
            123.9452764
          ],
          [
            10.326292,
            123.9451633
          ],
          [
            10.3263753,
            123.9449534
          ],
          [
            10.3265491,
            123.9444768
          ],
          [
            10.326554,
            123.944462
          ],
          [
            10.3267022,
            123.9440648
          ],
          [
            10.3268194,
            123.9437507
          ]
        ],
        "reference_m": 16,
        "inbound_lanes": 1,
        "outbound_lanes": 1,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 1422947353, 854426067, 95609464; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "OUANO_SE",
        "road_name": "C. Ouano Street · southeast",
        "approach": "S",
        "centerline": [
          [
            10.3262472,
            123.9452764
          ],
          [
            10.3261846,
            123.9454259
          ],
          [
            10.3261692,
            123.945459
          ],
          [
            10.3260314,
            123.9458382
          ],
          [
            10.3258987,
            123.9461953
          ],
          [
            10.325685,
            123.9467578
          ],
          [
            10.3253346,
            123.9475768
          ],
          [
            10.3251596,
            123.9480581
          ],
          [
            10.3249117,
            123.9487585
          ],
          [
            10.3247912,
            123.9490704
          ],
          [
            10.3247317,
            123.9492243
          ],
          [
            10.3243869,
            123.950082
          ],
          [
            10.3243677,
            123.9501313
          ],
          [
            10.3243339,
            123.9502182
          ]
        ],
        "reference_m": 16,
        "inbound_lanes": 1,
        "outbound_lanes": 1,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 1421666903, 1469891267, 45656552; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "MENDOZA_NW",
        "road_name": "F. Mendoza · adjacent northwest arm",
        "approach": "N",
        "centerline": [
          [
            10.3264996,
            123.9454684
          ],
          [
            10.32723,
            123.9438969
          ]
        ],
        "reference_m": 13,
        "inbound_lanes": 1,
        "outbound_lanes": 1,
        "lane_width_m": 2.9,
        "geometry_source": "OpenStreetMap ways 95609515; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "MENDOZA_SE",
        "road_name": "F. Mendoza · adjacent southeast arm",
        "approach": "S",
        "centerline": [
          [
            10.3264996,
            123.9454684
          ],
          [
            10.3264929,
            123.9454891
          ],
          [
            10.3264687,
            123.9455504
          ],
          [
            10.3263611,
            123.9458392
          ],
          [
            10.3262717,
            123.9461863
          ],
          [
            10.3260755,
            123.9468297
          ],
          [
            10.3260308,
            123.9469764
          ],
          [
            10.3259707,
            123.9471545
          ],
          [
            10.3256541,
            123.9480858
          ]
        ],
        "reference_m": 13,
        "inbound_lanes": 1,
        "outbound_lanes": 1,
        "lane_width_m": 2.9,
        "geometry_source": "OpenStreetMap ways 1416899109, 1469891265, 1422947352; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      }
    ],
    "layout_note": "Compound study site: the adjacent F. Mendoza crossing shown on paper p.37 is included under site 2. Turning movements and sensing boundaries need field/SUMO mapping."
  },
  {
    "id": "J-C",
    "study_number": 3,
    "name": "3 · A. Soriano Avenue",
    "mapped_name": "A. Soriano / Ouano Avenue × S.B. Cabahug Street",
    "signal_node_id": "280332461 / 494121523",
    "center": [
      10.324589,
      123.941334
    ],
    "arms": [
      {
        "id": "SORIANO_SE",
        "road_name": "A. Soriano · corridor toward study site 2",
        "approach": "E",
        "centerline": [
          [
            10.32457235,
            123.94133715
          ],
          [
            10.324425,
            123.9416707
          ],
          [
            10.324304,
            123.9419396
          ],
          [
            10.3242973,
            123.9419546
          ],
          [
            10.3240542,
            123.9424894
          ],
          [
            10.3240124,
            123.9425858
          ],
          [
            10.323986,
            123.9426489
          ],
          [
            10.3238487,
            123.9429804
          ],
          [
            10.3237817,
            123.9431323
          ]
        ],
        "reference_m": 28,
        "inbound_lanes": 2,
        "outbound_lanes": 3,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 590032352, 51816634, 1457390463, 95609407; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "OUANO_NW_IN",
        "road_name": "Ouano Avenue · northwest approach",
        "approach": "W",
        "centerline": [
          [
            10.3245073,
            123.9412989
          ],
          [
            10.3245291,
            123.9412432
          ],
          [
            10.3245358,
            123.941223
          ],
          [
            10.3245432,
            123.9412006
          ],
          [
            10.3245814,
            123.9410931
          ],
          [
            10.3246202,
            123.9409848
          ],
          [
            10.3247175,
            123.940733
          ],
          [
            10.3248366,
            123.9404081
          ],
          [
            10.3249603,
            123.9400705
          ],
          [
            10.3250708,
            123.939769
          ],
          [
            10.3253476,
            123.939075
          ],
          [
            10.3254186,
            123.9388962
          ],
          [
            10.3254453,
            123.9388216
          ],
          [
            10.3255332,
            123.9385864
          ],
          [
            10.3255416,
            123.938564
          ],
          [
            10.3256039,
            123.9384118
          ],
          [
            10.3256724,
            123.9382209
          ],
          [
            10.3257569,
            123.9379947
          ]
        ],
        "reference_m": 22,
        "inbound_lanes": 4,
        "outbound_lanes": 0,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 933846685, 102243432, 102243435, 237983880; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "OUANO_NW_OUT",
        "road_name": "Ouano Avenue · northwest exit",
        "approach": "W",
        "centerline": [
          [
            10.3246374,
            123.9413754
          ],
          [
            10.3246602,
            123.9413243
          ],
          [
            10.3246752,
            123.9412888
          ],
          [
            10.3247277,
            123.9411792
          ],
          [
            10.3248655,
            123.9408584
          ],
          [
            10.3253152,
            123.9396558
          ],
          [
            10.3253837,
            123.9394823
          ]
        ],
        "reference_m": 22,
        "inbound_lanes": 0,
        "outbound_lanes": 4,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 77594104, 935664545, 102243433, 102243434; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "CABAHUG_NE",
        "road_name": "S.B. Cabahug · northeast",
        "approach": "N",
        "centerline": [
          [
            10.3246374,
            123.9413754
          ],
          [
            10.3246951,
            123.9413723
          ],
          [
            10.3247549,
            123.9414088
          ],
          [
            10.3248124,
            123.941444
          ],
          [
            10.3248682,
            123.9414781
          ],
          [
            10.3249541,
            123.9415306
          ],
          [
            10.3253347,
            123.9417746
          ],
          [
            10.3254176,
            123.9418193
          ],
          [
            10.3259843,
            123.9420357
          ],
          [
            10.3260293,
            123.9420506
          ],
          [
            10.326691,
            123.9422921
          ],
          [
            10.3267118,
            123.9422996
          ]
        ],
        "reference_m": 22,
        "inbound_lanes": 1,
        "outbound_lanes": 1,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 933846687, 1472414580, 1472414579, 211903251; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "CABAHUG_SW_IN",
        "road_name": "S.B. Cabahug · southwest approach",
        "approach": "S",
        "centerline": [
          [
            10.3245073,
            123.9412989
          ],
          [
            10.3243933,
            123.9412287
          ],
          [
            10.3238723,
            123.9408961
          ],
          [
            10.3236003,
            123.9407103
          ],
          [
            10.3235191,
            123.9406588
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 1,
        "outbound_lanes": 0,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 234947394; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      },
      {
        "id": "CABAHUG_SW_OUT",
        "road_name": "S.B. Cabahug · southwest exit",
        "approach": "S",
        "centerline": [
          [
            10.3245291,
            123.9412432
          ],
          [
            10.3242546,
            123.9410631
          ],
          [
            10.3236194,
            123.9406463
          ],
          [
            10.3235405,
            123.9405897
          ]
        ],
        "reference_m": 18,
        "inbound_lanes": 0,
        "outbound_lanes": 2,
        "lane_width_m": 3.0,
        "geometry_source": "OpenStreetMap ways 1471743351, 922325971; reviewed against satellite imagery",
        "reference_status": "Imagery-reviewed crossing proxy; exact signal / stop-line survey required.",
        "lane_width_status": "Planning width; align to vehicle path and verify on site"
      }
    ],
    "layout_note": "A. Soriano approach tapers upstream: two continuous incoming lanes are represented. The short turn pocket and lane inventory require survey before installation; do not extend a third lane into a lane that does not exist."
  }
];
export const STUDY_AREA = {
  "id": "MANDAUE-PAPER-P33",
  "title": "Mandaue City · three-intersection study corridor",
  "source_document": "Transpo_ Signal Timing Optimization.pdf",
  "source_pages": [
    33,
    34,
    36,
    37,
    38
  ],
  "selection_status": "User-designated study area from paper p.33",
  "agency": "Traffic Enforcement Agency of Mandaue (T.E.A.M.)",
  "corridor_links": [
    {
      "from_site": "J-A",
      "to_site": "J-B",
      "reported_distance_m": 548.71,
      "path": [
        [
          10.3304892,
          123.9478644
        ],
        [
          10.3304625,
          123.9478423
        ],
        [
          10.3304147,
          123.9478103
        ],
        [
          10.3303482,
          123.9477692
        ],
        [
          10.3302386,
          123.9477045
        ],
        [
          10.3299188,
          123.9475085
        ],
        [
          10.3298429,
          123.9474614
        ],
        [
          10.32974,
          123.9474001
        ],
        [
          10.329682,
          123.9473696
        ],
        [
          10.3291097,
          123.9471002
        ],
        [
          10.3290256,
          123.9470612
        ],
        [
          10.3287803,
          123.9469526
        ],
        [
          10.3281809,
          123.9466796
        ],
        [
          10.3281606,
          123.9466677
        ],
        [
          10.3275188,
          123.9462236
        ],
        [
          10.3273388,
          123.946099
        ],
        [
          10.327328,
          123.946091
        ],
        [
          10.3273098,
          123.9460775
        ],
        [
          10.3270664,
          123.9458865
        ],
        [
          10.3267888,
          123.9456797
        ],
        [
          10.3264996,
          123.9454684
        ],
        [
          10.3263494,
          123.9453551
        ],
        [
          10.3263105,
          123.9453252
        ],
        [
          10.3262472,
          123.9452764
        ]
      ]
    },
    {
      "from_site": "J-B",
      "to_site": "J-C",
      "reported_distance_m": 596.19,
      "path": [
        [
          10.3262472,
          123.9452764
        ],
        [
          10.3261588,
          123.9452069
        ],
        [
          10.3254527,
          123.9447226
        ],
        [
          10.3253438,
          123.9446487
        ],
        [
          10.3245593,
          123.9441106
        ],
        [
          10.3244536,
          123.9440407
        ],
        [
          10.3243981,
          123.9440007
        ],
        [
          10.3243136,
          123.9439447
        ],
        [
          10.3240225,
          123.94373
        ],
        [
          10.3239197,
          123.9436616
        ],
        [
          10.3237974,
          123.9435686
        ],
        [
          10.32377,
          123.9435427
        ],
        [
          10.3237506,
          123.943521
        ],
        [
          10.323732,
          123.9434939
        ],
        [
          10.3237198,
          123.9434736
        ],
        [
          10.3237095,
          123.9434468
        ],
        [
          10.3237035,
          123.9434174
        ],
        [
          10.323701,
          123.9433839
        ],
        [
          10.3237092,
          123.9433211
        ],
        [
          10.3237817,
          123.9431323
        ],
        [
          10.3238487,
          123.9429804
        ],
        [
          10.323986,
          123.9426489
        ],
        [
          10.3240124,
          123.9425858
        ],
        [
          10.3240542,
          123.9424894
        ],
        [
          10.3242973,
          123.9419546
        ],
        [
          10.324304,
          123.9419396
        ],
        [
          10.324425,
          123.9416707
        ],
        [
          10.3245708,
          123.9415264
        ],
        [
          10.3246374,
          123.9413754
        ]
      ]
    }
  ],
  "scope_note": "The manually controlled minor crossing between sites 2 and 3 is a boundary influence, not a fourth modeled signalized site (paper pp.33–34).",
  "geometry_note": "Road alignment is derived from OpenStreetMap, reviewed against imagery. Reported paper distances are not used to stretch coordinates."
};
