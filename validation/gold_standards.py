# r2m_office DB GOLD STANDARD - Version 1

#A Version (Original)
gold_standard = {
        "extinguisher_check1": {
            "rule_text": "Are all portable fire extinguishers readily accessible and not restricted by stored items?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
        },
        "extinguisher_check2": {
            "rule_text": "Are portable fire extinguishers either securely wall mounted or on a supplied stand?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
        },
        "extinguisher_check3": {
            "rule_text": "Are portable fire extinguishers clearly labelled?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
        },
        "fire_call_check": {
            "rule_text": "Are all fire alarm call points clearly signed and easily accessible?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
        },
        "fire_escape_check1": {
            "rule_text": "Are fire exit signs installed at the proper locations and remain clearly visible?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
        },
        "door_check": {
            "rule_text": "Are fire doors kept closed, i.e., not wedged open?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
        },
        "waste_check": {
            "rule_text": "Is waste and rubbish kept in a designated area?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
        },
        "ignition_check": {
            "rule_text": "Have combustible materials been stored away from sources of ignition?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
        },
        "fire_escape_check2": {
            "rule_text": "Are fire escape routes kept clear?",
            "overall_compliant": True,
            "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
        },
        "fall_check": {
            "rule_text": "Are there any objects on the walk path?",
            "overall_compliant": False,
            "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
        }
    }

#B Version 
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Is access to portable fire extinguishers free from obstruction by nearby items?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
    },
    "extinguisher_check2": {
        "rule_text": "Have portable fire extinguishers been safely mounted to walls or placed on proper stands?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
    },
    "extinguisher_check3": {
        "rule_text": "Is the labelling on all portable fire extinguishers clear and visible?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
    },
    "fire_call_check": {
        "rule_text": "Is signage at all fire alarm call points clearly visible, and are these points easy to reach?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
    },
    "fire_escape_check1": {
        "rule_text": "Are signs marking fire exits placed appropriately and clearly noticeable at all times?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
    },
    "door_check": {
        "rule_text": "Is each fire door completely shut and not held open?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
    },
    "waste_check": {
        "rule_text": "Are waste materials and rubbish placed exclusively within their designated spaces?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
    },
    "ignition_check": {
        "rule_text": "Are all combustible items kept at a safe distance from ignition points?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
    },
    "fire_escape_check2": {
        "rule_text": "Is there any obstruction blocking fire escape routes?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
    },
    "fall_check": {
        "rule_text": "Is the walkway clear of objects that could obstruct passage?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
    }
}

#C Version 
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Can portable fire extinguishers be easily reached without stored items blocking them?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
    },
    "extinguisher_check2": {
        "rule_text": "Are portable fire extinguishers securely positioned, either wall-fixed or stand-supported?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
    },
    "extinguisher_check3": {
        "rule_text": "Do portable fire extinguishers have clear identification labels?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
    },
    "fire_call_check": {
        "rule_text": "Can occupants easily find and access clearly labelled fire alarm call points?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
    },
    "fire_escape_check1": {
        "rule_text": "Can occupants clearly see all fire exit signs positioned at required locations?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
    },
    "door_check": {
        "rule_text": "Have all fire doors remained closed and free from obstruction?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
    },
    "waste_check": {
        "rule_text": "Has all rubbish been confined strictly to designated disposal areas?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
    },
    "ignition_check": {
        "rule_text": "Is there adequate separation between combustible materials and sources of ignition?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
    },
    "fire_escape_check2": {
        "rule_text": "Do fire escape paths remain unobstructed and easy to use?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
    },
    "fall_check": {
        "rule_text": "Are any items placed directly in the walking area?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
    }
}

#D Version
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Is access to hand-held fire suppression devices blocked by surrounding furnishings or items?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
    },
    "extinguisher_check2": {
        "rule_text": "Are manual fire extinguishing units properly mounted on walls or placed on certified supports?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
    },
    "extinguisher_check3": {
        "rule_text": "Do all emergency fire spray devices have visible identification labels?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
    },
    "fire_call_check": {
        "rule_text": "Are the manual emergency alert stations marked with signage and easy to reach?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
    },
    "fire_escape_check1": {
        "rule_text": "Are exit route indicators located appropriately and not obscured?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
    },
    "door_check": {
        "rule_text": "Are emergency doors shut properly and not held open?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
    },
    "waste_check": {
        "rule_text": "Are refuse bins stored within designated containment areas?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
    },
    "ignition_check": {
        "rule_text": "Are flammable supplies positioned safely away from ignition risks?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
    },
    "fire_escape_check2": {
        "rule_text": "Are emergency evacuation points unobstructed by any items?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
    },
    "fall_check": {
        "rule_text": "Are pedestrian corridors free from encroaching objects?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
    }
}

#E Version
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Do furnishings or stored equipment obstruct easy access to fire extinguishing canisters?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguisher EX-3002:323069 (ID:109) is adjacent to chairs (ID:98, 99) on multiple sides, restricting access. Other extinguishers (IDs 1, 2, 3, 107) are unobstructed and compliant."
    },
    "extinguisher_check2": {
        "rule_text": "Are all extinguishers either properly fixed to structural surfaces or resting on approved holders?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because extinguishers EX-3002:323045 (ID:107) and EX-3002:323069 (ID:109) are not affixed to any wall—only touching floor and nearby objects. Others (IDs 1, 2, 3) are affixed and compliant."
    },
    "extinguisher_check3": {
        "rule_text": "Do the fire extinguishing tools display visible identification tags?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because only extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111); the others (IDs 2, 3, 107, 109) lack label contact, violating the rule."
    },
    "fire_call_check": {
        "rule_text": "Are fire emergency activation points clearly marked and not obstructed?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Alarm Manual Call Point (ID:115) lacks signage; ID:113 is clearly signed and both are physically accessible, but missing signage for ID:115 causes violation."
    },
    "fire_escape_check1": {
        "rule_text": "Are fire direction signs properly located and clearly visible at all times?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Exit Sign (ID:117) is correctly placed above fire exit doors (IDs 88, 18) and partially contained in/touching a wall (ID:52), meeting placement and visibility requirements."
    },
    "door_check": {
        "rule_text": "Are all fire-resistance doors maintained in a fully shut position?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because FireExitDoor2 (ID:132) is only 11.4–27.6% contained in its frame and wall, indicating it is wedged open. Door ID:18 is sufficiently contained and compliant."
    },
    "waste_check": {
        "rule_text": "Is trash stored in authorized containment zones?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Waste bin (ID:10) is 21.9% contained within Trash Disposal Area (ID:118), which is sufficient for compliance."
    },
    "ignition_check": {
        "rule_text": "Are fire-prone substances kept away from electrical sources?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Stock of Paper (ID:110), a combustible material, is near a 3 Phase Socket Outlet (ID:77), an ignition source. Other plants (IDs 100, 101) are safe."
    },
    "fire_escape_check2": {
        "rule_text": "Is the emergency egress doors kept clear of physical barriers?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because objects near FireExit_Door (ID:18, 132) do not block access; placement of extinguisher and HVAC device is acceptable and does not obstruct the route."
    },
    "fall_check": {
        "rule_text": "Are footpaths within the room free of any obstructions?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because Fire Extinguisher (ID:107) is located on top of walkway1 (ID:119), representing clear violations."
    }
}


#r2m_officeV2 GOLD STANDARD

#A Version (Original)
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Are all portable fire extinguishers readily accessible and not restricted by stored items?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Are portable fire extinguishers either securely wall mounted or on a supplied stand?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall."
    },
    "extinguisher_check3": {
        "rule_text": "Are portable fire extinguishers clearly labelled?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Are all fire alarm call points clearly signed and easily accessible?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Are fire exit signs installed at the proper locations and remain clearly visible?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Are fire doors kept closed, i.e., not wedged open?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Is waste and rubbish kept in a designated area?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within designated trash area."
    },
    "ignition_check": {
        "rule_text": "Have combustible materials been stored away from sources of ignition?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Are fire escape routes kept clear?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Are there any objects on the walk path?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}


#B Version 
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Is access to portable fire extinguishers free from obstruction by nearby items?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Have portable fire extinguishers been safely mounted to walls or placed on proper stands?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall or mounted on an appropriate stand."
    },
    "extinguisher_check3": {
        "rule_text": "Is the labelling on all portable fire extinguishers clear and visible?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Is signage at all fire alarm call points clearly visible, and are these points easy to reach?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Are signs marking fire exits placed appropriately and clearly noticeable at all times?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Is each fire door completely shut and not held open?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Are waste materials and rubbish placed exclusively within their designated spaces?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within the designated Trash Disposal Area."
    },
    "ignition_check": {
        "rule_text": "Are all combustible items kept at a safe distance from ignition points?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Is there any obstruction blocking fire escape routes?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Is the walkway clear of objects that could obstruct passage?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}

#C Version
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Can portable fire extinguishers be easily reached without stored items blocking them?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Are portable fire extinguishers securely positioned, either wall-fixed or stand-supported?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall or mounted on an appropriate stand."
    },
    "extinguisher_check3": {
        "rule_text": "Do portable fire extinguishers have clear identification labels?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Can occupants easily find and access clearly labelled fire alarm call points?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Can occupants clearly see all fire exit signs positioned at required locations?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Have all fire doors remained closed and free from obstruction?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Has all rubbish been confined strictly to designated disposal areas?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within the designated Trash Disposal Area."
    },
    "ignition_check": {
        "rule_text": "Is there adequate separation between combustible materials and sources of ignition?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Do fire escape paths remain unobstructed and easy to use?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Are any items placed directly in the walking area?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}

#D Version 
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Is access to hand-held fire suppression devices blocked by surrounding furnishings or items?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Are manual fire extinguishing units properly mounted on walls or placed on certified supports?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall or mounted on an appropriate stand."
    },
    "extinguisher_check3": {
        "rule_text": "Do all emergency fire spray devices have visible identification labels?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Are the manual emergency alert stations marked with signage and easy to reach?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Are exit route indicators located appropriately and not obscured?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Are emergency doors shut properly and not held open?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Are refuse bins stored within designated containment areas?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within the designated Trash Disposal Area."
    },
    "ignition_check": {
        "rule_text": "Are flammable supplies positioned safely away from ignition risks?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Are emergency evacuation points unobstructed by any items?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Are pedestrian corridors free from encroaching objects?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}

#E Version
gold_standard = {
    "extinguisher_check1": {
        "rule_text": "Do furnishings or stored equipment obstruct easy access to fire extinguishing canisters?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are not obstructed by any nearby stored items and are easily accessible."
    },
    "extinguisher_check2": {
        "rule_text": "Are all extinguishers either properly fixed to structural surfaces or resting on approved holders?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguishers (IDs 1, 2, 3) are properly affixed to a wall or mounted on an appropriate stand."
    },
    "extinguisher_check3": {
        "rule_text": "Do the fire extinguishing tools display visible identification tags?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because extinguisher EX-3002:323036 (ID:1) is touching a label (ID:111), and extinguishers (IDs 2, 3) are also in contact with clearly visible labels."
    },
    "fire_call_check": {
        "rule_text": "Are fire emergency activation points clearly marked and not obstructed?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because both fire alarm call points (IDs 113 and 115) are clearly signed and physically accessible."
    },
    "fire_escape_check1": {
        "rule_text": "Are fire direction signs properly located and clearly visible at all times?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because no fire exit sign is positioned correctly above the fire exit doors, failing visibility and placement requirements."
    },
    "door_check": {
        "rule_text": "Are all fire-resistance doors maintained in a fully shut position?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because Fire Door (ID:18) is sufficiently contained within its frame and surrounding wall, indicating it is closed."
    },
    "waste_check": {
        "rule_text": "Is trash stored in authorized containment zones?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because the Waste Bin (ID:10) is not properly placed within the designated Trash Disposal Area."
    },
    "ignition_check": {
        "rule_text": "Are fire-prone substances kept away from electrical sources?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because the combustible materials, such as plants (IDs 100, 101), are not near any ignition sources."
    },
    "fire_escape_check2": {
        "rule_text": "Is the emergency egress doors kept clear of physical barriers?",
        "overall_compliant": False,
        "explanation_summary": "Rule is not compliant because a furnishing object (ID:98) is positioned directly in front of Fire Exit Door (ID:19), obstructing access, despite nearby extinguishers and HVAC devices not causing obstruction."
    },
    "fall_check": {
        "rule_text": "Are footpaths within the room free of any obstructions?",
        "overall_compliant": True,
        "explanation_summary": "Rule is compliant because no objects are located directly on the surface of walkway1 (ID:119), ensuring a clear walking path."
    }
}