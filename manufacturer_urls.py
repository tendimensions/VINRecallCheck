"""
Mapping of vehicle manufacturers to their recall lookup URLs.
"""

MANUFACTURER_RECALL_URLS = {
    'HYUNDAI': 'https://owners.hyundaiusa.com/us/en/resources/recalls.html',
    'KIA': 'https://owners.kia.com/us/en/recall-info.html',
    'GENESIS': 'https://www.genesis.com/us/en/owners/service/recalls.html',
    
    'JEEP': 'https://recalls.mopar.com/',
    'DODGE': 'https://recalls.mopar.com/',
    'CHRYSLER': 'https://recalls.mopar.com/',
    'RAM': 'https://recalls.mopar.com/',
    'FIAT': 'https://recalls.mopar.com/',
    'ALFA ROMEO': 'https://recalls.mopar.com/',
    
    'FORD': 'https://owner.ford.com/tools/recalls.html',
    'LINCOLN': 'https://owner.lincoln.com/tools/recalls.html',
    
    'CHEVROLET': 'https://www.chevrolet.com/recalls',
    'GMC': 'https://www.gmc.com/recalls',
    'BUICK': 'https://www.buick.com/recalls',
    'CADILLAC': 'https://www.cadillac.com/recalls',
    
    'HONDA': 'https://owners.honda.com/service-maintenance/recalls',
    'ACURA': 'https://owners.acura.com/service-maintenance/recalls',
    
    'TOYOTA': 'https://www.toyota.com/recall',
    'LEXUS': 'https://drivers.lexus.com/lexusdrivers/resources/safety-recalls',
    
    'NISSAN': 'https://www.nissan-recalls.com/',
    'INFINITI': 'https://www.infinitiusa.com/recalls-vin',
    
    'MAZDA': 'https://www.mazdausa.com/recalls',
    
    'SUBARU': 'https://www.subaru.com/vehicle-recalls.html',
    
    'VOLKSWAGEN': 'https://www.vw.com/recalls/',
    'AUDI': 'https://www.audiusa.com/us/web/en/recall-lookup.html',
    'PORSCHE': 'https://www.porsche.com/usa/recalls/',
    
    'BMW': 'https://www.bmwusa.com/recalls-and-campaigns.html',
    'MINI': 'https://www.miniusa.com/recalls-and-campaigns.html',
    
    'MERCEDES-BENZ': 'https://www.mbusa.com/en/recall',
    'MERCEDES BENZ': 'https://www.mbusa.com/en/recall',
    
    'VOLVO': 'https://www.volvocars.com/us/support/recalls/',
    
    'TESLA': 'https://www.tesla.com/support/service-and-repairs/recalls',
    
    'RIVIAN': 'https://www.rivian.com/support/article/how-do-i-find-out-if-my-rivian-has-an-open-recall',
    
    'LUCID': 'https://www.lucidmotors.com/owners/recalls',
}


def get_recall_url(make: str) -> str:
    """
    Get the recall lookup URL for a specific manufacturer.
    
    Args:
        make: The vehicle manufacturer name
        
    Returns:
        The recall lookup URL, or NHTSA default if not found
    """
    make_upper = make.upper().strip()
    url = MANUFACTURER_RECALL_URLS.get(make_upper)
    
    if url:
        return url
    else:
        # Default to NHTSA if manufacturer not found
        return 'https://www.nhtsa.gov/recalls'
