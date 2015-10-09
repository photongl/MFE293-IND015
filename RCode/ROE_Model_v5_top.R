# ===============================================
# NOTE:
# You can shutdown H2O by typing h2o.shutdown()
# in the R interactive window
# ===============================================

library(h2o)
library(readr)
library(ggplot2)

# ======== Prepare data ==========
pos_neg <- function(x)
{
  if (x < 0){
    "N"
  }
  else{
    "P"
  }
}

# read file
#df <- read.csv("filings-roe-bow.csv")
df <- read.csv("filings-roe-doc2vec.csv")

tickers <- levels(df$Name)
df_final <- data.frame()
for(i in 1:length(tickers))
{
  df_ticker <- df[df$Name==tickers[i], ]
  if (nrow(df_ticker) > 3)
  {
    df_diff_ticker <- df_ticker[2:(nrow(df_ticker) - 1), 4:103] - df_ticker[1:(nrow(df_ticker) - 2), 4:103]
    colnames(df_diff_ticker) <-  sprintf("diff_%s",colnames(df_diff_ticker))
    del_roe <- diff(df_ticker$roe)
    del_roe_1 <- del_roe[2:length(del_roe)]
    sign_del_roe_1 <- as.factor(sapply(del_roe_1, pos_neg))
    roe_1 <- df_ticker$roe[3:nrow(df_ticker)]
    sign_roe_1 <- as.factor(sapply(roe_1, pos_neg))
    df_final <- rbind(df_final, cbind(df_ticker[2:(nrow(df_ticker) - 1), ]
                                      #, df_diff_ticker
                                      #, df_ticker[2:(nrow(df_ticker) - 1), 104:107]
                                      , del_roe = del_roe[1:(length(del_roe)-1)]
                                      , del_roe_1
                                      , roe_1
                                      , sign_roe_1
                                      , sign_del_roe_1))
  }
}
df_final <- df_final[order(df_final$year.quarter, df_final$del_roe_1), ]
quarters <- levels(df_final$year.quarter)
x_train <- c()
for(i in 1:length(quarters))
{
	vec <- which(df_final$year.quarter==quarters[i])
	bottom_third_nrow_for_i <- 0.333*length(vec)
	bottom_third_nrow_for_i <- as.integer(bottom_third_nrow_for_i)
	top_third_nrow_for_i <- 0.667*length(vec)
	top_third_nrow_for_i <- as.integer(top_third_nrow_for_i)
	#if(max_nrow_for_i == 0)
	#{
	#	max_nrow_for_i = 1
	#}
	#print(max_nrow_for_i)
	vec1 <- vec[1: bottom_third_nrow_for_i]
	vec2 <- vec[top_third_nrow_for_i:length(vec)]
	vec_final <- c(vec1,vec2)
	x_train <- c(x_train, vec_final)
}


x_train <- x_train[!is.na(x_train)]

df_mid <- df_final[-x_train,]
df_out <- df_final[x_train,]


# start h2o and set parameters
localh2o = h2o.init(nthreads=-1)
year_start = 2001
year_end = 2013
N <- length(year_start:year_end)
training_auc <- numeric(N*4)
validation_auc <- numeric(N*4)
validation_auc_bm <- numeric(N*4)
err_top <- numeric(N*4)
err_bottom <- numeric(N*4)
err_bm_top <- numeric(N*4)
err_bm_bottom <- numeric(N*4)
indices <- numeric(N*4)

# column indices of predictor and response variables
num_features <- ncol(df_final) - 12
predictors <- c(4:(num_features+3))
predictors_benchmark <- c((num_features+5))
response <- num_features + 11

# walk through the data and collect training and validation metrics
i = 1
for(year in year_start:year_end)
{ 
  # create training and validation sets
  for (quarter in 1:4)
  {
    test_year = year + floor(quarter/4)
    test_quarter = (quarter)%%4+1
    
    index <- sprintf("%s-Q%s", year, quarter)
    indices[i] <- index
    cat(sprintf("Training data upto %s, Test period: %s-Q%s\n", index, test_year, test_quarter))

    #df_train <- df_out[((df_out$date.year + df_out$date.quarter/4) < test_year + test_quarter/4) &
    #                     ((df_out$date.year + df_out$date.quarter/4) > test_year + test_quarter/4 - 1), ]
    df_train <- df_final[((df_final$date.year + df_final$date.quarter/4) < test_year + test_quarter/4), ]
    #df_train <- df_out[((df_out$date.year + df_out$date.quarter/4) < test_year + test_quarter/4), ]
    #df_test <- df_out[df_out$date.year == test_year & df_out$date.quarter == test_quarter, ]
    #df_test <- df_mid[df_mid$date.year == test_year & df_mid$date.quarter == test_quarter, ]
    df_test <- df_final[(df_final$date.year + df_final$date.quarter/4) == test_year + test_quarter/4, ]
    
    # write these out to a file and load in h2o
    training_file <- "filing-roe-training.csv"
    test_file <- "filing-roe-test.csv"
    write.csv(df_train, training_file, row.names=FALSE, quote=FALSE)
    write.csv(df_test, test_file, row.names=FALSE, quote=FALSE)
    
    training.hex = h2o.uploadFile(localh2o, path=training_file, destination_frame="training.hex")
    test.hex = h2o.uploadFile(localh2o, path=test_file, destination_frame="test.hex")
    
    # ========= Train ============
    # train a gradient boosting machine
    fit <- h2o.gbm(seed = 12345
                   , model_id = "filings-gbm-model"
                   , x=predictors   # predictor vars
                   , y=response     # dependent var
                   , ntrees = 40
                   , max_depth = 5
                   , learn_rate = 0.05
                   , nbins = 30
                   , nbins_cat = 8
                   , min_rows = 20
                   , training_frame = training.hex
                   , validation_frame = test.hex)
    
    # train a benchmark gradient boosting machine
    fit_benchmark <- h2o.gbm(seed = 12345
                   , model_id = "filings-gbm-model-bm"
                   , x=predictors_benchmark   # predictor vars
                   , y=response     # dependent var
                   , ntrees = 40
                   , max_depth = 5
                   , learn_rate = 0.05
                   , nbins = 20
                   , nbins_cat = 8
                   , min_rows = 5
                   , training_frame = training.hex
                   , validation_frame = test.hex)
    
    scores <- cbind(as.data.frame(predict(fit, newdata = test.hex))
                    , actual=as.character(df_test$sign_roe_1)
                    , excess_roe = df_test$roe_1)
    scores$predict <- as.character(scores$predict)
    scores_bm <- cbind(as.data.frame(predict(fit_benchmark, newdata = test.hex))
                       , actual=as.character(df_test$sign_roe_1))
    scores_bm$predict <- as.character(scores_bm$predict)
    
    qtile <- 0.333
    scores_bottom <- scores[order(scores$P),][1:(qtile * nrow(scores)), ]
    scores_top <- scores[order(scores$P),][((1 - qtile)*nrow(scores)):(nrow(scores)), ]
    err_bottom[i] <- nrow(scores_bottom[scores_bottom$predict != scores_bottom$actual,]) / nrow(scores_bottom)
    err_top[i] <- nrow(scores_top[scores_top$predict != scores_top$actual,]) / nrow(scores_top)
    cat(sprintf("Median top outperformance detected: %s\n", median(scores_top$excess_roe)))
    cat(sprintf("Median top outperformance misclassified: %s\n", median(scores_top[scores_top$predict != scores_top$actual,]$excess_roe)))
    cat(sprintf("Median bottom outperformance detected: %s\n", median(scores_bottom$excess_roe)))
    
    scores_bm_bottom <- scores_bm[order(scores_bm$P),][1:(qtile * nrow(scores_bm)), ]
    scores_bm_top <- scores_bm[order(scores_bm$P),][((1 - qtile)*nrow(scores_bm)):(nrow(scores_bm)), ]
    err_bm_bottom[i] <- nrow(scores_bm_bottom[scores_bm_bottom$predict != scores_bm_bottom$actual,]) / nrow(scores_bm_bottom)
    err_bm_top[i] <- nrow(scores_bm_top[scores_bm_top$predict != scores_bm_top$actual,]) / nrow(scores_bm_top)  
    
    training_auc[i] <- h2o.auc(fit)
    validation_auc[i] <- h2o.auc(fit, valid=TRUE)
    validation_auc_bm[i] <- h2o.auc(fit_benchmark, valid=TRUE)
    i = i + 1
  }
}

df_plot <- rbind(data.frame(n=1:length(validation_auc), Period=indices, AUC = training_auc, err_top = err_top, err_bottom = err_bottom, type="Training")
                 , data.frame(n=1:length(validation_auc),Period=indices, AUC = validation_auc, err_top = err_top, err_bottom = err_bottom,  type="Validation")
                 , data.frame(n=1:length(validation_auc_bm),Period=indices, AUC = validation_auc_bm, err_top = err_bm_top, err_bottom = err_bm_bottom, type="Validation-BM"))

print(ggplot(df_plot, aes(x=n, y=err_top, color=type)) + 
        geom_line(size=1) + 
        scale_x_continuous(breaks=1:length(err_top), labels=indices) + 
        theme(axis.text.x = element_text(angle = 90, hjust = 1)))

print(ggplot(df_plot, aes(x=n, y=err_bottom, color=type)) + 
        geom_line(size=1) + 
        scale_x_continuous(breaks=1:length(err_bottom), labels=indices) + 
        theme(axis.text.x = element_text(angle = 90, hjust = 1)))
