import sys

target = sys.argv[1]

with open(target) as f:
    content = f.read()

# Fix pcie1 first: remove freq-limit, change offset to 0x0000
old = "\t\tmediatek,mtd-eeprom = <&factory 0x8000>;\n\t\tieee80211-freq-limit = <5000000 6000000>;"
new = "\t\tmediatek,mtd-eeprom = <&factory 0x0000>;"
content = content.replace(old, new, 1)

# Fix pcie0: change offset to 0x8000, add freq-limit
old = "\t\tmediatek,mtd-eeprom = <&factory 0x0000>;\n\t};\n};\n\n&pcie1"
new = "\t\tmediatek,mtd-eeprom = <&factory 0x8000>;\n\t\tieee80211-freq-limit = <5000000 6000000>;\n\t};\n};\n\n&pcie1"
content = content.replace(old, new, 1)

with open(target, "w") as f:
    f.write(content)
print("DTS fixed: " + target)
