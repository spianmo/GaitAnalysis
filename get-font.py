# 在matplotlib中提供一个方法可以查看我们可以设置的默认字体，先查看一下有哪些可以使用
from matplotlib.font_manager import FontManager
import subprocess

all_fonts = set(f.name for f in FontManager().ttflist)

print('all font list get from matplotlib.font_manager:')
for f in sorted(all_fonts):
    print('\t' + f)
