from AllMethods import *

# 初始化窗口
root = tk.Tk()
root.title("本地笔记本应用")

# 添加列表框显示文件列表
file_list = Listbox(root, width=30, height=15,highlightthickness=1,  # 设置边框的厚度
                         highlightbackground="gray",  # 设置边框背景颜色
                         highlightcolor="gray")
file_list.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

# 文本编辑区
note_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=150, height=50,highlightthickness=1,  # 设置边框的厚度
                         highlightbackground="gray",  # 设置边框背景颜色
                         highlightcolor="gray")
note_text.pack(padx=10, pady=10)
note_text.bind('<KeyRelease>', lambda event: on_text_change(event, note_text, file_list))
note_text.config(state=tk.DISABLED)  # 禁用文本框编辑

# 创建右键菜单
menu = tk.Menu(file_list, tearoff=0)
menu.add_command(label="新增文件", command=lambda: add_new_list(file_list, root))
menu.add_command(label="删除", command=lambda: delete_selected_item(file_list, note_text))
menu.add_command(label="重命名", command=lambda: rename_file(file_list, note_text))
# 绑定右键点击事件
file_list.bind("<Button-3>", lambda event: right_click(event, menu))
file_list.bind('<Button-1>', lambda event: on_list_item_click(event, file_list, note_text))

update_file_list(file_list)

if __name__ == '__main__':
    # 启动事件循环
    root.mainloop()
    # 关闭数据库连接
    closeDb()
