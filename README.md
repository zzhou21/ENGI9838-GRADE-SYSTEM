# The reason why the project may not work on your local environment
Since our project is constructed with a local mysql database, if your local environment dont have a local database, it wont work.
I added a function to automatically build the database, but not sure if it gonna work. Also, you need to change the code in app.py, line 40, mysql+pymysql://root:Zzy19980220,to "your user name":"your pwd" 
![image](https://github.com/user-attachments/assets/dbde4932-8415-4e78-9b5b-553dc334d364)

# Some test results

## 1. Succesful run and connected to the port and db
![image](https://github.com/user-attachments/assets/53963e76-03ad-4bd0-9ca3-38f2e4e0f50b)
![image](https://github.com/user-attachments/assets/23e8e97b-4144-46a5-8aaa-586c1b7111eb)


## 2.  Succesful for registration, both for students and teacher
![image](https://github.com/user-attachments/assets/f0f0bfa2-40e7-4faf-b288-df763425536b)


![image](https://github.com/user-attachments/assets/b648978f-6da8-431e-8043-b62c9b2eaf47)

## 3. Succesful for creating courses
![image](https://github.com/user-attachments/assets/5e8cc575-f12b-4df0-8803-cc60e9909591)

![image](https://github.com/user-attachments/assets/26ef20e4-7b1b-4b92-8541-eb10372f2607)

## 4. Suceesful for submission
![image](https://github.com/user-attachments/assets/3d1075c9-a051-4c16-8164-701a51e7a61a)

The url for the assignments is stored in the uploads directory, can be achieved directly by clicking on it

![image](https://github.com/user-attachments/assets/b4556c8e-2aa7-4505-a43e-b4a174f3f811)

## 5. Succesful for creating assignments
![image](https://github.com/user-attachments/assets/b1b74992-c6df-42e9-8cfc-6cc64f91d0af)

![image](https://github.com/user-attachments/assets/184d9023-3f5d-4463-86f5-8f77fe3c1f00)

![image](https://github.com/user-attachments/assets/8a6e2d54-a9b0-43af-ac76-d5e224002d23)

# Not fully succesful for grading page, not showing the corresponding assignment

![image](https://github.com/user-attachments/assets/c061bbc4-28ad-4ee5-9436-e4184752ee4d)






