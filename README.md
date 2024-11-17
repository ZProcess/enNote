# 打包成win10 exe应用的步骤
1. pyinstaller --onefile --windowed your_script.py
# 修改spec 文件
2.datas=[('notes/', 'notes'), ('notes.db', '.')],
# 再次打包
pyinstaller your_script.spec