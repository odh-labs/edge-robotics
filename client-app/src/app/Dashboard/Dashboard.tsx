import React, { useState, useEffect } from 'react';
import useWebSocket from 'react-use-websocket';
import { Card, CardBody, CardTitle, Grid, GridItem, PageSection, Title } from '@patternfly/react-core';

const Dashboard: React.FunctionComponent = () => {
  const { lastMessage } = useWebSocket('ws://localhost:5005/events');
  const [messageHistory, setMessageHistory] = useState<MessageEvent[]>([]);

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage));
    }
  }, [lastMessage, setMessageHistory]);

  return (
    <PageSection>
      <Title headingLevel="h1" size="lg">
        Inference Output Video
      </Title>
      <Card id="card-demo-horizontal-split-example" isFlat>
        <Grid md={6}>
          <GridItem
            style={{
              minHeight: '200px',
              backgroundPosition: 'center',
              backgroundSize: 'cover',
              backgroundImage: 'url(http://localhost:5005/video)',
            }}
          />
          <GridItem>
            <CardTitle>Robot State Change Events</CardTitle>
            <CardBody>
              {messageHistory.map((message, idx) => (
                <span key={idx}>{message ? message.data : null}</span>
              ))}
            </CardBody>
          </GridItem>
        </Grid>
      </Card>
    </PageSection>
  );
};

export { Dashboard };
