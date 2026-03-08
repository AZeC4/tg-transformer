#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import asyncio
import os
import webbrowser


class TGConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram 账号格式转换工具")
        self.root.geometry("600x560")
        self.root.resizable(False, False)

        self.conv_type = tk.StringVar(value="s2t")
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.use_proxy = tk.BooleanVar(value=False)
        self.proxy_ip = tk.StringVar(value="127.0.0.1")
        self.proxy_port = tk.StringVar(value="7890")

        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self.root, padx=15, pady=10)
        main.pack(fill="both", expand=True)

        tk.Label(
            main, text="Telegram 账号格式转换工具", font=("Arial", 15, "bold")
        ).pack(pady=(5, 15))

        # 转换方向
        tf = ttk.LabelFrame(main, text="转换方向", padding=8)
        tf.pack(fill="x", pady=(0, 8))
        ttk.Radiobutton(
            tf,
            text="协议号 → 直登号  (sessions → tdata)",
            variable=self.conv_type,
            value="s2t",
            command=self._on_type_change,
        ).pack(anchor="w")
        ttk.Radiobutton(
            tf,
            text="直登号 → 协议号  (tdata → sessions)",
            variable=self.conv_type,
            value="t2s",
            command=self._on_type_change,
        ).pack(anchor="w", pady=(4, 0))

        # 源文件
        sf = ttk.LabelFrame(main, text="源文件", padding=8)
        sf.pack(fill="x", pady=(0, 8))
        sf.columnconfigure(0, weight=1)

        ttk.Entry(sf, textvariable=self.source_path).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        btn_box = tk.Frame(sf)
        btn_box.grid(row=0, column=1)
        self.src_file_btn = ttk.Button(
            btn_box, text="选择文件", command=self._select_src_file, width=8
        )
        self.src_file_btn.pack(side="left", padx=(0, 3))
        ttk.Button(
            btn_box, text="选择文件夹", command=self._select_src_dir, width=9
        ).pack(side="left")

        self.src_hint = ttk.Label(
            sf,
            text="支持选择单个 .session 文件，或包含多个 .session 文件的文件夹",
            foreground="gray",
        )
        self.src_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        # 输出文件夹
        of = ttk.LabelFrame(main, text="输出文件夹", padding=8)
        of.pack(fill="x", pady=(0, 8))
        of.columnconfigure(0, weight=1)

        ttk.Entry(of, textvariable=self.output_path).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(of, text="浏览", command=self._select_output, width=8).grid(
            row=0, column=1
        )

        # 代理设置
        pf = ttk.LabelFrame(main, text="代理设置", padding=8)
        pf.pack(fill="x", pady=(0, 8))

        ttk.Checkbutton(
            pf,
            text="启用 SOCKS5 代理",
            variable=self.use_proxy,
            command=self._toggle_proxy,
        ).pack(anchor="w")

        self.proxy_row = tk.Frame(pf)
        tk.Label(self.proxy_row, text="IP 地址:").pack(side="left")
        ttk.Entry(self.proxy_row, textvariable=self.proxy_ip, width=18).pack(
            side="left", padx=(5, 20)
        )
        tk.Label(self.proxy_row, text="端口:").pack(side="left")
        ttk.Entry(self.proxy_row, textvariable=self.proxy_port, width=8).pack(
            side="left", padx=5
        )

        # 按钮 + 状态
        self.conv_btn = ttk.Button(
            main, text="  开始转换  ", command=self._start_convert
        )
        self.conv_btn.pack(pady=10)

        self.status_var = tk.StringVar(value="就绪")
        self.status_lbl = tk.Label(
            main, textvariable=self.status_var, fg="gray", font=("Arial", 9)
        )
        self.status_lbl.pack()

        # 自定义广告（蓝色、字号加大、底部留白防遮挡，网站可点击）
        adf = tk.Frame(main)
        adf.pack(pady=(16, 20))
        lb1 = tk.Label(
            adf, text="协议号批发：@xieyihaoautobot",
            fg="#0066cc", font=("Arial", 13), cursor="hand2"
        )
        lb1.pack()
        lb1.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/xieyihaoautobot"))
        lb2 = tk.Label(
            adf, text="电报导航：dianbaodaohang.com",
            fg="#0066cc", font=("Arial", 13), cursor="hand2"
        )
        lb2.pack()
        lb2.bind("<Button-1>", lambda e: webbrowser.open("https://dianbaodaohang.com"))

    # ── 交互逻辑 ──────────────────────────────────────────────────────────

    def _on_type_change(self):
        self.source_path.set("")
        if self.conv_type.get() == "s2t":
            self.src_hint.config(
                text="支持选择单个 .session 文件，或包含多个 .session 文件的文件夹"
            )
            self.src_file_btn.config(state="normal")
        else:
            self.src_hint.config(
                text="选择账号根目录（该目录下应包含 tdata 文件夹）"
            )
            self.src_file_btn.config(state="disabled")

    def _select_src_file(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="选择 Session 文件",
            filetypes=[("Session 文件", "*.session"), ("所有文件", "*.*")],
        )
        if path:
            self.source_path.set(path)

    def _select_src_dir(self):
        title = (
            "选择包含 Session 文件的文件夹"
            if self.conv_type.get() == "s2t"
            else "选择账号根目录（包含 tdata 文件夹）"
        )
        path = filedialog.askdirectory(parent=self.root, title=title)
        if path:
            self.source_path.set(path)

    def _select_output(self):
        path = filedialog.askdirectory(parent=self.root, title="选择输出文件夹")
        if path:
            self.output_path.set(path)

    def _toggle_proxy(self):
        if self.use_proxy.get():
            self.proxy_row.pack(fill="x", pady=(6, 0))
        else:
            self.proxy_row.pack_forget()

    # ── 校验 ──────────────────────────────────────────────────────────────

    def _validate(self):
        src = self.source_path.get().strip()
        out = self.output_path.get().strip()

        if not src:
            messagebox.showerror("输入错误", "请选择源文件/文件夹")
            return False
        if not os.path.exists(src):
            messagebox.showerror("输入错误", f"源路径不存在:\n{src}")
            return False
        if not out:
            messagebox.showerror("输入错误", "请选择输出文件夹")
            return False
        if not os.path.isdir(out):
            messagebox.showerror("输入错误", f"输出路径不是有效文件夹:\n{out}")
            return False

        if self.use_proxy.get():
            if not self.proxy_ip.get().strip():
                messagebox.showerror("输入错误", "请输入代理 IP 地址")
                return False
            try:
                p = int(self.proxy_port.get())
                if not (1 <= p <= 65535):
                    raise ValueError
            except ValueError:
                messagebox.showerror("输入错误", "代理端口无效，请输入 1-65535 的整数")
                return False
        return True

    def _get_proxy(self):
        if not self.use_proxy.get():
            return None
        try:
            import socks  # PySocks
            return (socks.SOCKS5, self.proxy_ip.get().strip(), int(self.proxy_port.get()))
        except ImportError:
            messagebox.showerror(
                "依赖缺失", "使用 SOCKS5 代理需要 PySocks 库:\npip install PySocks"
            )
            return "error"

    # ── 转换入口 ──────────────────────────────────────────────────────────

    def _start_convert(self):
        if not self._validate():
            return
        proxy = self._get_proxy()
        if proxy == "error":
            return

        self.conv_btn.config(state="disabled")
        self._set_status("转换中，请稍候...", "blue")
        threading.Thread(target=self._run, args=(proxy,), daemon=True).start()

    def _run(self, proxy):
        self._patch_opentele_userid()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            msg = loop.run_until_complete(self._convert(proxy))
            loop.close()
            self.root.after(0, lambda: self._done(msg))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self._error(err))

    async def _convert(self, proxy):
        if self.conv_type.get() == "s2t":
            return await self._sessions_to_tdata(proxy)
        return await self._tdata_to_sessions(proxy)

    # ── sessions → tdata ──────────────────────────────────────────────────

    async def _sessions_to_tdata(self, proxy):
        try:
            from opentele.tl import TelegramClient
            from opentele.api import API, UseCurrentSession
        except ImportError:
            raise ImportError("缺少 opentele 库\n请运行: pip install opentele")

        src = self.source_path.get()
        out = self.output_path.get()

        if os.path.isfile(src):
            session_files = [src]
        else:
            session_files = [
                os.path.join(src, f)
                for f in os.listdir(src)
                if f.endswith(".session") and os.path.isfile(os.path.join(src, f))
            ]

        if not session_files:
            raise FileNotFoundError("未找到 .session 文件，请确认选择了正确的路径")

        sem = asyncio.Semaphore(3)

        async def convert_one(sf):
            async with sem:
                name = os.path.splitext(os.path.basename(sf))[0]
                session_name = sf[:-8] if sf.endswith(".session") else sf
                try:
                    client = TelegramClient(
                        session_name, api=API.TelegramDesktop, proxy=proxy
                    )
                    await client.connect()
                    tdesk = await client.ToTDesktop(flag=UseCurrentSession)
                    tdesk.SaveTData(os.path.join(out, name, "tdata"))
                    await client.disconnect()
                    return (name, None)
                except Exception as e:
                    return (name, str(e))

        results = await asyncio.gather(*[convert_one(sf) for sf in session_files])
        ok = sum(1 for _, err in results if err is None)
        fails = [f"  {n}: {e}" for n, e in results if e is not None]
        msg = f"共 {len(session_files)} 个账号，成功转换 {ok} 个"
        if fails:
            msg += "\n\n失败列表:\n" + "\n".join(fails)
        return msg

    def _get_tdata_path(self, account_root):
        """opentele 的 basePath 要传 tdata 文件夹路径（其下直接有 key_datas），不是账号根。"""
        tdata_dir = os.path.join(account_root, "tdata")
        if not os.path.isdir(tdata_dir):
            return None
        for name in ("key_data", "key_datas"):
            if os.path.isfile(os.path.join(tdata_dir, name)):
                return tdata_dir
        return None

    def _collect_tdata_roots(self, src):
        """收集所有账号根目录（含 tdata 的目录或含 tdata 的子目录）。"""
        if not os.path.isdir(src):
            return []
        roots = []
        tdata_inside = os.path.join(src, "tdata")
        if os.path.isdir(tdata_inside):
            roots.append(src)
            return roots
        for name in os.listdir(src):
            sub = os.path.join(src, name)
            if os.path.isdir(sub) and os.path.isdir(os.path.join(sub, "tdata")):
                roots.append(sub)
        return roots

    # ── tdata → sessions ──────────────────────────────────────────────────

    @staticmethod
    def _patch_opentele_userid():
        """部分 tdata 反序列化后 UserId 为 None，导致 writeInt64 报错，此处兜底。"""
        try:
            import opentele.td.account as _acc
            _serialize = _acc.Account.serializeMtpAuthorization
            def _serialize_safe(self):
                uid = getattr(self, "_Account__UserId", None)
                if uid is None:
                    setattr(self, "_Account__UserId", 0)
                return _serialize(self)
            _acc.Account.serializeMtpAuthorization = _serialize_safe
        except Exception:
            pass

    async def _tdata_to_sessions(self, proxy):
        try:
            from opentele.td import TDesktop
            from opentele.api import CreateNewSession
        except ImportError:
            raise ImportError("缺少 opentele 库\n请运行: pip install opentele")
        src = self.source_path.get().rstrip("/\\")
        out = self.output_path.get()

        account_roots = self._collect_tdata_roots(src)
        if not account_roots:
            raise FileNotFoundError(
                "未找到有效 tdata 目录\n请选择账号根目录（内含 tdata 文件夹），或包含多个此类子目录的文件夹"
            )

        sem = asyncio.Semaphore(3)

        async def convert_one(account_root):
            async with sem:
                tdata_path = self._get_tdata_path(account_root)
                if tdata_path is None:
                    return (os.path.basename(account_root), "tdata 内无 key_data/key_datas")
                tdesk = TDesktop(tdata_path)
                if not tdesk.isLoaded():
                    return (os.path.basename(account_root), "tdata 加载失败")
                name = os.path.basename(account_root.rstrip("/\\")) or "output"
                session_out = os.path.join(out, name)
                try:
                    client = await tdesk.ToTelethon(
                        session_out, flag=CreateNewSession, proxy=proxy
                    )
                    await client.connect()
                    await client.disconnect()
                    return (name, None)
                except Exception as e:
                    return (name, str(e))

        results = await asyncio.gather(*[convert_one(r) for r in account_roots])
        ok = sum(1 for _, err in results if err is None)
        fails = [f"  {n}: {e}" for n, e in results if e is not None]
        msg = f"共 {len(account_roots)} 个账号，成功转换 {ok} 个"
        if fails:
            msg += "\n\n失败列表:\n" + "\n".join(fails)
        return msg

    # ── 结果回调 ──────────────────────────────────────────────────────────

    def _done(self, msg):
        self.conv_btn.config(state="normal")
        self._set_status("转换成功，已全部完成", "green")
        self._bring_front()
        messagebox.showinfo("转换成功", msg, parent=self.root)

    def _error(self, msg):
        self.conv_btn.config(state="normal")
        self._set_status("转换失败", "red")
        self._bring_front()
        messagebox.showerror("转换错误", msg, parent=self.root)

    def _bring_front(self):
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))

    def _set_status(self, text, color="gray"):
        self.status_var.set(text)
        self.status_lbl.config(fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = TGConverterApp(root)
    root.mainloop()
