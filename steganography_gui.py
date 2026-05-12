import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import os
from datetime import datetime


class ModernSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SteganoPro - 专业隐写术工具")
        self.root.geometry("950x700")
        self.root.resizable(True, True)
        
        self.original_image_path = ""
        self.watermarked_image_path = ""
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TNotebook', background='#12121a', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#1a1a27', 
                       foreground='#7a7a9a', 
                       padding=[25, 12],
                       font=('Microsoft YaHei UI', 10, 'bold'))
        style.map('TNotebook.Tab', 
                 background=[('selected', '#0f172a')],
                 foreground=[('selected', '#38bdf8')])
        
        style.configure('TFrame', background='#0f172a')
        style.configure('TLabel', background='#0f172a', foreground='#e2e8f0', font=('Microsoft YaHei UI', 9))
        style.configure('TLabelframe', background='#0f172a', foreground='#60a5fa', borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background='#0f172a', foreground='#60a5fa', font=('Microsoft YaHei UI', 9, 'bold'))
        
        style.configure('TButton', 
                       background='#1e40af',
                       foreground='white',
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       borderwidth=0,
                       padding=[15, 8])
        style.map('TButton',
                 background=[('active', '#2563eb'), ('pressed', '#1d4ed8')])
        
        style.configure('Accent.TButton', 
                       background='#0891b2',
                       foreground='white',
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       borderwidth=0,
                       padding=[15, 8])
        style.map('Accent.TButton',
                 background=[('active', '#06b6d4'), ('pressed', '#0891b2')])
        
        style.configure('TEntry', 
                       fieldbackground='#1e293b',
                       foreground='#f1f5f9',
                       borderwidth=1,
                       insertcolor='#38bdf8',
                       bordercolor='#334155')
    
    def text_to_binary(self, text):
        utf8_bytes = text.encode('utf-8')
        binary = ''.join(format(byte, '08b') for byte in utf8_bytes)
        return binary
    
    def binary_to_text(self, binary):
        byte_list = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                byte_list.append(int(byte, 2))
        try:
            text = bytes(byte_list).decode('utf-8')
            return text
        except UnicodeDecodeError:
            try:
                text = bytes(byte_list).decode('gbk')
                return text
            except:
                return ''.join([chr(b) for b in byte_list])
    
    def hide_text(self, image_path, secret_text, output_path):
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = list(img.getdata())
        
        secret_text += '###END###'
        binary_text = self.text_to_binary(secret_text)
        
        if len(binary_text) > len(pixels) * 3:
            raise ValueError("文本过长，选择更大的图片或缩短文本")
        
        new_pixels = []
        binary_index = 0
        
        for pixel in pixels:
            r, g, b = pixel
            
            if binary_index < len(binary_text):
                r = (r & 0xFE) | int(binary_text[binary_index])
                binary_index += 1
            
            if binary_index < len(binary_text):
                g = (g & 0xFE) | int(binary_text[binary_index])
                binary_index += 1
            
            if binary_index < len(binary_text):
                b = (b & 0xFE) | int(binary_text[binary_index])
                binary_index += 1
            
            new_pixels.append((r, g, b))
        
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path, format='PNG')
        return output_path
    
    def extract_text(self, image_path):
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = list(img.getdata())
        
        binary_text = ''
        
        for pixel in pixels:
            r, g, b = pixel
            binary_text += str(r & 1)
            binary_text += str(g & 1)
            binary_text += str(b & 1)
        
        extracted_bytes = bytearray()
        end_mark = '###END###'.encode('utf-8')
        
        for i in range(0, len(binary_text), 8):
            byte = binary_text[i:i+8]
            if len(byte) < 8:
                break
            extracted_bytes.append(int(byte, 2))
            
            if len(extracted_bytes) >= len(end_mark):
                recent_bytes = extracted_bytes[-len(end_mark):]
                if recent_bytes == end_mark:
                    result_bytes = extracted_bytes[:-len(end_mark)]
                    try:
                        return result_bytes.decode('utf-8')
                    except:
                        pass
        
        try:
            return extracted_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return extracted_bytes.decode('gbk')
            except:
                return ''.join([chr(b) for b in extracted_bytes])
    
    def create_gradient_header(self, parent, text):
        header_frame = tk.Frame(parent, bg='#0f172a', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=text, 
                bg='#0f172a', fg='#38bdf8', 
                font=('Microsoft YaHei UI', 18, 'bold')).pack(pady=(25, 0))
        
        return header_frame
    
    def create_widgets(self):
        main_container = tk.Frame(self.root, bg='#0f172a')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_gradient_header(main_container, "◈ SteganoPro 图片隐写术专业工具-by:离恨天网络工作室 lhtnet.com ◈")
        
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.hide_frame = tk.Frame(notebook, bg='#0f172a')
        self.extract_frame = tk.Frame(notebook, bg='#0f172a')
        
        notebook.add(self.hide_frame, text="  🔒  隐藏文字水印  ")
        notebook.add(self.extract_frame, text="  🔓  提取文字水印  ")
        
        self.create_hide_tab()
        self.create_extract_tab()
    
    def create_hide_tab(self):
        main_frame = tk.Frame(self.hide_frame, bg='#0f172a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📷  选择原始图片", font=('Microsoft YaHei UI', 11, 'bold')).pack(anchor=tk.W)
        
        path_frame = tk.Frame(main_frame, bg='#0f172a')
        path_frame.pack(fill=tk.X, pady=(8, 15))
        
        self.hide_path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=self.hide_path_var, 
                              bg='#1e293b', fg='#e2e8f0', insertbackground='#38bdf8',
                              font=('Microsoft YaHei UI', 9), relief='solid', bd=1)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        browse_btn = tk.Button(path_frame, text="📁 浏览", command=self.browse_original_image,
                              bg='#1e40af', fg='white', font=('Microsoft YaHei UI', 9, 'bold'),
                              relief='flat', padx=15, pady=6, cursor='hand2')
        browse_btn.pack(side=tk.RIGHT)
        
        preview_frame = tk.LabelFrame(main_frame, text=" 🖼️ 图片预览 ", 
                                      bg='#0f172a', fg='#60a5fa', 
                                      font=('Microsoft YaHei UI', 10, 'bold'),
                                      bd=1, relief='solid')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        self.hide_preview_label = tk.Label(preview_frame, text="✨ 请选择图片", 
                                          bg='#1e293b', fg='#94a3b8',
                                          font=('Microsoft YaHei UI', 11),
                                          bd=0, relief='flat')
        self.hide_preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="✏️  输入要隐藏的文字内容", font=('Microsoft YaHei UI', 11, 'bold')).pack(anchor=tk.W)
        
        self.secret_text = tk.Text(main_frame, height=5, wrap=tk.WORD,
                                   bg='#1e293b', fg='#f1f5f9', insertbackground='#38bdf8',
                                   font=('Microsoft YaHei UI', 10), relief='solid', bd=1)
        self.secret_text.pack(fill=tk.BOTH, expand=True, pady=(8, 18))
        
        btn_frame = tk.Frame(main_frame, bg='#0f172a')
        btn_frame.pack(fill=tk.X)
        
        hide_btn = tk.Button(btn_frame, text="⚡  执行隐藏水印", command=self.do_hide_text,
                            bg='#0891b2', fg='white', font=('Microsoft YaHei UI', 11, 'bold'),
                            relief='flat', padx=30, pady=10, cursor='hand2')
        hide_btn.pack(side=tk.RIGHT)
    
    def create_extract_tab(self):
        main_frame = tk.Frame(self.extract_frame, bg='#0f172a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📷  选择带水印的图片", font=('Microsoft YaHei UI', 11, 'bold')).pack(anchor=tk.W)
        
        path_frame = tk.Frame(main_frame, bg='#0f172a')
        path_frame.pack(fill=tk.X, pady=(8, 15))
        
        self.extract_path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=self.extract_path_var, 
                              bg='#1e293b', fg='#e2e8f0', insertbackground='#38bdf8',
                              font=('Microsoft YaHei UI', 9), relief='solid', bd=1)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        browse_btn = tk.Button(path_frame, text="📁 浏览", command=self.browse_watermarked_image,
                              bg='#1e40af', fg='white', font=('Microsoft YaHei UI', 9, 'bold'),
                              relief='flat', padx=15, pady=6, cursor='hand2')
        browse_btn.pack(side=tk.RIGHT)
        
        preview_frame = tk.LabelFrame(main_frame, text=" 🖼️ 图片预览 ", 
                                      bg='#0f172a', fg='#60a5fa', 
                                      font=('Microsoft YaHei UI', 10, 'bold'),
                                      bd=1, relief='solid')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        self.extract_preview_label = tk.Label(preview_frame, text="✨ 请选择图片", 
                                            bg='#1e293b', fg='#94a3b8',
                                            font=('Microsoft YaHei UI', 11),
                                            bd=0, relief='flat')
        self.extract_preview_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📋  提取出的文字水印", font=('Microsoft YaHei UI', 11, 'bold')).pack(anchor=tk.W)
        
        self.extracted_text = tk.Text(main_frame, height=5, wrap=tk.WORD, state=tk.DISABLED,
                                     bg='#1e293b', fg='#10b981', insertbackground='#38bdf8',
                                     font=('Microsoft YaHei UI', 10), relief='solid', bd=1)
        self.extracted_text.pack(fill=tk.BOTH, expand=True, pady=(8, 18))
        
        btn_frame = tk.Frame(main_frame, bg='#0f172a')
        btn_frame.pack(fill=tk.X)
        
        extract_btn = tk.Button(btn_frame, text="🔍  提取水印文字", command=self.do_extract_text,
                               bg='#059669', fg='white', font=('Microsoft YaHei UI', 11, 'bold'),
                               relief='flat', padx=30, pady=10, cursor='hand2')
        extract_btn.pack(side=tk.RIGHT)
    
    def browse_original_image(self):
        file_path = filedialog.askopenfilename(
            title="选择原始图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            self.original_image_path = file_path
            self.hide_path_var.set(file_path)
            self.display_image_preview(file_path, self.hide_preview_label)
    
    def browse_watermarked_image(self):
        file_path = filedialog.askopenfilename(
            title="选择带水印的图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            self.watermarked_image_path = file_path
            self.extract_path_var.set(file_path)
            self.display_image_preview(file_path, self.extract_preview_label)
    
    def display_image_preview(self, image_path, label_widget):
        try:
            img = Image.open(image_path)
            max_size = 420
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo, text="", bg='#1e293b')
            label_widget.image = photo
        except Exception as e:
            label_widget.config(text=f"❌ 无法加载图片: {str(e)}", image="")
    
    def do_hide_text(self):
        if not self.original_image_path:
            messagebox.showwarning("提示", "请先选择原始图片！")
            return
        
        secret = self.secret_text.get("1.0", tk.END).strip()
        if not secret:
            messagebox.showwarning("提示", "请输入要隐藏的文字！")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"steganopro_watermark_{timestamp}.png"
        default_dir = os.getcwd()
        default_path = os.path.join(default_dir, default_filename)
        
        try:
            output_path = filedialog.asksaveasfilename(
                title="保存带水印的图片",
                defaultextension=".png",
                initialfile=default_filename,
                initialdir=default_dir,
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
            )
            
            if not output_path:
                output_path = default_path
            
            self.hide_text(self.original_image_path, secret, output_path)
            messagebox.showinfo("成功", f"✅ 水印已成功隐藏！\n📂 保存位置: {output_path}")
            
        except PermissionError:
            try:
                backup_path = default_path
                self.hide_text(self.original_image_path, secret, backup_path)
                messagebox.showwarning(
                    "提示", 
                    "⚠️ 选择的位置没有写入权限，已自动保存到程序当前目录！\n"
                    f"📂 保存位置: {backup_path}"
                )
            except Exception as e2:
                messagebox.showerror("错误", f"❌ 保存失败: {str(e2)}\n请尝试将图片保存到桌面或其他有写入权限的文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"❌ 隐藏水印时出错: {str(e)}")
    
    def do_extract_text(self):
        if not self.watermarked_image_path:
            messagebox.showwarning("提示", "请先选择带水印的图片！")
            return
        
        try:
            result = self.extract_text(self.watermarked_image_path)
            self.extracted_text.config(state=tk.NORMAL)
            self.extracted_text.delete("1.0", tk.END)
            self.extracted_text.insert("1.0", result)
            self.extracted_text.config(state=tk.DISABLED)
            if not result:
                messagebox.showinfo("提示", "ℹ️ 未找到隐藏的水印文字")
            else:
                messagebox.showinfo("成功", "✅ 水印文字提取完成！")
        except Exception as e:
            messagebox.showerror("错误", f"❌ 提取水印时出错: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernSteganographyApp(root)
    root.mainloop()
