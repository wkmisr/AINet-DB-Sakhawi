# data.json + app_template.html -> ainet_browser.html
import sys
tpl = open('app_template.html', encoding='utf-8').read()
data = open(sys.argv[1] if len(sys.argv) > 1 else 'data.json', encoding='utf-8').read()
assert '__DATA__' in tpl
open('ainet_browser.html', 'w', encoding='utf-8').write(tpl.replace('__DATA__', data, 1))
print('ainet_browser.html written')
