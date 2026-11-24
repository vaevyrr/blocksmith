from __future__ import annotations
import threading, tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from ai_build import build
from ai_provider import OllamaProvider
from ai_schema import to_json
from local_setup import ollama_ready, installed_models, setup_local_ai, SetupError

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BlockSmith AI"); self.geometry("940x710"); self.minsize(780,600)
        self.provider=OllamaProvider(); self.plan=None; self._ui()
        self.after(250, self.check_setup)

    def _ui(self):
        root=ttk.Frame(self,padding=18); root.pack(fill="both",expand=True)
        ttk.Label(root,text="BlockSmith AI",font=("Segoe UI",22,"bold")).pack(anchor="w")
        ttk.Label(root,text="Create Minecraft packs with a private, local AI model.",font=("Segoe UI",10)).pack(anchor="w",pady=(2,12))
        setup=ttk.LabelFrame(root,text="Local AI setup",padding=10); setup.pack(fill="x")
        modelrow=ttk.Frame(setup); modelrow.pack(fill="x")
        ttk.Label(modelrow,text="Model").pack(side="left")
        self.model=tk.StringVar(value="llama3.2:3b")
        self.models=ttk.Combobox(modelrow,textvariable=self.model,width=25)
        self.models.pack(side="left",padx=8)
        self.setup_btn=ttk.Button(modelrow,text="Install / Set up local AI",command=self.start_setup)
        self.setup_btn.pack(side="left")
        ttk.Button(modelrow,text="Refresh",command=self.refresh_models).pack(side="left",padx=6)
        self.setup_status=tk.StringVar(value="Checking Ollama...")
        ttk.Label(setup,textvariable=self.setup_status).pack(anchor="w",pady=(8,0))
        ttk.Label(root,text="Platform").pack(anchor="w",pady=(14,4))
        self.platform=tk.StringVar(value="Bedrock")
        ttk.Combobox(root,textvariable=self.platform,values=["Bedrock","Java"],state="readonly",width=14).pack(anchor="w")
        ttk.Label(root,text="What should BlockSmith make?").pack(anchor="w",pady=(12,4))
        self.prompt=tk.Text(root,height=6,wrap="word"); self.prompt.pack(fill="x")
        self.prompt.insert("1.0","Make a magic sword called Starfall with 500 durability, 18 damage, a star projectile ability, and a 10 second cooldown.")
        buttons=ttk.Frame(root); buttons.pack(fill="x",pady=10)
        self.plan_btn=ttk.Button(buttons,text="Generate Pack Plan",command=self.generate_plan); self.plan_btn.pack(side="left")
        self.build_btn=ttk.Button(buttons,text="Build Pack",command=self.build_pack,state="disabled"); self.build_btn.pack(side="left",padx=8)
        ttk.Button(buttons,text="Export Plan JSON",command=self.export_plan).pack(side="left")
        ttk.Label(root,text="Plan preview").pack(anchor="w")
        self.preview=tk.Text(root,height=13,wrap="none"); self.preview.pack(fill="both",expand=True,pady=(4,8))
        bottom=ttk.Frame(root); bottom.pack(fill="x")
        ttk.Label(bottom,text="Output").pack(side="left")
        self.output=tk.StringVar(value=str(Path.cwd()/"generated")); ttk.Entry(bottom,textvariable=self.output).pack(side="left",fill="x",expand=True,padx=6)
        ttk.Button(bottom,text="Browse",command=self.choose_output).pack(side="left")
        self.replace=tk.BooleanVar(); ttk.Checkbutton(root,text="Replace existing project",variable=self.replace).pack(anchor="w",pady=(7,0))
        self.status=tk.StringVar(value="Ready."); ttk.Label(root,textvariable=self.status).pack(anchor="w",pady=(7,0))

    def check_setup(self):
        def work():
            try:
                ready=ollama_ready()
                names=installed_models() if ready else []
                self.after(0,lambda:self._setup_checked(ready,names))
            except Exception:
                self.after(0,lambda:self._setup_checked(False,[]))
        threading.Thread(target=work,daemon=True).start()

    def _setup_checked(self,ready,names):
        if ready:
            self.models["values"]=names
            if names and self.model.get() not in names: self.model.set(names[0])
            self.setup_status.set(f"Ollama connected — {len(names)} model(s) installed." if names else "Ollama is installed. Click Install / Set up local AI to download a model.")
        else:
            self.setup_status.set("Ollama is not installed or not running. Click Install / Set up local AI.")

    def refresh_models(self):
        self.check_setup()

    def start_setup(self):
        model=self.model.get().strip()
        if not model:
            messagebox.showerror("BlockSmith AI","Enter a model name first."); return
        if not messagebox.askyesno("Set up local AI",f"BlockSmith will download the official Ollama installer if needed, then download model '{model}'.\n\nThe model can require several GB of disk space. Continue?"):
            return
        self.setup_btn.configure(state="disabled")
        self.setup_status.set("Starting local AI setup...")
        def progress(message):
            self.after(0,lambda:self.setup_status.set(message))
        def work():
            try:
                setup_local_ai(model,progress)
                self.after(0,lambda:self.setup_finished(None))
            except Exception as exc:
                self.after(0,lambda:self.setup_finished(str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def setup_finished(self,error):
        self.setup_btn.configure(state="normal")
        if error:
            self.setup_status.set("Setup needs attention.")
            messagebox.showerror("Local AI setup failed",error)
            return
        self.setup_status.set("Local AI is ready.")
        self.check_setup()

    def generate_plan(self):
        if not ollama_ready():
            messagebox.showwarning("Local AI not ready","Install/start Ollama and download a model first."); return
        prompt=self.prompt.get("1.0","end").strip()
        if not prompt: messagebox.showerror("BlockSmith AI","Enter a pack request."); return
        self._busy(True,"Asking local AI for a pack plan...")
        def work():
            try:
                plan=OllamaProvider(model=self.model.get().strip()).generate_plan(prompt,self.platform.get().lower())
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
