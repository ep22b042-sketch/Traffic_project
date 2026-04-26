import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CHANGE THIS FILE NAME
# =========================

FILE_NAME = "anonymized_log"   # put your actual data file name here

# =========================
# COLUMN NAMES FROM README
# =========================
cols = [
    "timestamp", "proto", "sport", "dport", "flow_id",
    "srcIP", "dstIP", "pkts1", "pkts2", "bytes1", "bytes2"
]

# Load space-separated text file
df = pd.read_csv(FILE_NAME, sep=r"\s+", names=cols)

print("Data loaded successfully")
print("Shape:", df.shape)
print(df.head())

# =========================
# FEATURE CREATION
# =========================
df["total_pkts"] = df["pkts1"] + df["pkts2"]
df["total_bytes"] = df["bytes1"] + df["bytes2"]

df["download_heavy"] = df["bytes2"] > df["bytes1"]
df["upload_heavy"] = df["bytes1"] > df["bytes2"]

df["byte_ratio"] = (df["bytes1"] + 1) / (df["bytes2"] + 1)

# Convert timestamp
df["time"] = pd.to_datetime(df["timestamp"], unit="s")

# =========================
# BASIC SUMMARY
# =========================
print("\n===== BASIC SUMMARY =====")
print(df[["total_bytes", "total_pkts", "bytes1", "bytes2"]].describe())

print("\nProtocol counts:")
print(df["proto"].value_counts())

print("\nTop source ports:")
print(df["sport"].value_counts().head(10))

print("\nTop destination ports:")
print(df["dport"].value_counts().head(10))

# =========================
# PART A: APPLICATION INFERENCE
# =========================

# DNS-like: small UDP flows, few packets, port 53 only as supporting evidence
dns_like = df[
    (df["proto"] == 17) &
    (df["total_bytes"] < 300) &
    (df["total_pkts"] <= 4) &
    ((df["sport"] == 53) | (df["dport"] == 53))
]

# Web-like: medium size, download-heavy, often TCP ports 80/443 as support
web_like = df[
    (df["total_bytes"] >= 300) &
    (df["total_bytes"] < 50000) &
    (df["bytes2"] > df["bytes1"])
]

# Streaming/bulk-like: large download-heavy flows
streaming_like = df[
    (df["total_bytes"] >= 100000) &
    (df["bytes2"] > 5 * (df["bytes1"] + 1))
]

print("\n===== APPLICATION-LIKE TRAFFIC =====")
print("DNS-like flows:", len(dns_like))
print("Web-like flows:", len(web_like))
print("Streaming/Bulk-like flows:", len(streaming_like))

print("\nDNS-like sample:")
print(dns_like.head())

print("\nWeb-like sample:")
print(web_like.head())

print("\nStreaming/Bulk-like sample:")
print(streaming_like.head())

# =========================
# PART B: ANOMALY DETECTION
# =========================

print("\n===== ANOMALY CHECKS =====")

# 1. Hosts contacting many destinations
unique_dst = df.groupby("srcIP")["dstIP"].nunique().sort_values(ascending=False)
print("\nTop hosts by unique destinations:")
print(unique_dst.head(10))

# 2. Upload-heavy flows
upload_anomaly = df[df["bytes1"] > 10 * (df["bytes2"] + 1)]
print("\nUpload-heavy flows:", len(upload_anomaly))
print(upload_anomaly.sort_values("bytes1", ascending=False).head(10))

# 3. Largest flows
print("\nLargest flows:")
print(df.sort_values("total_bytes", ascending=False).head(10))

# =========================
# PART C: TRAFFIC CHARACTERIZATION
# =========================

total_bytes = df["total_bytes"].sum()
bytes1_total = df["bytes1"].sum()
bytes2_total = df["bytes2"].sum()

print("\n===== OVERALL TRAFFIC CHARACTERIZATION =====")
print("Total flows:", len(df))
print("Total bytes:", total_bytes)
print("Bytes1 total:", bytes1_total)
print("Bytes2 total:", bytes2_total)

if bytes2_total > bytes1_total:
    print("Overall traffic is download-heavy.")
else:
    print("Overall traffic is upload-heavy.")

small_flows = df[df["total_bytes"] < 300]
large_flows = df[df["total_bytes"] > 100000]

print("Small flows percentage:", 100 * len(small_flows) / len(df))
print("Large flows percentage:", 100 * len(large_flows) / len(df))
print("Large flows byte contribution percentage:",
      100 * large_flows["total_bytes"].sum() / total_bytes)

# =========================
# PLOTS
# =========================

# Plot 1: Flow size distribution
plt.figure()
df["total_bytes"].clip(upper=df["total_bytes"].quantile(0.99)).hist(bins=50)
plt.xlabel("Total bytes per flow")
plt.ylabel("Number of flows")
plt.title("Flow Size Distribution")
plt.savefig("flow_size_distribution.png")
plt.close()

# Plot 2: Traffic over time per minute
traffic_time = df.groupby(pd.Grouper(key="time", freq="1min"))["total_bytes"].sum()

plt.figure()
traffic_time.plot()
plt.xlabel("Time")
plt.ylabel("Total bytes per minute")
plt.title("Traffic Volume Over Time")
plt.tight_layout()
plt.savefig("traffic_over_time.png")
plt.close()

# Plot 3: Top hosts by unique destinations
plt.figure()
unique_dst.head(10).plot(kind="bar")
plt.xlabel("Source IP")
plt.ylabel("Unique destination IPs")
plt.title("Top Hosts by Number of Unique Destinations")
plt.tight_layout()
plt.savefig("top_hosts_unique_destinations.png")
plt.close()

print("\nPlots saved:")
print("1. flow_size_distribution.png")
print("2. traffic_over_time.png")
print("3. top_hosts_unique_destinations.png")