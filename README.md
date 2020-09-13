## Gmail-Scrapper
This repo scraps gmail for user transactions, emails, alerts, etc financial emails.

The app is written in flask hosted at `https://simple-gmail-scrapper.herokuapp.com`

The flow is the first Oauth is used to get user gmail readonly permissions and then we fetch all mails from last one week 
at start (using query "after:timestamp"), it can be made to pick mails from even earlier date but just to keep things safe and simple for demo I have initialized the initial timestamp to that of 7 days before.

On successful run it will store the most recent timestamp in redis flask session so, next run it picks only latest mails

after reading mail I basically look for keywords(list stored in redis updateable by directly inserting into redis even if the app is running 
like "alerts", "bills", etc) in subject, if present I scan the body and fetch attachments or date and push them to a mongo database

Currently this is not async in nature, so takes times, ideally pub/sub or queue should be added to improve this part.

flask-session redis based storage is used for storing oauth tokens and user creds

the flow is 

`/authorize` to authorize, it will ask for permission to read gmail and then run a scrapping process since `INTIAL_TIMESTAMP`
`/revoke` to revoke access
`/clear` to clear session
`/doc/<id>` to view a mail doc content stored in mongo after scrapping
`/docs/<count>` to fetch last `count` (say 2) docs from mongo  


