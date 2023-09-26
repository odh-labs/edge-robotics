The high level steps to deploy codesys soft plc with Takebishi Device Gateway and Kepler are:
- Install SNO 4.13: Assisted installer recommended! https://docs.openshift.com/container-platform/4.13/installing/installing_sno/install-sno-installing-sno.html
- Install CodeSys softPLC
- Install Takebishi Devicegateway (dgw) via Yudai Ono San's guide: https://gitlab.com/yono1/devicegw-on-openshift/-/tree/itap-demo?ref_type=heads
- Configure CodeSys to connect to Takebshi dgw
- Install Kepler via OpenShift console Operator Hub
- Install Grafana dashboard on SNO.
