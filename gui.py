from __future__ import annotations
import threading, tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from ai_build import build
from ai_provider import OllamaProvider
from ai_schema import to_json

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BlockSmith AI"); self.geometry("900x680"); self.minsize(760,580)
        self.provider=OllamaProvider(); self.plan=None; self._ui(); self.refresh_models()

    def _ui(self):
        root=ttk.Frame(self,padding=18); root.pack(fill="both",expand=True)
        ttk.Label(root,text="BlockSmith AI",font=("Segoe UI",22,"bold")).pack(anchor="w")
        ttk.Label(root,text="Describe a Minecraft pack. Local AI creates the plan; BlockSmith builds the files.",font=("Segoe UI",10)).pack(anchor="w",pady=(2,14))
        top=ttk.Frame(root); top.pack(fill="x")
        ttk.Label(top,text="Platform").pack(side="left")
        self.platform=tk.StringVar(value="Bedrock")
        ttk.Combobox(top,textvariable=self.platform,values=["Bedrock","Java"],state="readonly",width=12).pack(side="left",padx=(6,18))
        ttk.Label(top,text="Ollama model").pack(side="left")
        self.model=tk.StringVar(value="llama3.2"); self.models=ttk.Combobox(top,textvariable=self.model,width=24); self.models.pack(side="left",padx=6)
        ttk.Button(top,text="Refresh",command=self.refresh_models).pack(side="left")
        ttk.Button(top,text="Open Ollama",command=self.open_ollama).pack(side="right")
        ttk.Label(root,text="Pack request").pack(anchor="w",pady=(14,4))
        self.prompt=tk.Text(root,height=7,wrap="word"); self.prompt.pack(fill="x")
        self.prompt.insert("1.0","Make a magic sword called Starfall with 500 durability, 18 damage, a star projectile ability, and a 10 second cooldown.")
        buttons=ttk.Frame(root); buttons.pack(fill="x",pady=10)
        self.plan_btn=ttk.Button(buttons,text="Generate Pack Plan",command=self.generate_plan); self.plan_btn.pack(side="left")
        self.build_btn=ttk.Button(buttons,text="Build Pack",command=self.build_pack,state="disabled"); self.build_btn.pack(side="left",padx=8)
        ttk.Button(buttons,text="Export Plan JSON",command=self.export_plan).pack(side="left")
        ttk.Label(root,text="Plan preview").pack(anchor="w")
        self.preview=tk.Text(root,height=15,wrap="none"); self.preview.pack(fill="both",expand=True,pady=(4,8))
        bottom=ttk.Frame(root); bottom.pack(fill="x")
        ttk.Label(bottom,text="Output").pack(side="left")
        self.output=tk.StringVar(value=str(Path.cwd()/"generated")); ttk.Entry(bottom,textvariable=self.output).pack(side="left",fill="x",expand=True,padx=6)
        ttk.Button(bottom,text="Browse",command=self.choose_output).pack(side="left")
        self.replace=tk.BooleanVar(); ttk.Checkbutton(root,text="Replace existing project",variable=self.replace).pack(anchor="w",pady=(7,0))
        self.status=tk.StringVar(value="Ready — start Ollama and click Refresh."); ttk.Label(root,textvariable=self.status).pack(anchor="w",pady=(7,0))

    def open_ollama(self):
        import webbrowser; webbrowser.open("https://ollama.com/download")

    def refresh_models(self):
        def work():
            try: names=self.provider.models(); self.after(0,lambda:self.models_done(names))
            except Exception: self.after(0,lambda:self.status.set("Ollama not reachable. Install/start Ollama, then click Refresh."))
        threading.Thread(target=work,daemon=True).start()

    def models_done(self,names):
        if names:
            self.models["values"]=names
            if self.model.get() not in names: self.model.set(names[0])
            self.status.set(f"Connected to Ollama — {len(names)} model(s) available.")
        else: self.status.set("Ollama returned no installed models.")

    def generate_plan(self):
        prompt=self.prompt.get("1.0","end").strip()
        if not prompt: messagebox.showerror("BlockSmith AI","Enter a pack request."); return
        self._busy(True,"Asking local AI for a pack plan...")
        def work():
            try:
                plan=OllamaProvider(model=self.model.get().strip() or "llama3.2").generate_plan(prompt,self.platform.get().lower())
                self.after(0,lambda:self.plan_done(plan,None))
            except Exception as exc: self.after(0,lambda:self.plan_done(None,str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def plan_done(self,plan,err):
        self._busy(False,"Plan ready." if plan else "Plan failed.")
        if err: messagebox.showerror("AI plan failed",err); return
        self.plan=plan; self.preview.delete("1.0","end"); self.preview.insert("1.0",to_json(plan)); self.build_btn.configure(state="normal")

    def build_pack(self):
        if not self.plan: return
        self._busy(True,"Building pack files...")
        def work():
            try: result=build(self.plan,Path(self.output.get().strip() or "."),self.replace.get()); self.after(0,lambda:self.build_done(result,None))
            except Exception as exc: self.after(0,lambda:self.build_done(None,str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def build_done(self,result,err):
        self._busy(False,"Build complete." if result else "Build failed.")
        if err: messagebox.showerror("Build failed",err); return
        self.preview.insert("end",f"\n\nBuild output:\n{result}"); messagebox.showinfo("BlockSmith AI",f"Pack generated at:\n{result}")

    def export_plan(self):
        if not self.plan: messagebox.showinfo("BlockSmith AI","Generate a plan first."); return
        path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if path: Path(path).write_text(to_json(self.plan),encoding="utf-8")

    def choose_output(self):
        path=filedialog.askdirectory(title="Choose output folder")
        if path: self.output.set(path)

    def _busy(self,busy,status):
        self.status.set(status); self.plan_btn.configure(state="disabled" if busy else "normal")
        self.build_btn.configure(state="disabled" if busy or not self.plan else "normal")

if __name__=="__main__": App().mainloop()
