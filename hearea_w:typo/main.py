from datasets import load_dataset
import pandas as pd

# v1.0 - General Knowledge
ds_general = load_dataset("HAERAE-HUB/HAE_RAE_BENCH_1.0", name="General Knowledge", split="test")
df_general = pd.DataFrame(ds_general)
df_general.to_csv("haerae_general_knowledge.csv", index=False)
print("🩷 General Knowledge 저장 완료!")

# v1.0 - Reading Comprehension
ds_reading = load_dataset("HAERAE-HUB/HAE_RAE_BENCH_1.0", name="Reading Comprehension", split="test")
df_reading = pd.DataFrame(ds_reading)
df_reading.to_csv("haerae_reading_comprehension.csv", index=False)
print("💜 Reading Comprehension 1.0 저장 완료!")

# v1.1 - Reading Comprehension (config 정확히!)
ds_reading_1_1 = load_dataset("HAERAE-HUB/HAE_RAE_BENCH_1.1", name="reading_comprehension", split="test")
df_reading_1_1 = pd.DataFrame(ds_reading_1_1)
df_reading_1_1.to_csv("haerae1.1_reading_comprehension.csv", index=False)
print("💜 Reading Comprehension 1.1 저장 완료!")


df1 = pd.read_csv("haerae_general_knowledge.csv")
df2 = pd.read_csv("haerae_reading_comprehension.csv")
df3 = pd.read_csv("haerae1.1_reading_comprehension.csv")
