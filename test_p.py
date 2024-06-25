import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import plotly.express as px      # Need to import
import tabulate
from PIL import Image
import requests
import json


mydb = mysql.connector.connect(host="localhost",user="root",password="password",database="phonepay")  # connecting to server
mycursor = mydb.cursor()

def homepage():
    st.title(':violet[PHONEPE PULSE DATA VISUALISATION]')   # homepage styles and details 
    st.subheader(':violet[Phonepe]:')
    st.write('PhonePe Pulse is a feature offered by the Indian digital payments platform called PhonePe.PhonePe Pulse provides users with insights and trends related to their digital transactions and usage patterns on the PhonePe app.')
    st.subheader(':violet[Phonepe Pulse Data Visualisation]:')
    st.write('Data visualization refers to the graphical representation of data using charts, graphs, and other visual elements to facilitate understanding and analysis in a visually appealing manner.'
            'The goal is to extract this data and process it to obtain insights and information that can be visualized in a user-friendly manner.')
    st.markdown("## :violet[Created By] : Amarnath K")

def analysis():
    st.title(':violet[ANALYSIS]')
    st.subheader('Analysis done on the basis of All India, States, and Top categories between 2018 and 2023')
    select = st.selectbox("Select Analysis Type", ["INDIA", "STATES", "TOP CATEGORIES"])
    if select=='INDIA':  # select drop the options
        tab1, tab2 = st.tabs(["TRANSACTION","USER"])  # select transaction or user to analyze the data
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                year= st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='year') # year selection 
            with col2:
                quater= st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='quater') # Quatar selection
            with col3:
                type= st.selectbox('**Select Transaction type**',
                                            ('Recharge & bill payments', 'Peer-to-peer payments',   # type of payment need to analyze
                                            'Merchant payments', 'Financial Services', 'Others'),key='type')
                # retrieve data from the table in server (aggregrate transaction)
                mycursor.execute(f"SELECT agg_transaction.State, agg_transaction.Transacion_amount FROM phonepay.agg_transaction WHERE Year = '{year}' AND Quater = '{quater}' AND Transacion_type = '{type}';")
                rslt1= mycursor.fetchall()
                rslt1=pd.DataFrame(np.array(rslt1), columns=['State', 'Transaction_amount']) # covert the resultant value into dataframe
                
                #retrieve data from aggregrate transaction table 
                mycursor.execute(f"SELECT agg_transaction.State, agg_transaction.Transacion_count, agg_transaction.Transacion_amount FROM phonepay.agg_transaction WHERE Year = '{year}' AND Quater = '{quater}' AND Transacion_type = '{type}';")
                rslt2= mycursor.fetchall()
                rslt2=pd.DataFrame(np.array(rslt2), columns=['State', 'Transaction_count','Transaction_amount']) # convert the result values into dataframe
                
                #retrieve data from the aggregrate transaction table
                mycursor.execute(f"SELECT SUM(Transacion_amount), AVG(Transacion_amount) FROM phonepay.agg_transaction WHERE Year = '{year}' AND Quater = '{quater}' AND Transacion_type = '{type}';")
                rslt3= mycursor.fetchall()
                rslt3= pd.DataFrame(np.array(rslt3), columns=['Total', 'Average'])
                # retrieve data from the aggregrate transaction table
                mycursor.execute(f"SELECT SUM(Transacion_count), AVG(Transacion_count) FROM phonepay.agg_transaction WHERE Year = '{year}' AND Quater = '{quater}' AND Transacion_type = '{type}';")
                rslt4=mycursor.fetchall()
                rslt4=pd.DataFrame(np.array(rslt4), columns=['Total', 'Average'])
                rslt4= rslt4.set_index(['Average'])
                
                # insert values into geo url
                rslt1.drop(columns=['State'], inplace=True)  # drop the state column . Because geo url also had a state name
                url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"  # Clone the geo data
                response = requests.get(url)   # get the geo url using get function
                data1 = json.loads(response.content)  # load the values 
                state_names_tra = [feature['properties']['ST_NM'] for feature in data1['features']]
                state_names_tra.sort()
                df_statenames = pd.DataFrame({'State': state_names_tra})
                df_statenames['Transaction_amount'] =rslt1 
                #conver dataframe into csv file
                df_statenames.to_csv("Statenames.csv",index=False)
                df_tr=pd.read_csv('Statenames.csv')
                #geo plot
                fig_tra = px.choropleth(
                df_tr,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='Transaction_amount',
                color_continuous_scale='thermal', title='Transactions')
                fig_tra.update_geos(fitbounds="locations", visible=False)
                fig_tra.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
                st.plotly_chart(fig_tra, use_container_width=True)

        #USER
        with tab2:
            col1,col2=st.columns(2)
            with col1:
                us_year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='us_year')
            with col2:
                us_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='us_qtr')
                # retrieve data from aggregrate user table for analyze
                mycursor.execute(f"SELECT State, SUM(Count) FROM agg_user WHERE Year = '{us_year}' AND Quarter = '{us_qtr}' GROUP BY State;")
                us_rslt1 = mycursor.fetchall()
                df_us_rslt1 = pd.DataFrame(np.array(us_rslt1), columns=['State', 'User Count'])
                df_us_rslt1 = df_us_rslt1.set_index(pd.Index(range(1, len(df_us_rslt1) + 1)))

                mycursor.execute(f"SELECT AVG(Count), SUM(Count) FROM agg_user WHERE Year = '{us_year}' AND Quarter = '{us_qtr}';")
                us_rslt2 = mycursor.fetchall()
                df_us_rslt2 = pd.DataFrame(np.array(us_rslt2), columns=['Average', 'Total'])
                df_us_rslt2 = df_us_rslt2.set_index(['Average'])

            
                # drop the state column in dataframe
                df_us_rslt1 .drop(columns=['State'], inplace=True)
                url1 = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"# clone the geo data
                response = requests.get(url1)
                data2 = json.loads(response.content)
                state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
                state_names_use.sort()
                # create the dataframe with geo state name column
                df_state_names_use = pd.DataFrame({'State': state_names_use})
                #combine the geo state name with dataframe
                df_state_names_use['User Count'] = df_us_rslt1
                #convert the data frame into csv
                df_state_names_use.to_csv('State_user.csv', index=False)
                df_use = pd.read_csv('State_user.csv')
                # geo plot
                fig_use = px.choropleth(
                df_use,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='User Count',
                color_continuous_scale='thermal', title='User Analysis')
                fig_use.update_geos(fitbounds="locations", visible=False)
                fig_use.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
                st.plotly_chart(fig_use, use_container_width=True)
                
        #state
    if select == "STATES":
        tab3 ,tab4 = st.tabs(["TRANSACTION","USER"])
        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:                   # for state column need to analyze data for districtwise
                tran_st = st.selectbox('**Select State**', (
                'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                'haryana', 'himachal-pradesh',
                'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                'maharashtra', 'manipur',
                'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                'tamil-nadu', 'telangana',
                'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), key='tran_st')
            with col2:
                tran_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='tran_yr')
            with col3:
                tran_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='tran_qtr')
            # retrieve data from aggregrate transaction for analaysis
            mycursor.execute(f"SELECT agg_transaction.Transacion_type, agg_transaction.Transacion_amount FROM phonepay.agg_transaction WHERE State = '{tran_st}' AND Year = '{tran_yr}' AND Quater = '{tran_qtr}';")
            state_rslt = mycursor.fetchall()
            df_state_rslt = pd.DataFrame(state_rslt,columns=['Transaction_type','Transaction_amount'])
            

            mycursor.execute(f"SELECT agg_transaction.Transacion_type, agg_transaction.Transacion_count, agg_transaction.Transacion_amount FROM phonepay.agg_transaction WHERE State = '{tran_st}' AND Year = '{tran_yr}' AND Quater = '{tran_qtr}';")
            ana_rslt = mycursor.fetchall()
            df_ana_rslt = pd.DataFrame(ana_rslt,columns=['Transaction_type', 'Transaction_count','Transaction_amount'])
            
            
            mycursor.execute(f"SELECT SUM(Transacion_amount), AVG(Transacion_amount) FROM agg_transaction WHERE State = '{tran_st}' AND Year = '{tran_yr}' AND Quater = '{tran_qtr}';")
            st_qry_rslt = mycursor.fetchall()
            df_st_qry_rslt = pd.DataFrame(st_qry_rslt, columns=['Total', 'Average'])
            

            mycursor.execute(f"SELECT SUM(Transacion_count), AVG(Transacion_count) FROM agg_transaction WHERE State = '{tran_st}' AND Year ='{tran_yr}' AND Quater = '{tran_qtr}';")
            st_tr_rslt = mycursor.fetchall()
            df_tr_rslt = pd.DataFrame(st_tr_rslt, columns=['Total', 'Average'])

            df_state_rslt ['Transaction_type'] = df_state_rslt ['Transaction_type'].astype(str)# convert Transaction type into str
            df_state_rslt ['Transaction_amount'] = df_state_rslt ['Transaction_amount'].astype(float)# convert Transaction amount into float

            # bar chart analyse data between transaction type and transaction amount
            df_state_rslt_fig=px.bar(df_state_rslt,x='Transaction_type',y='Transaction_amount',title='Transaction Analysis Chart', height=500)
            df_state_rslt_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_state_rslt_fig, use_container_width=True)
            st.header(':violet[Total calculation]')
            col4, col5 = st.columns(2)
            with col4:
                st.subheader(':violet[Transaction Analysis]')   # dataframe with show dataframe 
                analysis
                st.dataframe(df_ana_rslt)
            with col5:
                st.subheader(':violet[Transaction Amount]')
                st.dataframe(df_st_qry_rslt)
                st.subheader(':violet[Transaction Count]')
                st.dataframe(df_tr_rslt)
            #User Tab for state
        with tab4:
            col6, col7,col8 = st.columns(3)
            with col6:
                st_us_st = st.selectbox('**Select State**', (
                'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                'haryana', 'himachal-pradesh',
                'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                'maharashtra', 'manipur',
                'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                'tamil-nadu', 'telangana',
                'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), key='st_us_st')
            with col7:
                st_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='st_us_yr')
            # retrieve data from aggregrate user table for analysis
            mycursor.execute(f"SELECT Quarter, SUM(Count) FROM phonepay.agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}' Group by Quarter;")
            st_us_tab_rslt = mycursor.fetchall()
            df_us_tab_rslt=pd.DataFrame(st_us_tab_rslt,columns=['Quarter', 'User Count'])

            mycursor.execute(f"SELECT SUM(Count), AVG(Count) FROM phonepay.agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}';")
            st_us_qry_rslt = mycursor.fetchall()
            df_us_qry_rslt =pd.DataFrame(st_us_qry_rslt,columns=['Total','Average'])

            df_us_tab_rslt['Quarter'] = df_us_tab_rslt['Quarter'].astype(int)# data type conversion
            df_us_tab_rslt['User Count'] = df_us_tab_rslt['User Count'].astype(int)# data type conversion
            # bar chart plot for User data
            df_us_tab_rslt_fig = px.bar(df_us_tab_rslt, x='Quarter', y='User Count', title='User Analysis Chart',height=500, )
            df_us_tab_rslt_fig .update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_us_tab_rslt_fig , use_container_width=True)

            st.header(':violet[Total calculation]')
            col9,col10=st.columns(2)
            with col9:
                st.subheader(':violet[User Analysis]')  # dataframe overview
                st.dataframe(df_us_tab_rslt)
            with col10:
                st.subheader(':violet[User Count]')
                st.dataframe(df_us_qry_rslt)
    if select == "TOP CATEGORIES":
        tab5, tab6 = st.tabs(["TRANSACTION", "USER"])  # slect for top categories
        with tab5:
            top_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_tr_yr')
# retrieve data top transaction for analysis
        mycursor.execute(f"SELECT State, SUM(trans_amount) As Transaction_amount FROM phonepay.top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        top_tr_tab_qry_rslt = mycursor.fetchall()
        df_top_tr_tab_qry_rslt = pd.DataFrame(top_tr_tab_qry_rslt,columns=['State', 'Top Transaction amount'])
        
        mycursor.execute(f"SELECT State, SUM(trans_amount) as Transaction_amount, SUM(trans_count) as Transaction_count FROM phonepay.top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        top_tr_anly_tab_qry_rslt =mycursor.fetchall()
        df_top_tr_anly_tab_qry_rslt = pd.DataFrame(top_tr_anly_tab_qry_rslt,columns=['State', 'Top Transaction amount','Total Transaction count'])
        

        df_top_tr_tab_qry_rslt['State'] = df_top_tr_tab_qry_rslt['State'].astype(str)# datatype conversion
        df_top_tr_tab_qry_rslt['Top Transaction amount'] = df_top_tr_tab_qry_rslt['Top Transaction amount'].astype(float)# datatype conversion
#plot bar chart for the analysisng data
        df_top_tr_tab_qry_rslt1_fig = px.bar(df_top_tr_tab_qry_rslt, x='State', y='Top Transaction amount',color='Top Transaction amount', color_continuous_scale='thermal',title='Top Transaction Analysis Chart', height=600, )
        df_top_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
        st.plotly_chart(df_top_tr_tab_qry_rslt1_fig, use_container_width=True)

        st.header(':violet[Total calculation]')
        st.subheader(':violet[Top Transaction Analysis]')
        st.dataframe(df_top_tr_anly_tab_qry_rslt)
#Top user
        with tab6:
            top_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_us_yr')
# retrieve data for analysis 
        mycursor.execute(f"SELECT State, SUM(Registeruser) AS Top_user FROM phonepay.top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10;")
        top_us_tab_qry_rslt = mycursor.fetchall()
        df_top_us_tab_qry_rslt = pd.DataFrame(np.array(top_us_tab_qry_rslt), columns=['State', 'Total User count'])

        df_top_us_tab_qry_rslt['State'] = df_top_us_tab_qry_rslt['State'].astype(str)# data type conversion
        df_top_us_tab_qry_rslt['Total User count'] = df_top_us_tab_qry_rslt['Total User count'].astype(float)# data type conversion
# bar plot for top users
        df_top_us_tab_qry_rslt1_fig = px.bar(df_top_us_tab_qry_rslt, x='State', y='Total User count',color='Total User count', color_continuous_scale='thermal',title='Top User Analysis Chart', height=600, )
        df_top_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
        st.plotly_chart(df_top_us_tab_qry_rslt1_fig, use_container_width=True)

        st.header(':violet[Total calculation]')
        st.subheader(':violet[Total User Analysis]')
        st.dataframe(df_top_us_tab_qry_rslt)
def insights_page():    # These are for insights which measure from the data
    st.title(':violet[BASIC INSIGHTS]')
    st.subheader("The basic insights are derived from the Analysis of the Phonepe Pulse data. It provides a clear idea about the analysed data.")
    options = ["--select--",
            "1. Top 10 states based on year and amount of transaction",
            "2. Least 10 states based on year and amount of transaction",
            "3. Top 10 States and Districts based on Registered_users",
            "4. Least 10 States and Districts based on Registered_users",
            "5. Top 10 Districts based on the Transaction Amount",
            "6. Least 10 Districts based on the Transaction Amount",
            "7. Top 10 Districts based on the Transaction count",
            "8. Least 10 Districts based on the Transaction count",
            "9. Top Transaction types based on the Transaction Amount",
            "10. Top 10 Mobile Brands based on the User count of transaction"]
    select = st.selectbox(":violet[Select the option]",options)

    if select == "1. Top 10 states based on year and amount of transaction":
        mycursor.execute(
            "SELECT DISTINCT State,Year, SUM(trans_amount) AS Total_Transaction_Amount FROM phonepay.top_transaction GROUP BY State,Year ORDER BY Total_Transaction_Amount DESC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'Year', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 states based on amount of transaction")
            first=px.bar(df, x="Transaction_amount", y="States")
            st.plotly_chart(first,use_container_width=True)
    elif select == "2. Least 10 states based on year and amount of transaction":
        mycursor.execute(
            "SELECT DISTINCT State,Year, SUM(trans_amount) as Total FROM phonepay.top_transaction GROUP BY State, Year ORDER BY Total ASC LIMIT 10;")
        data = mycursor.fetchall()
        columns = ['States', 'Year', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns)
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 states based on amount of transaction")
            second=px.bar(df, x="Transaction_amount", y="States")
            st.plotly_chart(second,use_container_width=True)

    elif select == "3. Top 10 States and Districts based on Registered_users":
        mycursor.execute("SELECT DISTINCT State, pincode, SUM(Registeruser) AS Users FROM phonepay.top_user GROUP BY State, Pincode ORDER BY Users DESC LIMIT 10;")
        data = mycursor.fetchall()
        columns = ['State', 'Pincode', 'Registered_users']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 States and Districts based on Registered_users")
            third=px.bar(df, x="Registered_users", y="State")
            st.plotly_chart(third,use_container_width=True)
        
    elif select == "4. Least 10 States and Districts based on Registered_users":
        mycursor.execute("SELECT DISTINCT State, pincode, SUM(Registeruser) AS Users FROM phonepay.top_user GROUP BY State, Pincode ORDER BY Users ASC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['State', 'Pincode', 'Registered_users']
        df = pd.DataFrame(data, columns=columns)
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 States and Districts based on Registered_users")
            fourth=px.bar(df, x="Registered_users", y="State")
            st.plotly_chart(fourth,use_container_width=True)
    elif select == "5. Top 10 Districts based on the Transaction Amount":
        mycursor.execute("SELECT DISTINCT State, District, SUM(amount) AS Total FROM phonepay.map_transaction GROUP BY State, District ORDER BY Total DESC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Amount']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on Transaction Amount")
            fifth=px.bar(df, x="District", y="Amount")
            st.plotly_chart(fifth,use_container_width=True)
    elif select == "6. Least 10 Districts based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT State, District, SUM(amount) AS Total FROM phonepay.map_transaction GROUP BY State, District ORDER BY Total ASC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Amount']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 Districts based on Transaction Amount")
            sixth=px.bar(df, x="District", y="Amount")
            st.plotly_chart(sixth,use_container_width=True)
    elif select == "7. Top 10 Districts based on the Transaction count":
        mycursor.execute(
            "SELECT DISTINCT State, District, SUM(Count) AS Counts FROM phonepay.map_transaction GROUP BY State, District ORDER BY Counts DESC LIMIT 10");
        data =mycursor.fetchall()
        columns = ['States', 'District', 'Count']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on Transaction Count")
            seventh=px.bar(df, x="Count", y="District")
            st.plotly_chart(seventh,use_container_width=True)

    elif select == "8. Least 10 Districts based on the Transaction count":
        mycursor.execute(
            "SELECT DISTINCT State, District, SUM(Count) AS Counts FROM phonepay.map_transaction GROUP BY State, District ORDER BY Counts ASC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Count']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on the Transaction Count")
            eight=px.bar(df, x="Count", y="District")
            st.plotly_chart(eight,use_container_width=True)
            
    elif select == "9. Top Transaction types based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT Transacion_type, SUM(Transacion_amount) AS Amount FROM phonepay.agg_transaction GROUP BY Transacion_type ORDER BY Amount DESC LIMIT 5")
        data = mycursor.fetchall()
        columns = ['Transaction_type', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top Transaction Types based on the Transaction Amount")
            nine=px.bar(df, x="Transaction_type", y="Transaction_amount")
            st.plotly_chart(nine,use_container_width=True)

    elif select == "10. Top 10 Mobile Brands based on the User count of transaction":
        mycursor.execute(
            "SELECT DISTINCT Brand, SUM(Count) as Total FROM phonepay.agg_user GROUP BY Brand ORDER BY Total DESC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['Brands', 'User_Count']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Mobile Brands based on User count of transaction")
            ten=px.bar(df , x="User_Count", y="Brands")
            st.plotly_chart(ten,use_container_width=True)


st.header(" Phonepe Analysis ")
cata=['select','Home','analysis','insights']
select = st.selectbox(":violet[Select the option]",cata)

if select=='Home':
    homepage()
elif select=='analysis':
    analysis()
elif select=='insights':
    insights_page()