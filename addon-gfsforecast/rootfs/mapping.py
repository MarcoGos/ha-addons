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
        'layer': 'surface',
        'detailed': True
    },
    'tmin': {
        'code': 'TMIN', 
        'layer': '2 m above ground',
        'correction': -273,
        'detailed': True
    },
    'tmax': {
        'code': 'TMAX', 
        'layer': '2 m above ground',
        'correction': -273,
        'detailed': True
    },
    'tmp': {
        'code': 'TMP', 
        'layer': '2 m above ground',
        'correction': -273
    },
    'tsfc': {
        'code': 'TMP', 
        'layer': 'surface',
        'correction': -273,
        'detailed': True
    },
    'tmp500hpa': {
        'code': 'TMP', 
        'layer': '500 mb',
        'correction': -273,
        'detailed': True
    },
    'cldhigh': {
        'code': 'HCDC', 
        'layer': 'high cloud layer'
    },
    'cldmid': {
        'code': 'MCDC', 
        'layer': 'middle cloud layer',
        'detailed': True
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
        'layer': '2 m above ground',
        'detailed': True
    },
    'cape': {
        'code': 'CAPE', 
        'layer': 'surface',
        'detailed': True
    },
    'liftedindex': {
        'code': '4LFTX',
        'layer': 'surface',
        'detailed': True
    },
    'pres': {
        'code': 'PRES', 
        'layer': 'surface',
        'detailed': True
    },        
    'vis': {
        'code': 'VIS', 
        'layer': 'surface',
        'detailed': True
    }
}
