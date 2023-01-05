#pragma once

#include "CStreamer.h"
#include "OVCam.h"

class OVCamStreamer : public CStreamer
{
    bool m_showBig;
    OVCam &m_cam;

public:
    OVCamStreamer(SOCKET aClient, OVCam &cam);

    virtual void    streamImage(uint32_t curMsec);
};
