#you must install the packages httr and RJSONIO.
library(httr)
library(RJSONIO)

random_id = sample(1:1000,size=1)
random_name = paste("R test", random_id)
set.seed(2)
random_lat = runif(1, 35.0, 49.0) #random latitude inside U.S
random_lon = runif(1, -110.0, -70.0) #random longitude inside U.S

x <- list(
    user = "admin",
    password = "password",
    SourceID = 35,
    SiteCode = paste("R",random_id, sep="-"),
    SiteName = paste("R test site", random_id),
    Latitude = random_lat,
    Longitude = random_lon,
    SiteType = "Atmosphere",
    Elevation_m = 2000,
    State = "Utah",
    County = "Utah",
    Comments = "test site uploaded from R"
    )

POST("http://worldwater.byu.edu/app/index.php/default/services/api/sites",
         body = RJSONIO::toJSON(x),
         add_headers("Content-Type" = "application/json"),
         verbose()
    )
