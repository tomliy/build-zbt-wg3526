import sys

target = sys.argv[1]

with open(target) as f:
    content = f.read()

# Step 1: Remove pcie0 wifi node entirely
# Physical port 0 has no card, the 2.4G chip is on pcie2
pcie0_block = (
    '&pcie0 {\n'
    '\twifi0: wifi@0,0 {\n'
    '\t\tcompatible = \"pci14c3,7603\";\n'
    '\t\treg = <0x0000 0 0 0 0>;\n'
    '\t\tmediatek,mtd-eeprom = <&factory 0x0000>;\n'
    '\t};\n'
    '};\n'
)

if pcie0_block in content:
    content = content.replace(pcie0_block, '', 1)
    print('Removed pcie0 wifi node (port 0 has no card)')
else:
    print('WARNING: pcie0 wifi block not found!')

# Step 2: Add pcie2 wifi node for the 2.4G chip (MT7603EN on physical port 2)
wifi2_block = (
    '&pcie2 {\n'
    '\twifi0: wifi@0,0 {\n'
    '\t\tcompatible = \"pci14c3,7603\";\n'
    '\t\treg = <0x0000 0 0 0 0>;\n'
    '\t\tmediatek,mtd-eeprom = <&factory 0x0000>;\n'
    '\t};\n'
    '};\n'
)

# Insert after pcie1 block (before &ethernet, NOT inside it)
marker = '&ethernet'
if marker in content:
    content = content.replace(marker, wifi2_block + '\n' + marker, 1)
    print('Added pcie2 wifi node for 2.4G chip')
else:
    print('WARNING: ethernet marker not found!')

with open(target, 'w') as f:
    f.write(content)
print('DTS fixed: ' + target)
