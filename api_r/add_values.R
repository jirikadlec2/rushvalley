#you must install the packages httr and RJSONIO before running this code in R
library(httr)
library(RJSONIO)

random_id = sample(1:1000,size=1)
random_name = paste("R test", random_id)

x <- list(
    user = "admin",
    password = "password",
    organization = random_name,
    description = paste("Uploaded from R:",random_name),
    link = paste("http://", random_id, sep=""),
    name = random_name,
    phone = "012-345-6789",
    email = "test@gmail.com",
    address = random_name,
    city = random_name,
    state = random_name,
    zipcode = "12345",
    citation = paste("Uploaded from R as a test:", random_name),
    metadata = 10
    )

POST("http://worldwater.byu.edu/mvc/index.php/default/services/api/sources",
         body = RJSONIO::toJSON(x),
         add_headers("Content-Type" = "application/json"),
         verbose()
    )
