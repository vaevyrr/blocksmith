from __future__ import annotations
import threading, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from blocksmith import generate

class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title("BlockSmith");self.geometry("720x470");self.minsize(620,420);self.build()
    def build(self):
        outer=ttk.Frame(self,padding=20);outer.pack(fill="both",expand=True)
        ttk.Label(outer,text="BlockSmith",font=("Segoe UI",20,"bold")).pack(anchor="w")
        ttk.Label(outer,text="Generate a paired Minecraft Bedrock behavior/resource pack scaffold.",font=("Segoe UI",10)).pack(anchor="w",pady=(2,20))
        ttk.Label(outer,text="Project name").pack(anchor="w");self.name=tk.StringVar();ttk.Entry(outer,textvariable=self.name).pack(fill="x",pady=(3,14))
        ttk.Label(outer,text="Output folder").pack(anchor="w");r=ttk.Frame(outer);r.pack(fill="x",pady=(3,14));self.output=tk.StringVar();ttk.Entry(r,textvariable=self.output).pack(side="left",fill="x",expand=True);ttk.Button(r,text="Browse",command=self.choose).pack(side="left",padx=6)
        self.force=tk.BooleanVar();ttk.Checkbutton(outer,text="Replace existing generated folders",variable=self.force).pack(anchor="w")
        self.go=ttk.Button(outer,text="Generate Pack",command=self.run);self.go.pack(anchor="w",pady=18)
        self.status=tk.StringVar(value="Ready");ttk.Label(outer,textvariable=self.status).pack(anchor="w")
        self.progress=ttk.Progressbar(outer,mode="indeterminate");self.progress.pack(fill="x",pady=(8,0))
        self.output_text=tk.Text(outer,height=7);self.output_text.pack(fill="both",expand=True,pady=(12,0))
    def choose(self):
        p=filedialog.askdirectory(title="Choose output folder")
        if p:self.output.set(p)
    def run(self):
        if not self.name.get().strip():messagebox.showerror("BlockSmith","Enter a project name.");return
        out=Path(self.output.get() or ".");self.go.configure(state="disabled");self.progress.start(10);self.status.set("Generating...")
        def work():
            try:r=generate(self.name.get().strip(),out,self.force.get());err=None
            except Exception as e:r=None;err=str(e)
            self.after(0,lambda:self.finish(r,err))
        threading.Thread(target=work,daemon=True).start()
    def finish(self,r,err):
        self.progress.stop();self.go.configure(state="normal")
        if err:self.status.set("Failed");messagebox.showerror("Generation failed",err);return
        bp,rp=r;self.status.set("Generation complete");self.output_text.delete("1.0","end");self.output_text.insert("end",f"Behavior pack:\n{bp}\n\nResource pack:\n{rp}\n\nREADME.txt was created in the output folder.")
        messagebox.showinfo("BlockSmith","Pack scaffold generated successfully.")

if __name__=="__main__":App().mainloop()
