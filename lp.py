import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


class librarydashboard:
    def __init__(self):
        self.data = None

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

    def generate_report(self):
        if self.data is None:
            print("pls load dataset")
            return None

        print(f"total transactions :{len(self.data)}")
        print(f"unique books: {self.data['Book title'].nunique()}")
        print(f"unique users: {self.data['User id'].nunique()}")
        print(f"top 10 borrow book: {self.data['Book title'].value_counts().head(10)}")

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

    def pie_chart(self):
        if self.data is None:
            print("pls load dataset")
            return None

        genres = self.data["Genre"].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(genres.values, labels=genres.index, autopct="%1.1f%%", startangle=90)
        plt.title("genre distribution")
        plt.show()

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
        plt.xlabel("day")
        plt.ylabel("month")
        plt.show()


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