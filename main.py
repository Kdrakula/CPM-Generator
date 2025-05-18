import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

class CPMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPM Diagram Generator")

        # Lista czynności: (start_event, end_event, duration)
        self.activities = []
        self.current_edit_index = None
        self.activity_counter = 0  # A, B, C, ...
        self.canvas = None  # do wykresu

        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("Name", "Start Event", "End Event", "Duration"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Start Event", text="Start Event")
        self.tree.heading("End Event", text="End Event")
        self.tree.heading("Duration", text="Duration")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=5)

        tk.Label(entry_frame, text="Name").grid(row=0, column=0)
        tk.Label(entry_frame, text="Start").grid(row=0, column=1)
        tk.Label(entry_frame, text="End").grid(row=0, column=2)
        tk.Label(entry_frame, text="Duration").grid(row=0, column=3)

        self.name_entry = tk.Entry(entry_frame, width=10)
        self.name_entry.grid(row=1, column=0)

        self.start_entry = tk.Entry(entry_frame, width=10)
        self.start_entry.grid(row=1, column=1)

        self.end_entry = tk.Entry(entry_frame, width=10)
        self.end_entry.grid(row=1, column=2)

        self.duration_entry = tk.Entry(entry_frame, width=10)
        self.duration_entry.grid(row=1, column=3)

        tk.Button(entry_frame, text="Add Activity", command=self.add_activity).grid(row=1, column=4, padx=5)
        tk.Button(entry_frame, text="Edit Activity", command=self.edit_activity).grid(row=1, column=5, padx=5)
        tk.Button(entry_frame, text="Update Activity", command=self.update_activity).grid(row=1, column=6, padx=5)
        tk.Button(entry_frame, text="Delete Activity", command=self.delete_activity).grid(row=1, column=7, padx=5)
        tk.Button(entry_frame, text="Generate CPM", command=self.generate_cpm).grid(row=3, column=4, padx=5)
        tk.Button(entry_frame, text="Save CSV", command=self.save_csv).grid(row=2, column=4, padx=5)
        tk.Button(entry_frame, text="Load CSV", command=self.load_csv).grid(row=2, column=5, padx=5)

    def add_activity(self):
        name = self.name_entry.get().strip()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        duration = self.duration_entry.get().strip()

        if not start.isdigit() or not end.isdigit() or not duration.isdigit():
            messagebox.showerror("Error", "Start event, end event and duration must be integers")
            return

        if not name:
            name = chr(ord('A') + self.activity_counter)
            self.activity_counter += 1

        start = int(start)
        end = int(end)
        duration = int(duration)

        if end <= start:
            messagebox.showerror("Error", "End event must be greater than start event")
            return

        self.activities.append((name, start, end, duration))
        self.tree.insert('', 'end', values=(name, start, end, duration))
        self.clear_entries()

    def edit_activity(self):
        selected = self.tree.selection()
        if not selected or len(selected) != 1:
            messagebox.showwarning("Warning", "Please select exactly one activity to edit")
            return

        item = selected[0]
        values = self.tree.item(item, 'values')

        self.name_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

        self.name_entry.insert(0, values[0])
        self.start_entry.insert(0, values[1])
        self.end_entry.insert(0, values[2])
        self.duration_entry.insert(0, values[3])

        for i, act in enumerate(self.activities):
            if act == (values[0], int(values[1]), int(values[2]), int(values[3])):
                self.current_edit_index = i
                break

    def update_activity(self):
        if self.current_edit_index is None:
            messagebox.showwarning("Warning", "No activity is currently being edited")
            return

        name = self.name_entry.get().strip()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        duration = self.duration_entry.get().strip()

        if not start.isdigit() or not end.isdigit() or not duration.isdigit():
            messagebox.showerror("Error", "Start event, end event and duration must be integers")
            return

        start = int(start)
        end = int(end)
        duration = int(duration)

        if end <= start:
            messagebox.showerror("Error", "End event must be greater than start event")
            return

        self.activities[self.current_edit_index] = (name, start, end, duration)
        self.current_edit_index = None

        self.tree.delete(*self.tree.get_children())
        for act in self.activities:
            self.tree.insert('', 'end', values=act)

        self.clear_entries()

    def delete_activity(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No activity selected")
            return
        for item in selected:
            values = self.tree.item(item, 'values')
            self.activities = [act for act in self.activities if act != (values[0], int(values[1]), int(values[2]), int(values[3])) ]
            self.tree.delete(item)

    def generate_cpm(self):
        G = nx.DiGraph()

        # Wierzchołki - zdarzenia, krawędzie - czynności z wagą czas trwania
        for name, start, end, duration in self.activities:
            G.add_node(start)
            G.add_node(end)
            G.add_edge(start, end, name=name, duration=duration)

        try:
            topo_order = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            messagebox.showerror("Error", "Cycle detected in activities graph")
            return

        # Earliest start times dla zdarzeń
        earliest_start = {node:0 for node in G.nodes}
        for node in topo_order:
            for pred in G.predecessors(node):
                est = earliest_start[pred] + G.edges[pred, node]['duration']
                if est > earliest_start[node]:
                    earliest_start[node] = est

        max_time = max(earliest_start.values())

        # Latest finish times dla zdarzeń
        latest_finish = {node:max_time for node in G.nodes}
        for node in reversed(topo_order):
            for succ in G.successors(node):
                lft = latest_finish[succ] - G.edges[node, succ]['duration']
                if lft < latest_finish[node]:
                    latest_finish[node] = lft

        # Slack (zapas czasu) = latest_finish - earliest_start
        slack = {node: latest_finish[node] - earliest_start[node] for node in G.nodes}

        # Przechowaj ES, LF i Slack w węzłach (atrybuty)
        for node in G.nodes:
            G.nodes[node]['ES'] = earliest_start[node]
            G.nodes[node]['LF'] = latest_finish[node]
            G.nodes[node]['Slack'] = slack[node]

        # Krytyczna ścieżka: czynności, których najwcześniejszy start = najpóźniejszy finish dla zdarzeń
        critical_edges = []
        for name, start, end, duration in self.activities:
            es = earliest_start[start]
            lf = latest_finish[end] - duration
            if es == lf:
                critical_edges.append((start, end))

        self.show_graph(G, critical_edges)

    def show_graph(self, G, critical_edges):
        fig, ax = plt.subplots(figsize=(8,6))

        pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR")
        node_colors = ['skyblue' for _ in G.nodes]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, ax=ax)
        # nx.draw_networkx_labels(G, pos, ax=ax)
        # Tworzymy etykiety z ES, LF i Slack
        node_labels = {
            node: f"{node}\nES:{G.nodes[node]['ES']}    LF:{G.nodes[node]['LF']}\nSlack:{G.nodes[node]['Slack']}"
            for node in G.nodes
        }
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, ax=ax)

        # Krawędzie z podziałem na krytyczne i niekrytyczne
        edge_colors = []
        for u, v in G.edges:
            if (u,v) in critical_edges:
                edge_colors.append('red')
            else:
                edge_colors.append('gray');

        edge_labels = {(u, v): f"{G.edges[u, v]['name']} ({G.edges[u, v]['duration']})" for u, v in G.edges}

        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, ax=ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def save_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Start Event', 'End Event', 'Duration'])
            for act in self.activities:
                writer.writerow(act)

    def load_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.activities.clear()
            self.tree.delete(*self.tree.get_children())
            for row in reader:
                if len(row) != 4:
                    continue
                try:
                    name = row[0]
                    start = int(row[1])
                    end = int(row[2])
                    duration = int(row[3])
                except ValueError:
                    continue
                self.activities.append((name, start, end, duration))
                self.tree.insert('', 'end', values=(name, start, end, duration))

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = CPMApp(root)
    root.mainloop()
