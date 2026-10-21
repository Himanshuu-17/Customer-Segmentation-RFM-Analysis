import pandas as pd
# Load the customer transaction dataset
df=pd.read_excel("customer_RFM.xlsx")

#Display the first rows
print(df.head())

#Check dataset dimensions
print("Dataset Shape:",df.shape)

#Check Column name
print("\nColumn Names:")
print(df.columns)

#Check data types and missing Values
print("\nDataset Information:")
df.info()

#Check Missing Values In each Column
print("\nMissing Values:")
print(df.isnull().sum())

#Check dupliactes records
print("\nDuplicate Records:",df.duplicated().sum())

#Chcek invalid quantites 
print("\nZero or Negative Quantities:")
print((df["Quantity"]<=0).sum())

#Check inavlid prices
print("\nZero or Negative Prices:")
print((df["UnitPrice"]<=0).sum())

#Check Order status Distribution
print('\nOrder Status Distribution:')
print(df["OrderStatus"].value_counts())

#Check order date data type
print("\nOrderDate Data Type:")
print(df["OrderDate"].dtype)

#Convert dateData into proper Datetime Format
df["OrderDate"]=pd.to_datetime(df["OrderDate"],errors="coerce")
print("\nUpdated OrderDate Data Type:")
print(df["OrderDate"].dtype)
print("\nInvalid Dates:",df["OrderDate"].isnull().sum())

#Remove records with missing customerID
df=df.dropna(subset=["CustomerID"])

#Check udated Dataset
print("Dataset Shape:",df.shape)
print("Missing CustomerID:",df["CustomerID"].isnull().sum())

#Check inavlid Quantity records 
print("\nInvalid Quantity records:")
print(df[df["Quantity"]<=0][["TransactionID","Quantity","UnitPrice","SalesAmount"]])

#Check Inavlid UnitPrice records 
print("\nInvalid UnitPrice Records:")
print(df[df["UnitPrice"]<=0][["TransactionID","Quantity","UnitPrice","SalesAmount"]])

#Remove records with invalid Qunatity or UnitPrice
df=df[
    (df["Quantity"]>0) &
    (df["UnitPrice"]>0)
]

#Verify Cleaned Data
print("Dataset Shape After Cleaning:",df.shape)
print("Inavlid Quantity:",(df["Quantity"]<=0).sum())
print("Invalid UnitPrice:",(df["UnitPrice"]<=0).sum())

#Check transactions status after cleaning
print("\nOrder Status Distribution:")
print(df["OrderStatus"].value_counts())

#Check Sales amount by order status
print("\nSales Amount by Order Status:")
print(df.groupby("OrderStatus")["SalesAmount"].sum())

#Keep only completed transactions for RFM analysis
rfm_data=df[df["OrderStatus"]=="Completed"].copy()

#Check the filtered dataset
print("\nRFM Dataset Shape :",rfm_data.shape)

print("\nOrder Status in RFM Dataset:")
print(rfm_data["OrderStatus"].value_counts() )

#Count unique customers
print("Unique Customers:",rfm_data["CustomerID"].nunique())

#Count transaction records
print("Transaction Records:",len(rfm_data))

#Count unique orders
print("Unique Orders :",rfm_data["OrderID"].nunique())

#Find each customers last purchase date
last_purchase=rfm_data.groupby("CustomerID")["OrderDate"].max()
print(last_purchase.head())

#Define a fixed snapshot date for RFM analysis
snapshot_date=pd.Timestamp("2026-01-01")

#Calculate the number of days since each customers last purchase.
recency=(snapshot_date - last_purchase).dt.days
print(recency.head())

#Count unique completed orders placed by each customer.
frequency = rfm_data.groupby("CustomerID")["OrderID"].nunique()
print(frequency.head())

#Calculate total spending for each customer.
monetary=rfm_data.groupby("CustomerID")["SalesAmount"].sum()
print(monetary.head())

#Combine RFM metrics into one customer-level
rfm=pd.DataFrame({
    "Recency":recency,
    "Frequency":frequency,
    "Monetary":monetary
})
#Display the first five customer records 
print(rfm.head())

#Assign Recency scores from 1 to 5
rfm["R_Score"]=pd.qcut(
    rfm["Recency"],
    q=5,
    labels=[5,4,3,2,1],
    duplicates="drop"
)
print(rfm[["Recency","R_Score"]].head())

#Assign Frequency Scores from 1 to 5.
rfm["F_Score"]=pd.qcut(
    rfm["Frequency"].rank(method="first"),
    q=5,
    labels=[1,2,3,4,5]
)
print(rfm[["Frequency","F_Score"]].head())

#Assing Monetary Scores: Higher spending gets a higher score
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    q=5,
    labels=[1,2,3,4,5]
)
#check the score 
print(rfm[["Monetary","M_Score"]].head())

#Combine R , F and M score into one RFM Score
rfm["RFM_Score"]=(
    rfm["R_Score"].astype(int).astype(str) + 
    rfm["F_Score"].astype(int).astype(str) +
    rfm["M_Score"].astype(int).astype(str)
)
#Check the final RFM Score
print(rfm[["R_Score","F_Score","M_Score","RFM_Score"]].head())

#Classify customers based on their RFM scores
def segment_customer(row):
    if row["R_Score"]>=4 and row["F_Score"]>=4 and row["M_Score"]>=4:
        return "Champions"
    elif row["F_Score"]>=4 and row["M_Score"]>=3:
        return "Loyal Customers"
    elif row["R_Score"]>=3 and row["F_Score"]>=2:
        return "Potential Loyalists"
    elif row["R_Score"] <=2 and row["F_Score"]>=3:
        return "At Risk"
    else:
        return "Others"
#Apply the segmentation rules to every customer
rfm["Customer_Segment"] = rfm.apply(segment_customer,axis=1)
#Display customers scores and their segments 
print(rfm[["RFM_Score","Customer_Segment"]].head())

#Count customers in each segment 
segment_summary=rfm["Customer_Segment"].value_counts()
print("\nCustomer Segment Summary:")
print(segment_summary)

#Calculate percentage of customers in each segment
segment_percentage=(rfm["Customer_Segment"].value_counts(normalize=True)*100).round(2)
print("\nCustomer Segment Percentage:")
print(segment_percentage)

#Export customer RFM analysis for power BI
#rfm.to_csv("customer_rfm_results.csv")
#Round monetory values two decimal placs
rfm["Monetary"]=rfm["Monetary"].round(2)
rfm.to_csv("customer_rfm_results.csv",index=True,index_label="CustomerID")

print("\nRFM results exported successfully!")

#Verify the exported RFM dataset
print("\nFinal Dataset Shape:",rfm.shape)
print("\nMissing Values:")
print(rfm.isnull().sum())