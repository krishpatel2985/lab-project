# 📚 Library Transactions Dashboard & Analyzer

A Python-based data analysis and visualization tool that processes library transaction history. It leverages **Pandas**, **NumPy**, **Matplotlib**, and **Seaborn** to clean the raw data, compute library usage metrics, and display insights through interactive plots and reports.

---

Video Explanation : https://drive.google.com/file/d/1hKEeQ1wCzMTsTrJkVx93Nhko2SuTnXPy/view?usp=sharing

---

## 📂 Project Structure

- **`app.py`**: Modern, interactive Streamlit web application featuring dynamic filters, KPI metric cards, interactive Plotly & Matplotlib charts, reader behavior analysis, and loan return calculators.
- **`lp.py`**: The primary Python script containing the `librarydashboard` class, handling core data operations, statistics, and Matplotlib/Seaborn visualizations.
- **`library_transactions.csv`**: The raw transaction dataset containing library records.
- **`requirements.txt`**: Complete dependency specifications for running locally and deploying to Streamlit Community Cloud.
- **`.streamlit/config.toml`**: Sleek modern dark mode UI theme configuration.

---

## 📊 Dataset Schema

The input dataset (`library_transactions.csv`) contains records of book borrowings with the following columns:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `Transaction id` | Text (Object) | A unique identifier for each checkout transaction. | `T0001` |
| `Date(yyyy-mm-dd)` | Date (YYYY-MM-DD) | The date when the book was borrowed. | `2025-12-14` |
| `User id` | Text (Object) | A unique identifier for the library member. | `U1055` |
| `Book title` | Text (Object) | The name of the borrowed book. | `To Kill a Mockingbird` |
| `Genre` | Text (Object) | The category/genre of the book. | `Classic` |
| `Borrowing duration(days)` | Integer | The duration for which the book was borrowed in days. | `14` |

---

## ✨ Features & Functionality

### 1. Interactive Streamlit Web Application (`app.py`)
- **Real-Time Sidebar Filters**: Filter by custom date ranges, genre multi-select, duration sliders, and instant search by book title or member ID.
- **Executive Metric Cards**: Dynamic indicators for Total Loans, Active Readers, Book Variety, Genre Count, Average Duration, and Busiest Weekday.
- **Tabbed Analytics**:
  - **📊 Core Visualizations**: Top 10 borrowed books, genre circulation share (donut), monthly borrowing trends, and month vs weekday activity heatmaps (toggleable between interactive Plotly and classic Matplotlib/Seaborn).
  - **📚 Catalog & Genre Deep Dive**: Loan duration breakdown by genre, dispersion box plots, and complete book popularity leaderboard.
  - **👥 Reader & Member Habits**: Most active members leaderboard, loan length histograms, and reader engagement segmentation.
  - **⏱️ Loan Due Date & Return Calculator**: Dynamic return date scheduler, weekend/busiest-day footfall advisories, and smart book recommendations.
  - **📋 Transaction Explorer & Export**: Searchable data table, official summary report view, and one-click CSV/TXT export.

### 2. Standalone Python Analytics Engine (`lp.py`)
- **Key Metrics & Statistics**: Total transactions, unique users, books, genres, mean/min/max duration, and peak borrowing weekday.
- **Grouped Aggregations (`dac()`)**: Duration counts and means partitioned by genre and user.
- **Static Visualizations**: Top 10 bar chart, monthly trend line, genre pie chart, and Seaborn correlation heatmap.

---

## 🛠️ Installation & Requirements

Ensure you have Python installed, then install all dependencies using `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### Option A: Launch the Interactive Streamlit Web App (Recommended)
```bash
streamlit run app.py
```
*The app will automatically launch in your default browser at `http://localhost:8501` (or next available port).*

### Option B: Run the Standalone Script
```bash
python lp.py
```

---

## 🔍 Code Walkthrough: Block-by-Block Explanation

Below is the step-by-step breakdown of [lp.py](file:///d:/RD/weekly%20task/lab%20project/lp.py).

### 1. Library Imports
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
```
* **`numpy`**: Used for fast numerical operations, such as calculating the mean, maximum, and minimum borrowing duration.
* **`pandas`**: The core library for reading CSVs, converting column data types, filtering records, and performing grouping and aggregations.
* **`matplotlib.pyplot`**: Used to construct standard plots (bar chart, line graph, pie chart) and customize axes, labels, and layouts.
* **`seaborn`**: A statistical visualization library built on top of matplotlib, utilized here to draw an annotated correlation heatmap.
* **`os`**: Used to construct absolute file system paths, ensuring that the script can always find the dataset even when run from another working directory.

---

### 2. Class Definition and Constructor
```python
class librarydashboard:
    def __init__(self):
        self.data = None
```
* Defines the primary container class `librarydashboard`.
* In `__init__`, it initializes `self.data` as `None`. This attribute will hold the loaded dataset as a Pandas DataFrame once the loading method runs.

---

### 3. Data Loading and Preprocessing
```python
    def load_data(self, file_path=None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "library_transactions.csv")

        if not os.path.exists(file_path):
            print("file not found:", file_path)
            return False

        try:
            self.data = pd.read_csv(file_path)
            self.data["Date(yyyy-mm-dd)"] = pd.to_datetime(self.data["Date(yyyy-mm-dd)"], errors="coerce")
            self.data["Borrowing duration(days)"] = pd.to_numeric(self.data["Borrowing duration(days)"], errors="coerce")
            print("dataset loaded")
            print(self.data.head())
            print(self.data.isnull().sum())
            self.data = self.data.dropna()
            print("removed missing values")
            return True
        except Exception as e:
            print("error loading dataset:", e)
            return False
```
* **Dynamic Pathing**: If `file_path` is not provided, the script gets the folder path of the current file using `__file__` and targets the file `library_transactions.csv` in that same folder.
* **Type Conversion**:
  - `pd.to_datetime` parses transaction dates. Any malformed date string is converted to `NaT` (Not a Time) using `errors="coerce"`.
  - `pd.to_numeric` converts borrow durations into floats/ints. Invalid numeric data becomes `NaN`.
* **Cleaning**: `.isnull().sum()` prints the count of empty cells per column, and `self.data.dropna()` drops any row containing `NaN`/`NaT` values to ensure mathematical operations run cleanly.

---

### 4. Basic Statistics Calculation
```python
    def calculate_statistics(self):
        if self.data is None:
            print("pls load dataset")
            return None

        transactions = self.data["Transaction id"]
        userid = self.data["User id"]
        booktitle = self.data["Book title"]
        genre = self.data["Genre"]
        duration = self.data["Borrowing duration(days)"]

        print("Total transactions: ", len(transactions))
        print("unique users: ", userid.nunique())
        print("unique books: ", booktitle.nunique())
        print("unique genres: ", genre.nunique())
        print("average borrowing duration: ", np.mean(duration))
        print("max borrow duration: ", np.max(duration))
        print("min borrow duration: ", np.min(duration))

        busiest_day = self.data["Date(yyyy-mm-dd)"].dt.day_name().value_counts().idxmax()
        print("bussiest day is : ", busiest_day)
```
* Extract columns into descriptive variables.
* Uses `.nunique()` to count unique instances of members, books, and genres.
* Uses NumPy (`np.mean`, `np.max`, `np.min`) to calculate overall borrowing statistics.
* **Busiest Day**: Extracts the weekday string (e.g., `"Monday"`, `"Sunday"`) using the pandas `.dt.day_name()` accessor, counts occurrences of each weekday using `value_counts()`, and returns the highest-frequency weekday using `.idxmax()`.

---

### 5. Interactive Filtering (CLI-based)
```python
    def filter_transactions(self):
        if self.data is None:
            print("pls load dataset")
            return None

        print("1 - filter by genre")
        print("2 - filter by data range")

        choose = input("choose option: ")
        if choose == "1":
            genre = input("enter genre: ").strip()
            result = self.data[self.data["Genre"].str.lower() == genre.lower()]
            print(result)
        elif choose == "2":
            start = pd.to_datetime(input("enter start date (yyyy-mm-dd): "))
            end = pd.to_datetime(input("enter end date (yyyy-mm-dd): "))
            result = self.data[(self.data["Date(yyyy-mm-dd)"] >= start) & (self.data["Date(yyyy-mm-dd)"] <= end)]
            print(result)
        else:
            print("invalid choice")
```
* Prompt the user inside the console to pick a filter type.
* **Option 1**: Performs a case-insensitive match on the `Genre` column using `str.lower()`.
* **Option 2**: Reads two dates, converts them into datetime values, and creates a logical boolean mask (`&`) to extract records falling within that closed interval.

---

### 6. Summary Report Generation
```python
    def generate_report(self):
        if self.data is None:
            print("pls load dataset")
            return None

        print(f"total transactions :{len(self.data)}")
        print(f"unique books: {self.data['Book title'].nunique()}")
        print(f"unique users: {self.data['User id'].nunique()}")
        print(f"top 10 borrow book: {self.data['Book title'].value_counts().head(10)}")
```
* Prints high-level transaction stats.
* `value_counts().head(10)` groups the transaction log by book titles, counts checkouts per book, orders them in descending order, and fetches the top 10.

---

### 7. Aggregation by User and Genre
```python
    def dac(self):
        if self.data is None:
            print("pls load dataset")
            return None

        total = len(self.data)
        print(f"total borrowing is : {total}")
        duration = self.data["Borrowing duration(days)"]
        print(f"average borrowing duration is : {np.mean(duration)} days")

        genre = self.data.groupby("Genre").agg({"Borrowing duration(days)": ["count", "mean"]})
        print(f"borrowing duration by genre: {genre}")

        user = self.data.groupby("User id").agg({"Borrowing duration(days)": ["count", "mean"]})
        print(f"borrowing duration by user: {user}")
```
* **Grouped Aggregations**: Uses `.groupby()` to partition the transactions by a target dimension (`Genre` or `User id`).
* Uses `.agg(...)` to perform multiple aggregates simultaneously on the `Borrowing duration(days)` column: computing the checkout count (`count`) and average rent duration (`mean`) for each group.

---

### 8. Bar Chart Visualization
```python
    def bar_chart(self):
        if self.data is None:
            print("pls load dataset")
            return None

        topbooks = self.data["Book title"].value_counts().head(10)
        plt.figure(figsize=(12, 6))
        plt.bar(topbooks.index, topbooks.values)
        plt.title("Top 10 Borrowed Books")
        plt.xlabel("Book title")
        plt.ylabel("borrow number")
        plt.xticks(rotation=30)
        plt.show()
```
* Extracts the top 10 books.
* Configures a plotting figure window of dimensions 12x6 inches.
* Uses `plt.bar` to plot book titles on the X-axis (`topbooks.index`) and transaction counts on the Y-axis (`topbooks.values`).
* Applies `plt.xticks(rotation=30)` to slant the book names, ensuring text labels remain readable without clipping.

---

### 9. Line Graph Visualization
```python
    def line_graph(self):
        if self.data is None:
            print("pls load dataset")
            return None

        monthly = self.data.copy()
        trend = monthly.groupby(monthly["Date(yyyy-mm-dd)"].dt.to_period("M")).size()
        trend = trend.reset_index(name="count")
        trend["month"] = trend["Date(yyyy-mm-dd)"].astype(str)
        plt.figure(figsize=(12, 6))
        plt.plot(trend["month"], trend["count"])
        plt.title("monthly borrowing trend")
        plt.xlabel("month")
        plt.ylabel("borrow number")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()
```
* **Period Grouping**: Converts datetime values into monthly periods (e.g. `2025-12` instead of `2025-12-14`) via `.dt.to_period("M")`.
* Groups by this period and calls `.size()` to retrieve total monthly transaction counts.
* Converts period objects to standard strings via `.astype(str)` so Matplotlib can render dates sequentially.
* Draws a monthly trend line via `plt.plot()` and runs `plt.tight_layout()` to balance surrounding margins.

---

### 10. Pie Chart Visualization
```python
    def pie_chart(self):
        if self.data is None:
            print("pls load dataset")
            return None

        genres = self.data["Genre"].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(genres.values, labels=genres.index, autopct="%1.1f%%", startangle=90)
        plt.title("genre distribution")
        plt.show()
```
* Groups transactions by `Genre` and sums count values.
* Plots a circular division diagram.
* Formats individual shares using `%1.1f%%` (percentages with 1 decimal digit accuracy) and places slice titles corresponding to genres (`labels=genres.index`).

---

### 11. Heatmap Correlation Visualization
```python
    def heatmap(self):
        if self.data is None:
            print("pls load dataset")
            return None

        temp = self.data.copy()
        temp["Month"] = temp["Date(yyyy-mm-dd)"].dt.strftime("%B")
        temp["Day"] = temp["Date(yyyy-mm-dd)"].dt.day_name()

        heat_data = temp.groupby(["Month", "Day"]).size().unstack().fillna(0).astype(int)
        plt.figure(figsize=(12, 6))
        sns.heatmap(heat_data, cmap="coolwarm", annot=True, fmt="d")
        plt.title("correlation heatmap")
        plt.xlabel("month")
        plt.ylabel("day")
        plt.show()
```
* **Feature Extraction**: Extracts the full word representation of month names (`%B`, e.g., `"December"`) and weekday names.
* **Pivot Matrix**: Combines Month and Day dimensions into a pivot matrix. `.unstack()` reorganizes grouped indices, mapping days to columns and months to rows.
* Renders a color-coded matrix chart. High transaction density shifts towards warm hues, and low density towards cool hues. `annot=True` writes transaction integers (`fmt="d"`) into each intersection cell.

---

### 12. Main Execution Entry Point
```python
def main():
    dashboard = librarydashboard()
    if dashboard.load_data():
        dashboard.calculate_statistics()
        dashboard.generate_report()
        dashboard.dac()
        dashboard.bar_chart()
        dashboard.line_graph()
        dashboard.pie_chart()
        dashboard.heatmap()


if __name__ == "__main__":
    main()
```
* Check if Python execution is direct (`__name__ == "__main__"`).
* Instantiates `librarydashboard()`.
* Calls data loader; if successful, proceeds sequentially to print statistics, reports, and display all Matplotlib and Seaborn graphs.
