import sys

target = sys.argv[1]

with open(target) as f:
    lines = f.readlines()

in_pcie0 = False
in_pcie1 = False
pcie0_lines = []
pcie1_lines = []
pcie0_start = -1
pcie1_start = -1

for i, line in enumerate(lines):
    if line.startswith('&pcie0'):
        in_pcie0 = True
        pcie0_start = i
    elif line.startswith('&pcie1'):
        in_pcie0 = False
        in_pcie1 = True
        pcie1_start = i
    elif in_pcie0 and line.strip() == '};':
        pcie0_lines.append(i)
        in_pcie0 = False
    elif in_pcie1 and line.strip() == '};':
        pcie1_lines.append(i)
        in_pcie1 = False

eeprom_pcie0_fixed = False
eeprom_pcie1_fixed = False
compat_pcie0_fixed = False
compat_pcie1_fixed = False

for i, line in enumerate(lines):
    if pcie0_start < i < pcie0_lines[0]:
        # pcie0 has MT7662 (5G) -> should read factory 0x8000
        if 'mediatek,mtd-eeprom = <&factory 0x0000>;' in line:
            lines[i] = line.replace(
                'mediatek,mtd-eeprom = <&factory 0x0000>;',
                'mediatek,mtd-eeprom = <&factory 0x8000>;'
            )
            # Add ieee80211-freq-limit AFTER this line
            indent = line[:len(line) - len(line.lstrip())]
            lines.insert(i + 1, f'{indent}ieee80211-freq-limit = <5000000 6000000>;\n')
            eeprom_pcie0_fixed = True
            print(f'  Line {i+1}: pcie0 EEPROM 0x0000 -> 0x8000, added freq-limit')
        if 'compatible = "pci14c3,7603"' in line:
            lines[i] = line.replace('pci14c3,7603', 'pci14c3,7662')
            compat_pcie0_fixed = True
            print(f'  Line {i+1}: pcie0 compatible 7603 -> 7662')
        if 'ieee80211-freq-limit' in line and pcie1_start > i > pcie0_lines[0]:
            # This shouldn't be in pcie0 after fix, but let's make sure
            pass

    elif pcie1_start > 0 and pcie1_start < i < pcie1_lines[0]:
        # pcie1 has MT7603 (2.4G) -> should read factory 0x0000
        if 'mediatek,mtd-eeprom = <&factory 0x8000>;' in line:
            lines[i] = line.replace(
                'mediatek,mtd-eeprom = <&factory 0x8000>;',
                'mediatek,mtd-eeprom = <&factory 0x0000>;'
            )
            eeprom_pcie1_fixed = True
            print(f'  Line {i+1}: pcie1 EEPROM 0x8000 -> 0x0000')
        if 'compatible = "pci14c3,7662"' in line:
            lines[i] = line.replace('pci14c3,7662', 'pci14c3,7603')
            compat_pcie1_fixed = True
            print(f'  Line {i+1}: pcie1 compatible 7662 -> 7603')
        if 'ieee80211-freq-limit' in line:
            # Remove freq-limit from pcie1 (2.4G doesn't need 5G limit)
            lines[i] = ''
            print(f'  Line {i+1}: removed ieee80211-freq-limit from pcie1')

# Also remove any ieee80211-freq-limit that was in pcie0 before the fix
# (there shouldn't be any, but clean up to be safe)
for i, line in enumerate(lines):
    if pcie0_start < i < pcie0_lines[0]:
        if 'ieee80211-freq-limit' in line and i < pcie0_lines[0]:
            lines[i] = ''
            print(f'  Line {i+1}: cleaned up stray freq-limit in pcie0')

with open(target, 'w') as f:
    f.writelines(lines)

print(f'\nSummary:')
print(f'  pcie0 EEPROM fix: {"YES" if eeprom_pcie0_fixed else "NOT FOUND"}')
print(f'  pcie1 EEPROM fix: {"YES" if eeprom_pcie1_fixed else "NOT FOUND"}')
print(f'  pcie0 compatible fix: {"YES" if compat_pcie0_fixed else "NOT FOUND"}')
print(f'  pcie1 compatible fix: {"YES" if compat_pcie1_fixed else "NOT FOUND"}')

if not eeprom_pcie0_fixed or not eeprom_pcie1_fixed:
    print('\nERROR: EEPROM fix incomplete!')
    sys.exit(1)
else:
    print('\nDTS fixed successfully!')
