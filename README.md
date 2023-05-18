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
 application/json
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
   "status": "success",
   "message": "success login",
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
 application/json
 ```
 * Parameters
 ```
 username, email, password
 ```
 * Response
 ```
 ```
## Lupa Password ##
 * URL
 ```
 \forgot-pass
 ```
 * Method
 ```
 GET
 ```
 * Content-Type
 ```
 ```
 * Parameters
 ```
 email
 ```
 * Response
 ```
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
 * Content-Type
 ```
 multipart/form-data
 ```
 * Parameters
 ```
 email
 ```
 * Response
 ```
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
 * Content-Type
 ```
 ```
 * Parameters
 ```
 email
 ```
 * Response
 ```
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
 * Content-Type
 ```
 ```
 * Parameters
 ```
 email
 ```
 * Response
 ```
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
 * Content-Type
 ```
 ```
 * Parameters
 ```
 email
 ```
 * Response
 ```
 ```
