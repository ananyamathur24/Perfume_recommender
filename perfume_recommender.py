import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import os

# Paths (use raw strings for Windows paths)
BG_IMAGE_PATH = r"C:\\Users\\Ananya Mathur\\.vscode\\Perfume recommendation\\Bg perfume.png"
CSV_PATH = r"C:\\Users\\Ananya Mathur\\.vscode\\Perfume recommendation\\archive (2)\\fra_perfumes.csv"

class PerfumeRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Perfume Recommendation System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Load data
        self.data = pd.read_csv(CSV_PATH)

        # Load background image
        self.bg_image = Image.open(BG_IMAGE_PATH)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image.resize((800, 600)))

        # Create canvas to hold background image
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Survey variables
        self.gender_var = tk.StringVar(value="Any")

        # Start survey
        self.create_survey()

    def create_survey(self):
        # Clear previous widgets
        self.canvas.delete("survey")

        # Start with question 1
        self.current_question = 1
        self.show_question_1()

    def show_question_1(self):
        self.canvas.delete("survey")
        self.canvas.create_text(400, 100, text="What is your preferred perfume gender?", font=("Arial", 16, "bold"), fill="white", tags="survey")

        genders = ["Any", "Male", "Female", "Unisex"]
        y_start = 150
        for i, gender in enumerate(genders):
            rb = ttk.Radiobutton(self.root, text=gender, variable=self.gender_var, value=gender, command=self.show_question_2)
            self.canvas.create_window(400, y_start + i*40, window=rb, tags="survey")

    import ast

    def show_question_2(self):
        self.canvas.delete("survey")
        self.current_question = 2
        self.main_accord_var = tk.StringVar(value="Any")

        self.canvas.create_text(400, 100, text="What is your preferred main accord?", font=("Arial", 16, "bold"), fill="white", tags="survey")

        # Parse 'Main Accords' strings to lists
        def parse_accords(accord_str):
            try:
                return ast.literal_eval(accord_str)
            except:
                return []

        self.data['Parsed Main Accords'] = self.data['Main Accords'].apply(parse_accords)

        # Flatten all accords and get unique accords
        all_accords = set()
        for accords_list in self.data['Parsed Main Accords']:
            for accord in accords_list:
                all_accords.add(accord.lower())

        accords = ["Any"] + sorted(all_accords)

        y_start = 150
        for i, accord in enumerate(accords[:10]):  # Limit to first 10 for UI simplicity
            rb = ttk.Radiobutton(self.root, text=accord, variable=self.main_accord_var, value=accord, command=self.show_recommendations)
            self.canvas.create_window(400, y_start + i*40, window=rb, tags="survey")

    import ast

    def show_recommendations(self):
        self.canvas.delete("survey")
        self.current_question = 3

        gender = self.gender_var.get()
        main_accord = self.main_accord_var.get()

        # Map user gender choice to data gender values
        gender_map = {
            "Male": "for men",
            "Female": "for women",
            "Unisex": "for women and men",
            "Any": None
        }

        mapped_gender = gender_map.get(gender, None)

        # Parse 'Main Accords' strings to lists
        def parse_accords(accord_str):
            try:
                return ast.literal_eval(accord_str)
            except:
                return []

        self.data['Parsed Main Accords'] = self.data['Main Accords'].apply(parse_accords)

        filtered = self.data

        if mapped_gender:
            filtered = filtered[filtered['Gender'].str.contains(mapped_gender, case=False, na=False)]

        if main_accord != "Any":
            filtered = filtered[filtered['Parsed Main Accords'].apply(lambda accords: main_accord.lower() in [a.lower() for a in accords])]

        # Sort by Rating Value descending
        filtered = filtered.sort_values(by='Rating Value', ascending=False)

        self.recommendations = filtered.reset_index(drop=True)
        self.current_recommendation_index = 0

        if self.recommendations.empty:
            self.canvas.create_text(400, 300, text="No perfumes found matching your preferences.", font=("Arial", 16, "bold"), fill="white", tags="survey")
            return

        self.show_recommendation()

    def show_recommendation(self):
        self.canvas.delete("survey")

        perfume = self.recommendations.iloc[self.current_recommendation_index]

        text = f"Name: {perfume['Name']}\n" \
               f"Gender: {perfume['Gender']}\n" \
               f"Rating: {perfume['Rating Value']} ({perfume['Rating Count']} reviews)\n" \
               f"Main Accords: {perfume['Main Accords']}\n" \
               f"Perfumers: {perfume['Perfumers']}\n\n" \
               f"Description:\n{perfume['Description']}"

        self.canvas.create_text(400, 100, text="Recommended Perfume", font=("Arial", 18, "bold"), fill="white", tags="survey")
        self.canvas.create_text(400, 200, text=text, font=("Arial", 12), fill="white", width=700, tags="survey")

        # Navigation buttons
        btn_prev = ttk.Button(self.root, text="Previous", command=self.prev_recommendation)
        btn_next = ttk.Button(self.root, text="Next", command=self.next_recommendation)

        self.canvas.create_window(300, 500, window=btn_prev, tags="survey")
        self.canvas.create_window(500, 500, window=btn_next, tags="survey")

    def prev_recommendation(self):
        if self.current_recommendation_index > 0:
            self.current_recommendation_index -= 1
            self.show_recommendation()

    def next_recommendation(self):
        if self.current_recommendation_index < len(self.recommendations) - 1:
            self.current_recommendation_index += 1
            self.show_recommendation()

if __name__ == "__main__":
    root = tk.Tk()
    app = PerfumeRecommenderApp(root)
    root.mainloop()
