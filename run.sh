#!/bin/bash

# bounding boxes from https://boundingbox.klokantech.com
# centre from google maps

# build docker image
docker build -t transport-performance .

## ireland
#belfast
AREA_NAME='belfast' BBOX='-6.6273,54.2127,-5.232,54.9576' BBOX_CRS='EPSG: 4326' CENTRE='54.59774732357715,-5.929280707933035' CENTRE_CRS='EPSG: 4326' docker compose up
#londonderry/derry
AREA_NAME='derry' BBOX='-8.0226,54.6314,-6.6273,55.3687' BBOX_CRS='EPSG: 4326' CENTRE='54.995395629345566,-7.321984350253395' CENTRE_CRS='EPSG: 4326' docker compose up

##wales
#cardiff
AREA_NAME='cardiff' BBOX='-3.876433,51.083443,-2.48117,51.883883' BBOX_CRS='EPSG: 4326' CENTRE='51.479934665042386,-3.1781754268238376' CENTRE_CRS='EPSG: 4326' docker compose up
#newport
AREA_NAME='newport' BBOX='-3.6955,51.1869,-2.3002,51.9855' BBOX_CRS='EPSG: 4326' CENTRE='51.587709569312544,-2.995616630402366' CENTRE_CRS='EPSG: 4326' docker compose up
#swansea
AREA_NAME='swansea' BBOX='-4.643734,51.22059,-3.248471,52.018642' BBOX_CRS='EPSG: 4326' CENTRE='51.6198709817158,-3.9383584722165574' CENTRE_CRS='EPSG: 4326' docker compose up

##scotland
#aberdeen
AREA_NAME='aberdeen' BBOX='-2.7882,56.7959,-1.393,57.4932' BBOX_CRS='EPSG: 4326' CENTRE='57.14756483206266,-2.0993193309063987' CENTRE_CRS='EPSG: 4326' docker compose up
#ayr
#AREA_NAME='ayr' BBOX='-5.3096,55.0951,-3.9143,55.8239' BBOX_CRS='EPSG: 4326' CENTRE='55.4606360718252,-4.627077975673397' CENTRE_CRS='EPSG: 4326' docker compose up
#dundee
AREA_NAME='dundee' BBOX='-3.6644,56.1037,-2.2691,56.8139' BBOX_CRS='EPSG: 4326' CENTRE='56.461037934789246,-2.9683932771892705' CENTRE_CRS='EPSG: 4326' docker compose up
#edinburgh
AREA_NAME='edinburgh' BBOX='-3.8814,55.5887,-2.4861,56.3084' BBOX_CRS='EPSG: 4326' CENTRE='55.95391985485487,-3.1983895184374824' CENTRE_CRS='EPSG: 4326' docker compose up
#glasgow
AREA_NAME='glasgow' BBOX='-4.9471,55.4939,-3.5518,56.2154' BBOX_CRS='EPSG: 4326' CENTRE='55.85325353491739,-4.256031712361221' CENTRE_CRS='EPSG: 4326' docker compose up

##england
# birmingham
AREA_NAME='birmingham' BBOX='-2.596,52.0908,-1.2007,52.8735' BBOX_CRS='EPSG: 4326' CENTRE='52.48044813247625,-1.9010131228777054' CENTRE_CRS='EPSG: 4326' docker compose up
# blackburn
AREA_NAME='blackburn' BBOX='-3.180833,53.367355,-1.785569,54.127446' BBOX_CRS='EPSG: 4326' CENTRE='53.74677370018828,-2.4816443734943454' CENTRE_CRS='EPSG: 4326' docker compose up
# blackpool
AREA_NAME='blackpool' BBOX='-3.7466,53.4361,-2.3514,54.195' BBOX_CRS='EPSG: 4326' CENTRE='53.81611078368778,-3.053009760507232' CENTRE_CRS='EPSG: 4326' docker compose up
# brighton
AREA_NAME='brighton' BBOX='-0.840145,50.414664,0.555119,51.226687' BBOX_CRS='EPSG: 4326' CENTRE='50.82396432384774,-0.15261719285017575' CENTRE_CRS='EPSG: 4326' docker compose up
# bristol
AREA_NAME='bristol' BBOX='-3.294,51.0515,-1.8988,51.8524' BBOX_CRS='EPSG: 4326' CENTRE='51.45476476529719,-2.5915942578073246' CENTRE_CRS='EPSG: 4326' docker compose up
# cambridge
AREA_NAME='cambridge' BBOX='-0.5749,51.8083,0.8203,52.5961' BBOX_CRS='EPSG: 4326' CENTRE='52.1945569916661, 0.13620232829155013' CENTRE_CRS='EPSG: 4326' docker compose up
# hastings
AREA_NAME='hastings' BBOX='-0.112129,50.44878,1.283135,51.260216' BBOX_CRS='EPSG: 4326' CENTRE='50.85649798120869, 0.5815027556670932' CENTRE_CRS='EPSG: 4326' docker compose up
# hull
AREA_NAME='hull' BBOX='-1.035,53.3588,0.3603,54.119' BBOX_CRS='EPSG: 4326' CENTRE='53.745857797674915,-0.3394095523159548' CENTRE_CRS='EPSG: 4326' docker compose up
# leeds-bradford
AREA_NAME='leeds-bradford' BBOX='-2.238,53.4112,-0.8427,54.1705' BBOX_CRS='EPSG: 4326' CENTRE='53.79821584536564,-1.546549157407777' CENTRE_CRS='EPSG: 4326' docker compose up
# liverpool
AREA_NAME='liverpool' BBOX='-3.6818,53.0202,-2.2866,53.7865' BBOX_CRS='EPSG: 4326' CENTRE='53.40562178617905,-2.9813298622510875' CENTRE_CRS='EPSG: 4326' docker compose up
# london
AREA_NAME='london' BBOX='-0.8262,51.1087,0.569,51.9087' BBOX_CRS='EPSG: 4326' CENTRE='51.50918619320749,-0.126409042922771' CENTRE_CRS='EPSG: 4326' docker compose up
# manchester
AREA_NAME='manchester' BBOX='-2.9061,53.0723,-1.5108,53.8376' BBOX_CRS='EPSG: 4326' CENTRE='53.4901779140037,-2.2324148862360778' CENTRE_CRS='EPSG: 4326' docker compose up
# milton keynes
AREA_NAME='milton keynes' BBOX='-1.458,51.6368,-0.0627,52.4276' BBOX_CRS='EPSG: 4326' CENTRE='52.03976615105606,-0.7564936285139618' CENTRE_CRS='EPSG: 4326' docker compose up
# newcastle
AREA_NAME='newcastle' BBOX='-2.3039,54.6007,-0.9086,55.3385' BBOX_CRS='EPSG: 4326' CENTRE='54.97598394815939,-1.606516880628735' CENTRE_CRS='EPSG: 4326' docker compose up
# norwich
AREA_NAME='norwich' BBOX='0.5965,52.2354,1.9918,53.0156' BBOX_CRS='EPSG: 4326' CENTRE='52.63011966847089,1.2943199298277903' CENTRE_CRS='EPSG: 4326' docker compose up
# nottingham
AREA_NAME='nottingham' BBOX='-1.8535,52.5638,-0.4582,53.3383' BBOX_CRS='EPSG: 4326' CENTRE='52.95382841412136,-1.14606924203261' CENTRE_CRS='EPSG: 4326' docker compose up
# plymouth
AREA_NAME='plymouth' BBOX='-4.8362,49.9627,-3.441,50.7825' BBOX_CRS='EPSG: 4326' CENTRE='50.3716816662627,-4.143490763160838' CENTRE_CRS='EPSG: 4326' docker compose up
# portsmouth
AREA_NAME='portsmouth' BBOX='-1.793,50.3919,-0.3978,51.2043' BBOX_CRS='EPSG: 4326' CENTRE='50.80521006801556,-1.0849195287774007' CENTRE_CRS='EPSG: 4326' docker compose up
# sheffield
AREA_NAME='sheffield' BBOX='-2.1666,52.9958,-0.7713,53.7625' BBOX_CRS='EPSG: 4326' CENTRE='53.38072846707806,-1.4709422792217148' CENTRE_CRS='EPSG: 4326' docker compose up
# southampton
AREA_NAME='southampton' BBOX='-2.1007,50.4969,-0.7054,51.3075' BBOX_CRS='EPSG: 4326' CENTRE='50.90453978661142,-1.4067442947933784' CENTRE_CRS='EPSG: 4326' docker compose up
# stockton-on-tees
AREA_NAME='stockton-on-tees' BBOX='-2.0037,54.191,-0.6084,54.9363' BBOX_CRS='EPSG: 4326' CENTRE='54.564977495323554,-1.3131684918587296' CENTRE_CRS='EPSG: 4326' docker compose up
# stoke-on-trent
AREA_NAME='stoke-on-trent' BBOX='-2.8716,52.6244,-1.4763,53.3977' BBOX_CRS='EPSG: 4326' CENTRE='53.01806606037784,-2.1827667206338726' CENTRE_CRS='EPSG: 4326' docker compose up
# torbay
AREA_NAME='torbay' BBOX='-4.2174,50.055,-2.8222,50.8732' BBOX_CRS='EPSG: 4326' CENTRE='50.46663173051545,-3.5310875889885858' CENTRE_CRS='EPSG: 4326' docker compose up