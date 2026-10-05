import re

content = open('reports/Presentation.html', encoding='utf-8').read()
matches = re.findall(r'data-speaker="([^"]+)"', content)
print('Total slides verified:', len(matches))
for i, m in enumerate(matches):
    print(f'Slide {i+1:2d}: {m}')
