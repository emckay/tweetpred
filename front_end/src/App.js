import React, { Component } from 'react';
import {Col, Row, Container} from 'reactstrap'
import Account from './components/Account'
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <Container>
          <Row>
            <Col lg="6" md="12">
              <Account id={1} />
            </Col>
            <Col lg="6" md="12">
              <Account id={2} />
            </Col>
            <Col lg="6" md="12">
              <Account id={3} />
            </Col>
            <Col lg="6" md="12">
              <Account id={4} />
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}

export default App;
