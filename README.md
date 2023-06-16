# SENDGRID
## Create an environment variable
```
  1. echo "export SENDGRID_API_KEY='YOUR_API_KEY'" > sendgrid.env
  2. echo "sendgrid.env" >> .gitignore
  3. echo "sendgrid.env" >> .gitignore
```
## Install the package
```
pip3 install sendgrid
```


# API
## Login ##
 * URL
 ```
 /login
 ```
 * Method
 ```
 POST
 ```
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
 email, password
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "message": "Login success",
       "token": bearer token,
      }
      ```
## Register ##
* URL
 ```
 \register
 ```
 * Method
 ```
 POST
 ```
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
 username, email, password
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "email" : email,
       "username": username,
       "message": "Registration success",
      }
      ```
## Lupa Password ##
 * URL
 ```
 \forgot-pass
 ```
 * Method
 ```
 POST
 ```
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
 email
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "message": "Your password is sent successfully",
      }
      ```
## Upload ##
* URL
 ```
 \upload
 ```
 * Method
 ```
 POST
 ```
 * Headers
 ```
 'Authorization': Bearer Token
 ```
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
  file=[file], patient
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "result": result
      }
      ```
## History ##
* URL
 ```
 \history
 ```
 * Method
 ```
 GET
 ```
 * Headers
 ```
 'Authorization': Bearer Token
 ```
 * Content-Type
 ```
 -
 ```
 * Parameters
 ```
 -
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "patient_name": patientName,
       "result": result,
       "date": createdAt,
      }
      ```

## Get Username and Photo Profile  ##
* URL
 ```
 \profile
 ```
 * Method
 ```
 GET
 ```
 * Headers
 ```
 'Authorization': Bearer Token
 ```
 * Content-Type
 ```
 -
 ```
 * Parameters
 ```
 -
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "username": username,
       "img": base64 encode,
      }
      ```
 ## Edit Photo Profile  ##
* URL
 ```
 \profile
 ```
 * Method
 ```
 PUT
 ```
 * Headers
 ```
 'Authorization': Bearer Token
 ```
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
 file = [file].png
 ```
 * Response
    * Status Code:
      ```
       200
      ```
    * Response Body:
      ```
      {
       "message": "Your photo has been changed successfully,
       "encode": base64 encode,
      }
      ```
