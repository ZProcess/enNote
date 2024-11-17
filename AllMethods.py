from cryptography.fernet import Fernet
from tkinter import scrolledtext, filedialog, Listbox, END, simpledialog, messagebox
import os
import sqlite3
import tkinter as tk

# 初始化数据库连接
conn = sqlite3.connect('notes.db')
cursor = conn.cursor()
# 用于保存选中状态的列表
selectIndex = 0

# 创建数据库表
# 创建一个表来存储文件路径和列表项名称
cursor.execute('''
CREATE TABLE IF NOT EXISTS lists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    filepath TEXT NOT NULL,
    encryption_key TEXT NOT NULL
)
''')
conn.commit()


# 保存新列表项到数据库，并在notes文件夹下创建对应的txt文件
def add_new_list(file_list,root):
    name = simpledialog.askstring("新增文件", "请输入文件名称:",parent=root)
    if name:
        notes_dir = 'notes'
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)
        filepath = os.path.join(notes_dir, f"{name}.txt")
        # 检查文件是否存在
        if os.path.exists(filepath):
            messagebox.showerror("错误", "文件已存在，不能新增。")
        else:
            with open(filepath, 'w') as f:
                f.write("")  # 创建一个空的txt文件
            # 生成唯一的加密密钥
            encryption_key = generate_encryption_key()
            cursor.execute('INSERT INTO lists (name, filepath,encryption_key) VALUES (?, ?,?)',
                           (name, filepath, encryption_key))
            conn.commit()
            update_file_list(file_list)


# 更新文件列表
def update_file_list(file_list):
    cursor.execute('SELECT name FROM lists')
    lists = cursor.fetchall()
    file_list.delete(0, END)
    for list_item in lists:
        file_list.insert(END, list_item[0])


# 在文本编辑区内容改变时更新文件
def on_text_change(event, note_text, file_list):
    global selectIndex
    # 设置列表项为选中状态
    file_list.selection_clear(0, END)  # 清除之前的选中状态
    file_list.selection_set(selectIndex)  # 设置当前项为选中状态
    file_list.activate(selectIndex)  # 激活当前项
    notes_dir = 'notes'
    selection = file_list.curselection()
    list_name = file_list.get(selection)
    current_file_path = os.path.join(notes_dir, f"{list_name}.txt")
    # 执行 SQL 查询来获取与文件名对应的记录
    cursor.execute('SELECT encryption_key FROM lists WHERE name = ?', (list_name,))
    record = cursor.fetchone()
    if current_file_path:
        # 从记录中提取加密密钥
        encryption_key = record[0]
        save_file_content(current_file_path, note_text, encryption_key)

# 保存文本编辑区的内容到文件
def save_file_content(file_path, note_text, key):
    content = note_text.get('1.0', tk.END)
    enText = encrypt_text(content, key)
    # 打印加密后的文本，用于调试
    print("Encrypted text:", enText)
    # 确保enText是字节字符串，然后解码为普通字符串
    if isinstance(enText, bytes):
        enText_str = enText.decode('utf-8')
    else:
        enText_str = enText  # 如果enText已经是普通字符串，则无需解码
    # 确保enText不是None或空字符串
    if enText_str:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(enText_str)
    else:
        print("No content to write, encrypted text is empty or None.")



# 绑定列表项的事件
def on_list_item_click(event, file_list, note_text):
    # 获取鼠标点击位置的索引
    index = file_list.nearest(event.y)
    # 设置列表项为选中状态
    file_list.selection_clear(0, END)  # 清除之前的选中状态
    file_list.selection_set(index)  # 设置当前项为选中状态
    file_list.activate(index)  # 激活当前项
    file_list.focus_set()  # 将焦点设置到列表框上
    global selectIndex
    selectIndex = index
    # 现在可以获取选中的列表项了
    selection = file_list.curselection()
    notes_dir = 'notes'
    if selection:
        note_text.config(state=tk.NORMAL)  # 禁用文本框编辑
        list_name = file_list.get(selection)
        file_path = os.path.join(notes_dir, f"{list_name}.txt")
        # 执行 SQL 查询来获取与文件名对应的记录
        cursor.execute('SELECT encryption_key FROM lists WHERE name = ?', (list_name,))
        record = cursor.fetchone()
        # 从记录中提取加密密钥
        encryption_key = record[0]
        load_file_content(file_path, note_text,encryption_key)
    else:
        note_text.config(state=tk.DISABLED)  # 禁用文本框编辑



# 加载文件内容到编辑器
# 加载文件内容到文本编辑区
def load_file_content(file_path, note_text,key):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        if content:
            content = decrypt_text(content, key)
        note_text.delete('1.0', tk.END)
        note_text.insert(tk.END, content)


# 数据库相关

# 生成秘钥并存储到数据库
def generate_encryption_key():
    """ 生成秘钥并将其存储在数据库中 """
    key = Fernet.generate_key()
    return key


# 加密文本
def encrypt_text(text, key):
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode())
    return encrypted_text


# 解密文本
def decrypt_text(encrypted_text, key):
    f = Fernet(key)
    decrypted_text = f.decrypt(encrypted_text).decode()
    return decrypted_text


def right_click(event, menu):
    menu.tk_popup(event.x_root, event.y_root)

def delete_selected_item(file_list, note_text):
    # 获取当前选中的项
    selected_indices = file_list.curselection()
    if selected_indices:
        # 弹出确认对话框
        if messagebox.askyesno("确认", "您确定要删除这个文件吗？"):
            # 删除列表中的项
            for index in reversed(selected_indices):
                # 获取文件名和文件路径
                item = file_list.get(index)
                cursor.execute('SELECT filepath FROM lists WHERE name = ?', (item,))
                result = cursor.fetchone()
                if result:
                    filepath = result[0]
                    # 删除本地文件
                    try:
                        os.remove(filepath)
                    except OSError as e:
                        print(f"Error: {e.strerror}.")
                    # 删除数据库记录
                    cursor.execute('DELETE FROM lists WHERE name = ?', (item,))
                    conn.commit()
                # 删除列表框中的项
                file_list.delete(index)
            # 清空文本框并禁用
            note_text.delete('1.0', tk.END)
            note_text.config(state=tk.DISABLED)

def closeDb():
    conn.close()