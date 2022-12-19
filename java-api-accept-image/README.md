# Java API Accept Image
This provides a Spring Boot based API that accepts an image and saves that image to disk.


## Run - locally
- Clone this repo
- Change directory to edge-robotics - call that  directory *REPO_HOME*
- Change directory to *REPO_HOME/java-api-accept-image*
- Run **mvn spring-boot:run**
- Hit a POST API call to the http://localhost:8080/upload/image
- Upload your image to your API client - it gets saved to disk
- for a visual demo see *REPO_HOME/upload-image-api-call.mov*


## Use Podman to push to a repo - then download to OpenShift or elsewhere

Sample packaging instructions. Using podman - alternatively use Docker. Enter your credentials for your desired registry.
```
mvn package
podman login

podman build -f Dockerfile -t quay.io/tcorcoran/java-api-accept-image:latest .
podman tag quay.io/tcorcoran/java-api-accept-image:latest quay.io/tcorcoran/java-api-accept-image:latest
podman push quay.io/tcorcoran/java-api-accept-image:latest
```
