import tkinter as tk
from tkinter import messagebox, Button
import csv
import os
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

DATA_DIR = "data"
LOG_DIR = "log"
CHART_DIR = "charts"

SUMMARY_CSV = os.path.join(DATA_DIR, "roblox_players.csv")
BACKUP_LOG = os.path.join(LOG_DIR, "backup_log.csv")
CHART_AGE = os.path.join(CHART_DIR, "age_groups_chart.png")
CHART_VC = os.path.join(CHART_DIR, "vc_usage_chart.png")

# Create folders if they don't exist
for folder in [DATA_DIR, LOG_DIR, CHART_DIR]:
    os.makedirs(folder, exist_ok=True)


class RobloxTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Player Statistics")
        self.root.geometry("850x900")
        self.root.resizable(True, True)

        # Green Theme (I suck at color picking, it's messy but it's green so that's my aesthetic)
        self.theme = {
            "bg": "#626F47",
            "fg": "#F5ECD5",
            "entry_bg": "#ACC572",
            "entry_fg": "#537D5D",
            "btn_bg": "#ACC572",
            "btn_fg": "#537D5D",
            "stats_bg": "#ACC572",
            "stats_fg": "#537D5D",
            "log_fg": "#537D5D",
        }

        self.root.configure(bg=self.theme["bg"])

        # Load data
        self.entries = self.load_from_backup()

        self.setup_widgets()
        self.update_stats()
        self.update_log()

    def setup_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title
        title = tk.Label(main_frame, text="Roblox Player Tracker", font=("Helvetica", 16, "bold"), bg=self.theme["bg"], fg=self.theme["fg"])
        title.pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Enter Player Age:", font=("Helvetica", 12), bg=self.theme["bg"], fg=self.theme["fg"]).pack(side=tk.LEFT)
        self.age_entry = tk.Entry(input_frame, width=10, font=("Helvetica", 12), bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        self.age_entry.pack(side=tk.LEFT, padx=5)

        self.age_entry.bind('<KeyPress>', self.on_key_press)

        self.btn_no_vc = Button(input_frame, text="Add (w/o VC)", command=lambda: self.add_entry(False), bg=self.theme["btn_bg"], fg=self.theme["btn_fg"], font=("Helvetica", 10))
        self.btn_no_vc.pack(side=tk.LEFT, padx=5)

        self.btn_yes_vc = Button(input_frame, text="Add (w/ VC)", command=lambda: self.add_entry(True), bg=self.theme["btn_bg"], fg=self.theme["btn_fg"], font=("Helvetica", 10))
        self.btn_yes_vc.pack(side=tk.LEFT, padx=5)

        # Action Buttons
        action_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        action_frame.pack(pady=5)

        self.btn_save = Button(action_frame, text="Save Data", command=self.save_all, bg="#5a9a5a", fg="white", font=("Helvetica", 10))
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.btn_charts = Button(action_frame, text="Generate Charts", command=self.generate_charts, bg="#3a7a3a", fg="white", font=("Helvetica", 10))
        self.btn_charts.pack(side=tk.LEFT, padx=5)

        self.btn_exit = Button(action_frame, text="Exit", command=self.save_and_exit, bg="#a03a3a", fg="white", font=("Helvetica", 10))
        self.btn_exit.pack(side=tk.LEFT, padx=5)

        # Statistics
        tk.Label(main_frame, text="Statistics", font=("Helvetica", 12, "bold"), bg=self.theme["bg"], fg=self.theme["fg"]).pack(anchor="w", padx=10)
        self.stats_text = tk.Text(
            main_frame,
            wrap="word",
            height=32, 
            width=95,
            font=("Courier", 10),
            bg=self.theme["stats_bg"],
            fg=self.theme["stats_fg"]
        )
        self.stats_text.pack(padx=10, pady=5)

        # Log Box
        tk.Label(main_frame, text="Recent Entries (Log)", font=("Helvetica", 12, "bold"), bg=self.theme["bg"], fg=self.theme["fg"]).pack(anchor="w", padx=10)
        self.log_text = tk.Text(
            main_frame,
            wrap="none",
            height=8,
            width=95,
            font=("Courier", 10),
            bg=self.theme["stats_bg"],
            fg=self.theme["log_fg"]
        )
        self.log_text.pack(padx=10, pady=5)

        # Focus
        self.age_entry.focus()

    def on_key_press(self, event):
        if event.keysym in ('Return', 'KP_Enter'):
            messagebox.showinfo("Hold On", "Please use 'Add (w/ VC)' or 'Add (No VC)' buttons to ensure VC status is recorded.")
            return "break"

    def load_from_backup(self):
        entries = []
        if not os.path.exists(BACKUP_LOG):
            messagebox.showinfo("Fresh Start", "No previous data found. Starting fresh.")
            return []

        try:
            with open(BACKUP_LOG, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        entry = {
                            "age": int(row["Age"]),
                            "vc": row["VC"] == "Yes",
                            "timestamp": row["Timestamp"]
                        }
                        entries.append(entry)
                    except (ValueError, KeyError):
                        continue
            if entries:
                messagebox.showinfo("Data Loaded", f"✅ Loaded {len(entries)} entries from backup.")
        except Exception as e:
            messagebox.showerror("Load Failed", f"Could not read backup log:\n{str(e)}")
        return entries

    def add_entry(self, has_vc):
        user_input = self.age_entry.get().strip()
        if not user_input:
            return
        try:
            age = int(user_input)
            if age < 0 or age > 120:
                messagebox.showwarning("Invalid Age", "Please enter a valid age between 0 and 120.")
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vc_str = "Yes" if has_vc else "No"

            file_exists = os.path.exists(BACKUP_LOG)
            with open(BACKUP_LOG, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Age", "VC", "Timestamp"])
                writer.writerow([age, vc_str, timestamp])

            self.entries.append({"age": age, "vc": has_vc, "timestamp": timestamp})
            self.age_entry.delete(0, tk.END)
            self.update_stats()
            self.update_log()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a number.")

    def update_stats(self):
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", self.generate_stats_report())
        self.stats_text.config(state="disabled")

    def generate_stats_report(self):
        if not self.entries:
            return "No data yet. Enter players to see stats.\n"

        total = len(self.entries)
        last = self.entries[-1]

        age_data = defaultdict(lambda: {"total": 0, "vce": 0, "vcd": 0})
        for e in self.entries:
            age = e["age"]
            age_data[age]["total"] += 1
            if e["vc"]:
                age_data[age]["vce"] += 1
            else:
                age_data[age]["vcd"] += 1

        sorted_ages = sorted(age_data.items(), key=lambda x: x[1]["total"], reverse=True)
        top_3 = ", ".join(str(a) for a, _ in sorted_ages[:3])

        young = sum(1 for e in self.entries if 6 <= e["age"] <= 12)
        teen = sum(1 for e in self.entries if 13 <= e["age"] <= 17)
        adult = sum(1 for e in self.entries if e["age"] >= 18)

        vc_yes = sum(1 for e in self.entries if e["vc"])
        vc_no = total - vc_yes
        vc_percent = (vc_yes / total) * 100 if total else 0

        report = [
            f"TOTAL PLAYERS: {total}",
            "="*95,
            "",
            f"TOP 3 MOST COMMON AGES: {top_3}",
            "",
            f"LAST ENTRY: Age {last['age']} | VC: {'Yes' if last['vc'] else 'No'} | {last['timestamp']}",
            "",
            "VOICE CHAT USAGE:",
            f"  With VC:  {vc_yes}",
            f"  Without:  {vc_no}",
            f"  Percent:  {vc_percent:.1f}%",
            "",
            "AGE GROUPS:",
            f"  6–12 years old (Young):     {young}",
            f"  13–17 years old (Teens):    {teen}",
            f"  18+ years old (Adults):     {adult}",
            "",
            "="*95,
            "FULL BREAKDOWN BY AGE:",
        ]

        for age, data in sorted(age_data.items()):
            report.append(f"  {age} yrs old – {data['total']} players | w/ VC: {data['vce']} | w/o VC: {data['vcd']}")

        report.append("="*95)
        return "\n".join(report)

    def update_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)

        recent = self.entries[-50:]
        for entry in reversed(recent):
            vc_status = "Yes" if entry["vc"] else "No"
            line = f"{entry['age']:>3} | {vc_status:>3} | {entry['timestamp']}\n"
            self.log_text.insert("1.0", line)

        self.log_text.config(state="disabled")

    def save_all(self):
        if not self.entries:
            messagebox.showwarning("No Data", "No entries to save.")
            return

        age_data = defaultdict(lambda: {"total": 0, "vce": 0, "vcd": 0})
        for e in self.entries:
            age_data[e["age"]]["total"] += 1
            if e["vc"]:
                age_data[e["age"]]["vce"] += 1
            else:
                age_data[e["age"]]["vcd"] += 1

        try:
            os.makedirs(os.path.dirname(SUMMARY_CSV), exist_ok=True)
            with open(SUMMARY_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Age", "Players", "VCE", "VCD"])
                for age in sorted(age_data.keys()):
                    d = age_data[age]
                    writer.writerow([age, d["total"], d["vce"], d["vcd"]])
            messagebox.showinfo("Saved", f"Summary saved to:\n{SUMMARY_CSV}")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save summary:\n{str(e)}")

    def generate_charts(self):
        if not self.entries:
            messagebox.showwarning("No Data", "No data to chart.")
            return

        # Age Groups Pie Chart
        labels_age = ['6–12 (Young)', '13–17 (Teens)', '18+ (Adults)']
        sizes_age = [
            sum(1 for e in self.entries if 6 <= e["age"] <= 12),
            sum(1 for e in self.entries if 13 <= e["age"] <= 17),
            sum(1 for e in self.entries if e["age"] >= 18)
        ]
        colors_age = ['#d0e8d0', '#a8d8a8', '#80c880']
        plt.figure(figsize=(6, 6))
        plt.pie(sizes_age, labels=labels_age, colors=colors_age, autopct='%1.1f%%', startangle=90)
        plt.title("Player Age Distribution")
        plt.savefig(CHART_AGE, dpi=150, bbox_inches='tight')
        plt.close()

        # VC Usage Pie Chart
        vc_yes = sum(1 for e in self.entries if e["vc"])
        vc_no = len(self.entries) - vc_yes
        labels_vc = ['With Voice Chat', 'Without Voice Chat']
        sizes_vc = [vc_yes, vc_no]
        colors_vc = ['#a8e8a8', '#e8a8a8']
        plt.figure(figsize=(6, 6))
        plt.pie(sizes_vc, labels=labels_vc, colors=colors_vc, autopct='%1.1f%%', startangle=90)
        plt.title("Voice Chat Usage")
        plt.savefig(CHART_VC, dpi=150, bbox_inches='tight')
        plt.close()

        messagebox.showinfo("Charts Generated", f"Pie charts saved to:\n{CHART_DIR}/")

    def save_and_exit(self):
        self.save_all()
        self.root.quit()
        self.root.destroy()


# --- Run the App ---
if __name__ == "__main__":
    try:
        import matplotlib
    except ImportError:
        messagebox.showerror("Missing Library", "Please install matplotlib:\n\npip install matplotlib")
        exit()

    root = tk.Tk()
    app = RobloxTracker(root)
    root.mainloop()