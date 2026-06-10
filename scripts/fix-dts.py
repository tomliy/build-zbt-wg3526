import sys

target = sys.argv[1]

with open(target) as f:
    content = f.read()

# Fix pcie1 first: change EEPROM offset to 0x0000, remove 5GHz freq-limit
# Physical pcie1 has MT7603EN (2.4G chip), needs 2.4G calibration at factory 0x0000
old = '\t\tmediatek,mtd-eeprom = <&factory 0x8000>;\n\t\tieee80211-freq-limit = <5000000 6000000>;'
new = '\t\tmediatek,mtd-eeprom = <&factory 0x0000>;'
if old in content:
    content = content.replace(old, new, 1)
    print('Fixed pcie1: 0x8000 -> 0x0000, removed freq-limit')
else:
    print('WARNING: pcie1 pattern not found!')

# Fix pcie0: change EEPROM offset to 0x8000, add 5GHz freq-limit
# Physical pcie0 has MT7662 (5G chip), needs 5G calibration at factory 0x8000
old = '\t\tmediatek,mtd-eeprom = <&factory 0x0000>;\n\t};\n};\n\n&pcie1'
new = '\t\tmediatek,mtd-eeprom = <&factory 0x8000>;\n\t\tieee80211-freq-limit = <5000000 6000000>;\n\t};\n};\n\n&pcie1'
if old in content:
    content = content.replace(old, new, 1)
    print('Fixed pcie0: 0x0000 -> 0x8000, added freq-limit')
else:
    print('WARNING: pcie0 pattern not found!')

with open(target, 'w') as f:
    f.write(content)
print('DTS fixed: ' + target)
