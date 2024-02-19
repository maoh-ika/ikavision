from dataclasses import dataclass
from models.detected_item import DetectedItem
from models.buki import SubWeapon, SpecialWeapon

@dataclass
class SubWeaponIcon(DetectedItem):
    weapon: SubWeapon

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        weapon = SubWeapon(jc['weapon'])
        del jc['weapon']
        return cls(weapon=weapon, **jc)

@dataclass
class SpecialWeaponIcon(DetectedItem):
    weapon: SpecialWeapon

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        weapon = SpecialWeapon(jc['weapon'])
        del jc['weapon']
        return cls(weapon=weapon, **jc)

@dataclass
class WeaponGauge(DetectedItem):
    sub_icon: SubWeaponIcon
    sp_icon: SpecialWeaponIcon

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        sub = SubWeaponIcon.from_json(jc['sub_icon'])
        sp = SpecialWeaponIcon.from_json(jc['sp_icon'])
        del jc['sub_icon']
        del jc['sp_icon']
        return cls(sub_icon=sub, sp_icon=sp, **jc)
