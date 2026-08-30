**Orders Table EDA** 

**Columns Analysed from master Order Table**  
order\_id
customer\_id                         
customer\_unique\_id                  
order\_status                        
order\_purchase\_timestamp            
order\_approved\_at                  
order\_delivered\_carrier\_date        
order\_delivered\_customer\_date       
order\_estimated\_delivery\_date       
customer\_zip\_code\_prefix            
customer\_city                       
customer\_state                      
review\_score                        
review\_risk\_flag

**Preprocessing and Feature Engineering**

1. After initial cleaning, order\_approved\_at had 14 null values and order\_delivered\_carrier\_date had 1 null values. For replacing them I had calculated the median\_approval\_delay and then substituted it. Null values of columns are replaced by the same strategy.  
2. Created new columns   
   1. approval\_delay\_days=order\_approved\_at-order\_purchase\_timestamp  
   2. shipping\_prep\_days=order\_delivered\_carrier\_date-order\_approved\_at  
   3. transit\_days=order\_delivered\_customer\_date-order\_delivered\_carrier\_date  
   4. total\_delivery\_days=order\_delivered\_customer\_date-order\_purchase\_timestamp  
   5. delivery\_vs\_estimate\_days=order\_delivered\_customer\_date-order\_estimated\_delivery\_date  
   6. Delivered\_late  
   7. Purchase\_year, purchase\_month, purchase\_dow, purchase\_hour

**Outlier Detection and Treatment**

For numerical columns outliers were calculated using IQR and the outliers were capped based on the upper bound and lower bound. The treated outliers were not replaced in place. But separate columns were created for each column with a postfix of capped. This is done to ensure that we do not lose any information and check if outliers contributed to our findings as well.

**Findings and Insights**

1. For Total delivery days the histogram was heavily skewed towards the left. Most of the delivery occurred between 5-15 days. While some of the deliveries were very delayed to even 40 to 50 days.  
   1. There is a strong relationship between customer satisfaction and delivery delays. Low review scores tend to have a  high median delivery days. While high review scores have lesser delivery days  
   2. One possible action could be to improve the delivery pipeline and logistics.   
2. After initial data cleaning, status of delivery was delivered (99.9%) while 0.01% was cancelled.  
3. Most of the orders were from SP state. The SP state had almost 3.5x of the orders compared to second state in terms of number of orders  
4. After plotting the histogram of Review Counts, most of the products were rated as 5\. They were almost more than 50% of the total orders.   
5. It is observed from boxplot that the product which is rated as 4 or 5 has most of the orders delivered before the estimated time of delivery. The orders which are delivered late have an average score of 2.57 while the orders delivered early or on time have an average rating of 4.29. Showing that delivering the order on correct time is also an important aspect of review  
6. Order values had always shown an upward	trend. Showing a spike at the end of the year 2017\.   
7. The organization has always been working to improve the time taken to deliver the order. This is completely visible from the trend.   
8. Correlation Analysis:   
   1. There is a strong correlation between approval\_delay\_days and transit\_days. Showing whenever there is delay in approval it is also a transit delay.

