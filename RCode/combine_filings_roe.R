library(readr)
df <- read_csv("FILING_FEATURES_100.csv")
df_roe <- read.csv("clean_excess_roe_sp500.csv")
df_final <- merge(df, df_roe, by.x = c("Name", "year.quarter"), by.y = c("ticker", "year.quarter"))
#df_final <- df_merge#[,]
write.csv(df_final, "filings-roe-doc2vec.csv", quote = FALSE, row.names = FALSE)