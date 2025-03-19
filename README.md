## The reason why the project may not work on your local environment
Since our project is constructed with a local mysql database, if your local environment dont have a local database, it wont work.
I added a function to automatically build the database, but not sure if it gonna work. Also, you need to change the code in app.py, line 40, mysql+pymysql://root:Zzy19980220,to "your user name":"your pwd" 
![image](https://github.com/user-attachments/assets/dbde4932-8415-4e78-9b5b-553dc334d364)

## Some test results

# 1. Succesfully run and connected to the port and db
![image](https://github.com/user-attachments/assets/53963e76-03ad-4bd0-9ca3-38f2e4e0f50b)

# 2.  Succesfully for registration, both for students and teacher
![image](https://github.com/user-attachments/assets/48145c73-17ae-450b-b365-95bb17fca35c)

![image](https://github.com/user-attachments/assets/b648978f-6da8-431e-8043-b62c9b2eaf47)

# 3. Succesfully for creating courses
![image](https://github.com/user-attachments/assets/5e8cc575-f12b-4df0-8803-cc60e9909591)

![image](https://github.com/user-attachments/assets/26ef20e4-7b1b-4b92-8541-eb10372f2607)

# Other functionalities will be tested



