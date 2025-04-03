import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import logging

LOG_FILE = "logs.txt"
PDF_REPORT = "log_report.pdf"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

insert_pattern = re.compile(r'Successfully inserted (\d+) documents')
duration_pattern = re.compile(r'duration:(\d+\.\d+)s')
timestamp_pattern = re.compile(r'"asctime": "(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)"')

def parse_logs(file_path):
    records = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error(f"File {file_path} not found")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error when reading a file {file_path}: {e}")
        return pd.DataFrame()

    for i, line in enumerate(lines):
        try:
            insert_match = insert_pattern.search(line)
            if insert_match:
                num_docs = int(insert_match.group(1))
                duration = 0.0
                for j in range(i, min(i+3, len(lines))):
                    d_match = duration_pattern.search(lines[j])
                    if d_match:
                        duration = float(d_match.group(1))
                        break
                ts_match = timestamp_pattern.search(line)
                timestamp = datetime.strptime(ts_match.group(1), "%Y-%m-%d %H:%M:%S,%f") if ts_match else None

                records.append({
                    'timestamp': timestamp,
                    'num_docs': num_docs,
                    'duration_sec': duration
                })
        except Exception as e:
            logger.error(f"String parsing error {i}: {e}")
    return pd.DataFrame(records)

# --- Analysis  ---
def enrich_dataframe(df):
    try:
        df = df[df["duration_sec"] > 0].copy()
        df.sort_values("timestamp", inplace=True)
        df["speed_per_min"] = df["num_docs"] / df["duration_sec"] * 60
        df["rolling_avg"] = df["speed_per_min"].rolling(window=30, min_periods=1).mean()
        df["is_peak"] = df["speed_per_min"] > (df["rolling_avg"] * 1.2)
        df["is_drop"] = df["speed_per_min"] < (df["rolling_avg"] * 0.8)
    except Exception as e:
        logger.error(f"Data enrichment error: {e}")
    return df

# --- Graphing ---
def plot_speed_graph(df):
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(df["timestamp"], df["speed_per_min"], label="Speed", alpha=0.5)
        plt.plot(df["timestamp"], df["rolling_avg"], label="Moving average", linewidth=2)
        plt.scatter(df.loc[df["is_peak"], "timestamp"], df.loc[df["is_peak"], "speed_per_min"], color='green', label='Peak')
        plt.scatter(df.loc[df["is_drop"], "timestamp"], df.loc[df["is_drop"], "speed_per_min"], color='red', label='Falling')
        plt.title("Loading speed (documents/min)")
        plt.xlabel("Time")
        plt.ylabel("Speed")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
    except Exception as e:
        logger.error(f"Error in plotting the graph: {e}")
    return plt

# --- PDF generation ---
def generate_pdf_report(df):
    try:
        with PdfPages(PDF_REPORT) as pdf:
            # Text information
            fig, ax = plt.subplots(figsize=(8.5, 5))
            ax.axis('off')

            total_docs = int(df["num_docs"].sum())
            total_batches = len(df)
            total_sec = df["duration_sec"].sum()
            total_min = total_sec / 60
            min_speed = df["speed_per_min"].min()

            ax.set_title("Document upload report", fontsize=16, fontweight='bold', loc='center')

            text = f"""
            • Total documents uploaded: {total_docs}
            • Number of batches (inserts): {total_batches}
            • Total insertion time: {total_sec:.2f} seconds (≈ {total_min:.2f} minutes)
            • Minimum speed: {min_speed:.2f} documents/minute
            """
            ax.text(0.05, 0.95, text, fontsize=12, verticalalignment='top')
            pdf.savefig(fig)
            plt.close()

            plot_speed_graph(df)
            pdf.savefig()
            plt.close()
    except Exception as e:
        logger.error(f"Error during PDF report generation: {e}")

if __name__ == "__main__":
    df = parse_logs(LOG_FILE)
    if not df.empty:
        enriched_df = enrich_dataframe(df)
        generate_pdf_report(enriched_df)
        logger.info(f"✅ The report is saved in {PDF_REPORT}")
    else:
        logger.warning("No data to process")