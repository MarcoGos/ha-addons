from typing import Any

MAPPING: dict[str, dict[str, Any]] = {
    'uwind': {
        'code': 'UGRD', 
        'layer': '10 m above ground'
    },
    'vwind': {
        'code': 'VGRD',
        'layer': '10 m above ground'
    },
    'gust': {
        'code': 'GUST', 
        'layer': 'surface'
    },
    'tmin': {
        'code': 'TMIN', 
        'layer': '2 m above ground',
        'correction': -273
    },
    'tmax': {
        'code': 'TMAX', 
        'layer': '2 m above ground',
        'correction': -273
    },
    'tmp': {
        'code': 'TMP', 
        'layer': '2 m above ground',
        'correction': -273
    },
    'tsfc': {
        'code': 'TMP', 
        'layer': 'surface',
        'correction': -273
    },
    # 'tmp850hpa': {
    #     'code': 'TMP', 
    #     'layer': '850 mb',
    #     'correction': -273
    # },
    'tmp500hpa': {
        'code': 'TMP', 
        'layer': '500 mb',
        'correction': -273
    },
    'cldhigh': {
        'code': 'HCDC', 
        'layer': 'high cloud layer'
    },
    'cldmid': {
        'code': 'MCDC', 
        'layer': 'middle cloud layer'
    },
    'cldlow': {
        'code': 'LCDC', 
        'layer': 'low cloud layer'
    },
    'cldtotal': {
        'code': 'TCDC', 
        'layer': 'entire atmosphere'
    },
    'rain': {
        'code': 'APCP', 
        'layer': 'surface'
    },
    'humidity': {
        'code': 'RH', 
        'layer': '2 m above ground'
    },
    'cape': {
        'code': 'CAPE', 
        'layer': 'surface'
    },
    'liftedindex': {
        'code': '4LFTX',
        'layer': 'surface'
    },
    'pres': {
        'code': 'PRES', 
        'layer': 'surface'
    },        
    'vis': {
        'code': 'VIS', 
        'layer': 'surface'
    }
}

# def get_inventory_key_from_mapping(key: str) -> str:
#     if key in MAPPING:
#         return '{}:{}'.format(MAPPING[key]['code'], MAPPING[key]['layer'])