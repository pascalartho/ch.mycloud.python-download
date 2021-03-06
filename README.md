# ch.mycloud.python-download
ch.mycloud.python-download - Download files from mycloud.ch using python

## Description
The current version allows to download files from mycloud.ch to a local directory. Identical files (identical file name and file size) are skipped.

>### What is Swisscom myCloud?
>*myCloud is Swisscom's new online storage system for photos, videos and other files. It provides an easy way for you to store their personal content, and to access and share it at any time and from any device. All the files are stored in Switzerland.*

For further information visit https://www.swisscom.ch/en/residential/help/loesung/mycloud-faq.html or https://www.mycloud.ch/

## Usage
Simply install python v2.7 including python module "requests" and define all parameters in ````config.ini````:
````
[default]
accessToken = YourAccessToken==
localFolder = /home/ubuntu/mycloud/
mycloudFolder = /Photos/
````

To get your access token, you have to login to www.mycloud.ch. On the home screen, you find your already uploaded pictures. Copy a link of one picture. This link can look like this: https://library.prod.mdl.swisscom.ch/thumbnail/Storage::Photos::Asset::Z2FIcXJZdzNEQlJCT3NCMzhnRDZCQT09?width=240&height=240&access_token=YourAccessToken==

The last parameter (````access_token````) is the one we have to extract. This token (````YourAccessToken==````) is valid until you delete the session in the settings of mycloud.ch.`

## Open tasks
- The login process is not done automatically. The access token has to be set manually
- Download is not parallelized

## References
- https://www.mycloud.ch/
- https://www.swisscom.ch/en/residential/help/loesung/mycloud-faq.html
- https://github.com/pascalartho/ch.mycloud.python-upload
- https://www.python.org/downloads/
- http://docs.python-requests.org/en/master/
