import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from collections import deque


class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Pencarian Alumni")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Create search frame
        search_frame = tk.LabelFrame(self, text="Pencarian Alumni")
        search_frame.pack(pady=10)

        # Create university label and entry
        univ_label = tk.Label(search_frame, text="Universitas", font=('Arial', 12))
        univ_label.grid(row=0, column=0, padx=5, pady=5)

        univ_entry = tk.Entry(search_frame, font=('Arial', 12))
        univ_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create field of study label and entry
        bidang_label = tk.Label(search_frame, text="Bidang Keilmuan", font=('Arial', 12))
        bidang_label.grid(row=1, column=0, padx=5, pady=5)

        bidang_entry = tk.Entry(search_frame, font=('Arial', 12))
        bidang_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create search button
        search_button = tk.Button(search_frame, text="Cari", font=('Arial', 12),
                                  command=lambda: self.perform_search(univ_entry.get(), bidang_entry.get()))
        search_button.grid(row=2, columnspan=2, padx=5, pady=5)

    def perform_search(self, university, field_of_study):
        widget_window = tk.Toplevel(self)
        widget_window.title("Hasil Pencarian Alumni")

        frame = tk.Frame(widget_window)
        frame.pack(pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        treeview = ttk.Treeview(frame, yscrollcommand=scrollbar.set)
        treeview.pack(side="left")

        scrollbar.config(command=treeview.yview)

        try:
            # Load data from graph_gui.py
            alumni_graph = AlumniGraph()
            alumni_graph.load_data()

            # Filter data based on university and field of study
            filtered_data = alumni_graph.get_filtered_data(university, field_of_study)

            if not filtered_data.empty:
                treeview["columns"] = filtered_data.columns.tolist()

                for column in filtered_data.columns:
                    treeview.heading(column, text=column)

                for index, row in filtered_data.iterrows():
                    treeview.insert("", "end", text=index, values=row.tolist())

                # Get job recommendations using AlumniGraph class
                recommendations = alumni_graph.get_job_recommendations(university, field_of_study)

                if recommendations:
                    recommendation_message = "Rekomendasi pekerjaan:\n"
                    for recommendation in recommendations:
                        recommendation_message += f"- {recommendation}\n"
                    messagebox.showinfo("Info", recommendation_message)


                else:
                    messagebox.showinfo("Info", "Tidak ada rekomendasi pekerjaan yang sesuai.")

            else:
                messagebox.showinfo("Info", "Tidak ditemukan data untuk universitas dan bidang ilmu tersebut.")

        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")

    def open_hasil_pencarian_widget(self, university, field_of_study):
        widget_window = tk.Toplevel(self)
        widget_window.title("Hasil Pencarian Alumni")

        frame = tk.Frame(widget_window)
        frame.pack(pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        treeview = ttk.Treeview(frame, yscrollcommand=scrollbar.set)
        treeview.pack(side="left")

        scrollbar.config(command=treeview.yview)

        # Load data from graph_gui.py
        alumni_graph = AlumniGraph()
        alumni_graph.load_data()

        # Filter data based on university and field of study
        filtered_data = alumni_graph.get_filtered_data(university, field_of_study)

        if not filtered_data.empty:
            treeview["columns"] = filtered_data.columns.tolist()

            for column in filtered_data.columns:
                treeview.heading(column, text=column)

            for index, row in filtered_data.iterrows():
                treeview.insert("", "end", text=index, values=row.tolist())

        else:
            messagebox.showinfo("Info", "Tidak ditemukan data untuk universitas dan bidang ilmu tersebut.")


class AlumniGraph:
    def __init__(self):
        self.graph = Graph()

    def load_data(self):
        data = {
            'Nama': ['John Doe', 'Jane Smith', 'Michael Johnson'],
            'Universitas': ['UPN Veteran Jatim', 'Universitas Airlangga', 'Institut Teknologi Sepuluh Nopember'],
            'Program Studi': ['Teknik Informatika', 'Manajemen Bisnis', 'Psikologi'],
            'Bidang Keilmuan': ['Data Science', 'Machine Learning', 'Cyber Security'],
            'Pekerjaan': ['Software Engineer', 'Deep Learning Engineer', 'Cyber Security Analyst']
        }

        df = pd.DataFrame(data)
        self.create_graph(df)

    def create_graph(self, data):
        for _, row in data.iterrows():
            nama = row['Nama']
            universitas = row['Universitas']
            prodi = row['Program Studi']
            bidang_keilmuan = row['Bidang Keilmuan']
            pekerjaan = row['Pekerjaan']

            alumni = Alumni(nama, universitas, prodi, bidang_keilmuan, pekerjaan)
            self.graph.add_alumni(alumni)

    def get_filtered_data(self, university, field_of_study):
        alumni_list = self.graph.get_alumni_by_university_field(university, field_of_study)

        if alumni_list:
            data = {
                'Nama': [],
                'Universitas': [],
                'Program Studi': [],
                'Bidang Keilmuan': [],
                'Pekerjaan': []
            }

            for alumni in alumni_list:
                data['Nama'].append(alumni.nama)
                data['Universitas'].append(alumni.universitas)
                data['Program Studi'].append(alumni.prodi)
                data['Bidang Keilmuan'].append(alumni.bidang_keilmuan)
                data['Pekerjaan'].append(alumni.pekerjaan)

            return pd.DataFrame(data)

        else:
            return pd.DataFrame()

    def get_job_recommendations(self, university, field_of_study):
        start_alumni = self.graph.get_start_alumni(university, field_of_study)

        if start_alumni:
            recommendations = []
            queue = deque([(start_alumni, [])])

            while queue:
                current_alumni, path = queue.popleft()

                if current_alumni.pekerjaan not in path:
                    recommendations.append(current_alumni.pekerjaan)

                for neighbor in self.graph.get_neighbors(current_alumni):
                    queue.append((neighbor, path + [current_alumni.pekerjaan]))

            return recommendations

        else:
            return []


class Alumni:
    def __init__(self, nama, universitas, prodi, bidang_keilmuan, pekerjaan):
        self.nama = nama
        self.universitas = universitas
        self.prodi = prodi
        self.bidang_keilmuan = bidang_keilmuan
        self.pekerjaan = pekerjaan


class Graph:
    def __init__(self):
        self.alumni = {}

    def add_alumni(self, alumni):
        self.alumni[alumni.nama] = alumni

    def get_alumni_by_university_field(self, university, field_of_study):
        return [alumni for alumni in self.alumni.values() if
                alumni.universitas == university and alumni.bidang_keilmuan == field_of_study]

    def get_start_alumni(self, university, field_of_study):
        alumni_list = self.get_alumni_by_university_field(university, field_of_study)

        if alumni_list:
            return alumni_list[0]

        else:
            return None

    def get_neighbors(self, alumni):
        neighbors = []

        for other_alumni in self.alumni.values():
            if other_alumni.universitas == alumni.universitas and other_alumni.bidang_keilmuan != alumni.bidang_keilmuan:
                neighbors.append(other_alumni)

        return neighbors


if __name__ == '__main__':
    app = HomePage()
    app.mainloop()

