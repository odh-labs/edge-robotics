# What this directory does 
Deploys the model+UI provided by guiseAI to Openshift using a Dockerfile

# Directory contents
1. app : model+UI provided by guiseAI
2. manifest : manifest to be used by argocd 
3. Dockerfile : To deploy and expose the model on Openshift  
4. requirements.py : required python packages

# How to use
1. Login to Openshift
2. In Developer preview click +Add
3. Select Import from Git 
   1. Git Repo URL: https://github.com/odh-labs/edge-robotics/tree/main/Application
   2. Import Strategy: Dockerfile
      1. Dockerfile path: Application/Dockerfile
   3. Target port: 30000
   4. Create



