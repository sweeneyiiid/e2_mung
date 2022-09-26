# REA Kasanjiku apark meters


# Staging up

bright gave access to thundercloud test platform

http://sparkapp-staging.spk.io:5010/login?next=%2F

rea had already set up test api user


followed documentation below to get user api key:

https://api.sparkmeter.io/

.eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ


http://sparkapp-staging.spk.io:5010/api/v0/



curl --location --request GET 'https://SITE.sparkmeter.cloud/api/v0/system-info' \
--header 'Content-Type: application/json' \
--header 'Authentication-Token: wrong_authentication_token'




curl --location --request GET 'http://sparkapp-staging.spk.io:5010/api/v0/system-info' \
--header 'Content-Type: application/json' \
--header 'Authentication-Token: .eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ'

### linux
curl --location --request GET 'http://sparkapp-staging.spk.io:5010/api/v0/system-info' --header 'Content-Type: application/json' --header 'Authentication-Token: .eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ'



### windows
curl --location --request GET "http://sparkapp-staging.spk.io:5010/api/v0/system-info" --header "Content-Type: application/json" --header "Authentication-Token: .eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ"


Ok, so basic access works, now try to get some more interesting stuff.

# Run through Sparkmeter GET requests

###List meter models


