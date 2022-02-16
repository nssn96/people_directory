# Name : Surya Narayanan Nadhamuni Suresh
# UTA ID : 1001877873

# References Used:
# useful links
# 1) to upload a file in Azure --> https://www.dotnetfunda.com/articles/show/3466/step-by-step-approach-to-upload-a-text-file-to-azure-blob-storage-usin

# 2) import csv file to myphpadmin --
# https://medium.com/an-idea/import-csv-file-data-into-mysql-table-with-phpmyadmin-96024fc11f5d

# 3) finding hostname from phpmyadmin,
# https://www.milesweb.in/hosting-faqs/about-mysql-hostname-and-ways-to-find-it/#:~:text=After%20opening%20phpMyAdmin%2C%20go%20to%20Server%20information%20from,domain%20or%20IP%20address%20of%20the%20database%20server%3A

# 4) git upload -- > https://www.youtube.com/watch?v=eGaImwD8fPQ
# 5) upload to Azure --> https://www.youtube.com/watch?v=K_RTlbOOCts

# dynamic where clause --> https://www.sqlteam.com/articles/implementing-a-dynamic-where-clause

# https://www.javatpoint.com/html-form

# https://tomlogs.github.io/build-a-photos-application-with-azure-blob-storage

# https://sodocumentation.net/flask/topic/5459/file-uploads#:~:text=Uploaded%20files%20are%20available%20in%20request.files%2C%20a%20MultiDict,a%20common%20directory%20to%20save%20the%20files%20to.

# request objects---> https://www.tutorialspoint.com/flask/flask_request_object.htm
# file uploading ---> https://www.tutorialspoint.com/flask/flask_file_uploading.htm

# https://www.tutorialspoint.com/flask/flask_environment.htm


from flask import Flask, render_template, url_for,request,redirect,flash
import mysql.connector as mysql
from azure.storage.blob import BlobServiceClient




app = Flask(__name__)
app.secret_key = 'random string'

#AZURE  STORAGE DETAILS
AZURE_CONNECTION_STRING ='DefaultEndpointsProtocol=https;AccountName=sxn7873;AccountKey=pRd1n4f7EjkiQRpWhhZNJ6Q9RIVdJQjPDm1bpgjA3IqUF74ziM2CmtfOAyLZfJrzCRrzUA4YNpI0WE7EXeyO6Q==;EndpointSuffix=core.windows.net'


#DB connection details
HOST='utacloud1.reclaimhosting.com'
USER = 'sxn7873_surya'
PASSWORD='Pn2E)^Gq&Dc]'
DATABASE='sxn7873_adb'

#A specific function to set up a db connection
def dbConnect():
    global conn # defining a global variable
    #connect to database
    conn = mysql.connect(host=HOST,user=USER,password=PASSWORD,database=DATABASE)
    return conn

# the main select query
mainQuery = "Select * from people"

#Fuction to return the content of the whole table
def allData():
    dbConnect()
    cursor = conn.cursor()
    cursor.execute(mainQuery)
    res = cursor.fetchall()
    conn.close()
    return res

#Reference used for the dynamic query below
#https://www.sqlteam.com/articles/implementing-a-dynamic-where-clause
#Function to fetch data based on search fields
def searchByField(fields):
    for key,value in fields.items():
        
        query=   "SELECT * FROM people WHERE charm LIKE '%"+value+"%' "
    dbConnect()
    cursor = conn.cursor()

    if fields:

    # if fields:
    #     query+=" where "
    # else:
    #     return allData()
    # flag=0
    # for key,value in fields.items():
    #     if flag > 0:
    #         query += " AND "
    #     query+= " " + key + " = " + "'" +value+"'"
    #     flag+=1
    
    #sending the generated query to DB
        cursor.execute(query)
        res = cursor.fetchall()
        conn.close()
    return res

def deleteByUser(fields):
    query = "Delete  from people where Name LIKE '%"+fields['Name']+"%'"
    dbConnect()
    cursor = conn.cursor()
    #executing the query
    cursor.execute(query)
    #commiting the changes in DB
    conn.commit()
    conn.close()

def updateByUser(fields):
    updateQuery = "Update people SET "
    dbConnect()
    cursor = conn.cursor()
    flag=0
    for key,value in fields.items():
        if key!='oldName':
            if flag>0:
                updateQuery+= " , "
            updateQuery += key + " = '"+ value+"'"
            flag+=1
    updateQuery += " where Name = '"+fields['oldName']+"'"

    #executing the query
    cursor.execute(updateQuery)
    #commiting the changes in DB
    conn.commit()
    conn.close()

def addByUser(fields):
    addQuery = "Insert into people values ( "
    dbConnect()
    cursor = conn.cursor()
    flag=0
    for key,value in fields.items():
        if flag>0:
            addQuery+=" , "
        addQuery+="'"+value+"'"
        flag+=1
    addQuery+=")"
    
    #print(addQuery)

    #executing the query
    cursor.execute(addQuery)
    #commiting the changes in DB
    conn.commit()
    conn.close()

# A BLOB SERVICE CLIENT TO INTERACT WITH AZURE STORAGE ACCOUNT
container_name = "pics"
blob_client = BlobServiceClient.from_connection_string(conn_str=AZURE_CONNECTION_STRING)

#This client is to access the specific container in which we want to store the images 
container_client = blob_client.get_container_client(container=container_name)
    
        



@app.route('/')
def index():
    #result = allData()
    return render_template('index.html')


@app.route('/search', methods=['POST','GET'] )
def searchUser():
    dbConnect()
    if request.method=="POST":
        dic={}
        for key,value in request.form.items():
            if value!='':
                dic[key]=value
        result = searchByField(dic)
        if result==[]:
            flash('No such entries in Table')


    else:
        result = allData()
    
    return render_template('index.html', data=result)

@app.route('/delete', methods=['POST','GET'])
def deleteUser():
    dic={}
    for key,value in request.form.items():
        if value!='':
            dic[key]=value
    print(dic)
    deleteByUser(dic)
    flash('------------------The Selected user has been successfully deleted----------------')

    return redirect('/')


@app.route('/updatecheck', methods=['POST','GET'])
def updateCheck():
    global oldName
    oldName= dict()
    for key,value in request.form.items():
        if value!='':
            oldName[key]=value
    #print(oldName)

    return render_template('update.html')


@app.route('/update',methods=['POST','GET'])
def updateUser():
    if request.method=="POST":

        global oldName
        dic={}
        for key,value in request.form.items():
            if value!='':
                dic[key]=value
        newDic = oldName | dic

        file = request.files.get('photos', '')
        if file:
            try:
                container_client.upload_blob(file.filename,file)
                flash("Photos uploaded successfully")
            except Exception as e:
                print(e)
                flash("The specified file/filename already exists")




    
        print(dic)
        #updateByUser(newDic)
        if dic:
            flash('------------------Updated Successfully, Go back to Main Page----------------')
            updateByUser(newDic)
        else:
            flash('------------------Please enter values in any field----------------')
        
        
    return render_template('update.html')

@app.route('/add',methods=['POST','GET'])
def addUser():
    if request.method=="GET":
         return render_template('add.html')

    if request.method=="POST":
        dic={}
        for key,value in request.form.items():
            if value!='':
                dic[key]=value
        
        if dic:
            flash('------------------User Added Successfully, Go back to Main Page----------------')
            addByUser(dic)
        else:
            flash('------------------Please enter values in any field----------------')
    
    return render_template('add.html')



@app.route('/uploadPhoto',methods=['POST'])
def uploadPhoto():
    #if single file--- request.files.get['photos']
    pictureFile = request.files.get('photos', '')
    print(pictureFile)
    for file in request.files.getlist("photos"):
        print(file)
        #the below line uploads the file to the given container
        try:
            container_client.upload_blob(file.filename,file)
            flash("Photos uploaded successfully")
        except Exception as e:
            print(e)
            flash("The specified file/filename already exists")


    return render_template('index.html')

@app.route('/showPhotos')
def showPhoto():
    #the below line will list all the blobs(images) in the container
    images = container_client.list_blobs()
    data ={}

    for image in images:
        #blob_url = container_client.get_blob_client(blob=image.name)
        # img_tag+="<img src='{}' width='auto' height='200'/>".format(blob_url.url) 
        data[image.name] = image.size        
    print(data)
    
    return render_template('index.html',pic=data) 

        


# @app.route('/marks',methods=['POST','GET'])
# def results():
#     dict = {'English' : 75, 'Computer' : 95 , "Maths" : 80}
#     return render_template('index.html', result = dict,name='')

# if request.method == 'POST':
#       result = request.form
#       return render_template("result.html",result = result)

# @app.route('/welcome',methods=['POST','GET'])
# def welcome():
#     if request.method=='POST':
#         user = request.form['fname']
#         #print(request.form)
#         dic={}
#         for key,value in request.form.items():
#             if value!='':
#                 dic[key]=value
#         #return redirect('/')
#         print(dic)
#         return render_template('index.html',name = user,result= dict())






if __name__ == "__main__":
    app.run()