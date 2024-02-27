# change default shell to bash
SHELL := /bin/bash

# bounding boxes from https://boundingbox.klokantech.com
# centre from google maps

# build docker image
docker_build:
	docker build -t transport-performance .

# remove dangling docker images
clean_docker_images:
	docker image prune

# run all areas
all: | docker_build england ireland scotland wales

## ireland
ireland: belfast derry
belfast:
	COUNTRY_NAME='ireland' AREA_NAME='belfast' BBOX='-6.6273,54.2127,-5.232,54.9576' CENTRE='54.59774732357715,-5.929280707933035' docker compose up
derry:
	COUNTRY_NAME='ireland' AREA_NAME='derry' BBOX='-8.0226,54.6314,-6.6273,55.3687' CENTRE='54.995395629345566,-7.321984350253395' docker compose up

##wales
wales: cardiff newport swansea
cardiff:
	COUNTRY_NAME='wales' AREA_NAME='cardiff' BBOX='-3.876433,51.083443,-2.48117,51.883883' CENTRE='51.479934665042386,-3.1781754268238376' docker compose up
newport:
	COUNTRY_NAME='wales' AREA_NAME='newport' BBOX='-3.6955,51.1869,-2.3002,51.9855' CENTRE='51.587709569312544,-2.995616630402366' docker compose up
swansea:
	COUNTRY_NAME='wales' AREA_NAME='swansea' BBOX='-4.643734,51.22059,-3.248471,52.018642' CENTRE='51.6198709817158,-3.9383584722165574' docker compose up

##scotland
scotland: aberdeen dundee edinburgh glasgow
aberdeen:
	COUNTRY_NAME='scotland' AREA_NAME='aberdeen' BBOX='-2.7882,56.7959,-1.393,57.4932' CENTRE='57.14756483206266,-2.0993193309063987' docker compose up
dundee:
	COUNTRY_NAME='scotland' AREA_NAME='dundee' BBOX='-3.6644,56.1037,-2.2691,56.8139' CENTRE='56.461037934789246,-2.9683932771892705' docker compose up
edinburgh:
	COUNTRY_NAME='scotland' AREA_NAME='edinburgh' BBOX='-3.8814,55.5887,-2.4861,56.3084' CENTRE='55.95391985485487,-3.1983895184374824' docker compose up
glasgow:
	COUNTRY_NAME='scotland' AREA_NAME='glasgow' BBOX='-4.9471,55.4939,-3.5518,56.2154' CENTRE='55.85325353491739,-4.256031712361221' docker compose up

##england
england: birmingham blackburn blackpool brighton bristol cambridge hastings hull leeds_bradford liverpool london manchester milton_keynes newcastle norwich \
	nottingham plymouth portsmouth sheffield southampton stockton_on_tees stoke_on_trent torbay
birmingham:
	COUNTRY_NAME='england' AREA_NAME='birmingham' BBOX='-2.596,52.0908,-1.2007,52.8735' CENTRE='52.48044813247625,-1.9010131228777054' docker compose up
blackburn:
	COUNTRY_NAME='england' AREA_NAME='blackburn' BBOX='-3.180833,53.367355,-1.785569,54.127446' CENTRE='53.74677370018828,-2.4816443734943454' docker compose up
blackpool:
	COUNTRY_NAME='england' AREA_NAME='blackpool' BBOX='-3.745,53.4366,-2.3497,54.1955' CENTRE='53.81860386826019,-3.038210861131225' docker compose up
brighton:
	COUNTRY_NAME='england' AREA_NAME='brighton' BBOX='-0.840145,50.414664,0.555119,51.226687' CENTRE='50.82396432384774,-0.15261719285017575' docker compose up
bristol:
	COUNTRY_NAME='england' AREA_NAME='bristol' BBOX='-3.294,51.0515,-1.8988,51.8524' CENTRE='51.45476476529719,-2.5915942578073246' docker compose up
cambridge:
	COUNTRY_NAME='england' AREA_NAME='cambridge' BBOX='-0.5749,51.8083,0.8203,52.5961' CENTRE='52.1945569916661, 0.13620232829155013' docker compose up
hastings:
	COUNTRY_NAME='england' AREA_NAME='hastings' BBOX='-0.112129,50.44878,1.283135,51.260216' CENTRE='50.85649798120869, 0.5815027556670932' docker compose up
hull:
	COUNTRY_NAME='england' AREA_NAME='hull' BBOX='-1.035,53.3588,0.3603,54.119' CENTRE='53.745857797674915,-0.3394095523159548' docker compose up
leeds_bradford:
	COUNTRY_NAME='england' AREA_NAME='leeds-bradford' BBOX='-2.238,53.4112,-0.8427,54.1705' CENTRE='53.79821584536564,-1.546549157407777' docker compose up
liverpool:
	COUNTRY_NAME='england' AREA_NAME='liverpool' BBOX='-3.6818,53.0202,-2.2866,53.7865' CENTRE='53.40562178617905,-2.9813298622510875' docker compose up
london:
	COUNTRY_NAME='england' AREA_NAME='london' BBOX='-0.8262,51.1087,0.569,51.9087' CENTRE='51.50918619320749,-0.126409042922771' docker compose up
manchester:
	COUNTRY_NAME='england' AREA_NAME='manchester' BBOX='-2.9061,53.0723,-1.5108,53.8376' CENTRE='53.4901779140037,-2.2324148862360778' docker compose up
milton_keynes:
	COUNTRY_NAME='england' AREA_NAME='milton keynes' BBOX='-1.458,51.6368,-0.0627,52.4276' CENTRE='52.03976615105606,-0.7564936285139618' docker compose up
newcastle:
	COUNTRY_NAME='england' AREA_NAME='newcastle' BBOX='-2.3039,54.6007,-0.9086,55.3385' CENTRE='54.97598394815939,-1.606516880628735' docker compose up
norwich:
	COUNTRY_NAME='england' AREA_NAME='norwich' BBOX='0.5965,52.2354,1.9918,53.0156' CENTRE='52.63011966847089,1.2943199298277903' docker compose up
nottingham:
	COUNTRY_NAME='england' AREA_NAME='nottingham' BBOX='-1.8535,52.5638,-0.4582,53.3383' CENTRE='52.95382841412136,-1.14606924203261' docker compose up
plymouth:
	COUNTRY_NAME='england' AREA_NAME='plymouth' BBOX='-4.8362,49.9627,-3.441,50.7825' CENTRE='50.3716816662627,-4.143490763160838' docker compose up
portsmouth:
	COUNTRY_NAME='england' AREA_NAME='portsmouth' BBOX='-1.793,50.3919,-0.3978,51.2043' CENTRE='50.80521006801556,-1.0849195287774007' docker compose up
sheffield:
	COUNTRY_NAME='england' AREA_NAME='sheffield' BBOX='-2.1666,52.9958,-0.7713,53.7625' CENTRE='53.38072846707806,-1.4709422792217148' docker compose up
southampton:
	COUNTRY_NAME='england' AREA_NAME='southampton' BBOX='-2.1007,50.4969,-0.7054,51.3075' CENTRE='50.90453978661142,-1.4067442947933784' docker compose up
stockton_on_tees:
	COUNTRY_NAME='england' AREA_NAME='stockton-on-tees' BBOX='-2.0037,54.191,-0.6084,54.9363' CENTRE='54.564977495323554,-1.3131684918587296' docker compose up
stoke_on_trent:
	COUNTRY_NAME='england' AREA_NAME='stoke-on-trent' BBOX='-2.8716,52.6244,-1.4763,53.3977' CENTRE='53.01806606037784,-2.1827667206338726' docker compose up
torbay:
	COUNTRY_NAME='england' AREA_NAME='torbay' BBOX='-4.2174,50.055,-2.8222,50.8732' CENTRE='50.46663173051545,-3.5310875889885858' docker compose up
