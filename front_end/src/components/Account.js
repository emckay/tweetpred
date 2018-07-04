import React from 'react'
import MarketProbabilitiesChart from './MarketProbabilitiesChart'
import './Account.css'
import timeAgo from 'timeago.js'
import {Row, Col, FormGroup, Input, Label, Badge} from 'reactstrap'
import xhr from '../xhr'

const hourDif = (start, end) => {
  return (end.getTime() - start.getTime()) / 60 / 60 / 1000
}
const timeUntil = (until) => {
  const hours = Math.round(hourDif(new Date(), until))
  if (hours < 24) {
    return `${hours}h`
  }
  return `${Math.floor(hours / 24)}d ${hours % 24}h`
}

const pace = (soFar, periodStart, periodEnd) => {
  const totalHours = hourDif(periodStart, periodEnd)
  const hoursSoFar = hourDif(periodStart, new Date())
  return (soFar / hoursSoFar * totalHours).toFixed(1)
}

const paramLabels = ['mu', 'alpha', 'beta', 'c_0', 'c_1', 'c_2']
class Account extends React.Component {
  render() {
    const {data, refresh} = this.props
    return (
      <div className="account">
        <div className="top-row">
          <Badge color="dark" href={`https://twitter.com/${data.account.screen_name}`}>
            {data.account.screen_name}
          </Badge>
        </div>
        <div className="top-row">
          <Badge color="light">
            Ends in {timeUntil(new Date(data.period_end))}
          </Badge>
          <Badge color="light">
            So far: {data.so_far}
          </Badge>
          <Badge color="light">
            Pace: {pace(data.so_far, new Date(data.period_start), new Date(data.period_end))}
          </Badge>
          <Badge color="light" onClick={refresh} tabIndex={1} href="">
            {timeAgo().format(new Date(data.as_of))}
          </Badge>
        </div>
        <div className="plot">
          <MarketProbabilitiesChart bins={data.bins} n={data.n} />
        </div>
        <Row>
          <Col xs="4" className="options">
            <FormGroup>
              <Label for="exampleSelect" className="sr-only">
                Model class
              </Label>
              <Input
                type="select"
                name="select"
                id="exampleSelect"
                style={{maxWidth: '200px'}}
                bsSize="sm"
              >
                <option>hawkes</option>
                <option disabled>others coming soon...</option>
              </Input>
            </FormGroup>
            <a href={data.account.market_url} className="small">
              Market
            </a>
          </Col>
          <Col xs="8" className="params">
            <div className="param-col">
              <div className="param-row">
                <Badge className="param-label" color="light">n</Badge>
                <Badge className="param-label" color="light">
                  {data.n}
                </Badge>
              </div>
              {data.params.slice(0, 3).map((p, i) => (
                <div className="param-row" key={i}>
                  <Badge className="param-label" color="light">
                    {paramLabels[i]}
                  </Badge>
                  <Badge className="param-label" color="light">
                    {p.toFixed(3)}
                  </Badge>
                </div>
              ))}
            </div>
            <div className="param-col">
              {data.params.slice(3).map((p, i) => (
                <div className="param-row" key={i}>
                  <Badge className="param-label" color="light">
                    {paramLabels[i + 3]}
                  </Badge>
                  <Badge className="param-label" color="light">
                    {p.toFixed(3)}
                  </Badge>
                </div>
              ))}
            </div>
          </Col>
        </Row>
      </div>
    )
  }
}

class AccountDataProvider extends React.Component {
  state = {
    loading: true,
    data: null,
  }

  componentDidMount() {
    this.fetchAndUpdate()
  }

  fetchAndUpdate = async () => {
    const {id} = this.props
    this.setState({loading: true})
    try {
      const res = await xhr.get(`/accounts/${id}/latest_histogram/`)
      this.setState({loading: false, data: res.data})
    } catch (err) {
      console.error(err)
    }
  }

  render() {
    const {loading, data} = this.state
    if (loading) {
      return <div className="account">Loading...</div>
    }
    return <Account data={data} refresh={this.fetchAndUpdate} />
  }
}

export default AccountDataProvider
